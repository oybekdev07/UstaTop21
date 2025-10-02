from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from backend.database import get_db
from backend.models import Master, User, UserRole, Category, Portfolio
from backend.schemas import (
    Master as MasterSchema, 
    MasterCreate, 
    MasterUpdate,
    Portfolio as PortfolioSchema,
    PortfolioCreate
)
from backend.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[MasterSchema])
async def get_masters(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = Query(None),
    min_rating: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    search: Optional[str] = Query(None),
    is_available: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Master).options(
        joinedload(Master.user),
        joinedload(Master.category)
    ).filter(Master.user.has(is_active=True))
    
    # Apply filters
    if category_id:
        query = query.filter(Master.category_id == category_id)
    
    if min_rating:
        query = query.filter(Master.rating >= min_rating)
    
    if max_price:
        query = query.filter(Master.base_price <= max_price)
    
    if is_available is not None:
        query = query.filter(Master.is_available == is_available)
    
    if search:
        search_filter = or_(
            Master.specialization.contains(search),
            Master.description.contains(search),
            Master.user.has(User.first_name.contains(search)),
            Master.user.has(User.last_name.contains(search))
        )
        query = query.filter(search_filter)
    
    masters = query.offset(skip).limit(limit).all()
    return masters

@router.get("/{master_id}", response_model=MasterSchema)
async def get_master(master_id: int, db: Session = Depends(get_db)):
    master = db.query(Master).options(
        joinedload(Master.user),
        joinedload(Master.category)
    ).filter(Master.id == master_id).first()
    
    if not master:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master not found"
        )
    
    return master

@router.post("/", response_model=MasterSchema)
async def create_master_profile(
    master_data: MasterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if user already has a master profile
    existing_master = db.query(Master).filter(Master.user_id == current_user.id).first()
    if existing_master:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a master profile"
        )
    
    # Verify category exists
    category = db.query(Category).filter(Category.id == master_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Create master profile
    db_master = Master(
        user_id=current_user.id,
        **master_data.dict()
    )
    
    db.add(db_master)
    
    # Update user role to master
    current_user.role = UserRole.MASTER
    
    db.commit()
    db.refresh(db_master)
    
    # Load relationships
    master = db.query(Master).options(
        joinedload(Master.user),
        joinedload(Master.category)
    ).filter(Master.id == db_master.id).first()
    
    return master

@router.put("/{master_id}", response_model=MasterSchema)
async def update_master_profile(
    master_id: int,
    master_update: MasterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    master = db.query(Master).filter(Master.id == master_id).first()
    if not master:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master not found"
        )
    
    # Check permissions
    if current_user.id != master.user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update master profile
    update_data = master_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(master, field, value)
    
    db.commit()
    db.refresh(master)
    
    # Load relationships
    master = db.query(Master).options(
        joinedload(Master.user),
        joinedload(Master.category)
    ).filter(Master.id == master_id).first()
    
    return master

@router.post("/{master_id}/portfolio", response_model=PortfolioSchema)
async def add_portfolio_item(
    master_id: int,
    portfolio_data: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    master = db.query(Master).filter(Master.id == master_id).first()
    if not master:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master not found"
        )
    
    # Check permissions
    if current_user.id != master.user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_portfolio = Portfolio(
        master_id=master_id,
        **portfolio_data.dict()
    )
    
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    
    return db_portfolio

@router.get("/{master_id}/portfolio", response_model=List[PortfolioSchema])
async def get_master_portfolio(master_id: int, db: Session = Depends(get_db)):
    master = db.query(Master).filter(Master.id == master_id).first()
    if not master:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master not found"
        )
    
    portfolio = db.query(Portfolio).filter(Portfolio.master_id == master_id).all()
    return portfolio

@router.delete("/{master_id}/portfolio/{portfolio_id}")
async def delete_portfolio_item(
    master_id: int,
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    master = db.query(Master).filter(Master.id == master_id).first()
    if not master:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master not found"
        )
    
    # Check permissions
    if current_user.id != master.user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    portfolio_item = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.master_id == master_id
    ).first()
    
    if not portfolio_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio item not found"
        )
    
    db.delete(portfolio_item)
    db.commit()
    
    return {"message": "Portfolio item deleted successfully"}

@router.post("/{master_id}/verify")
async def verify_master(
    master_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only admin can verify masters
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    master = db.query(Master).filter(Master.id == master_id).first()
    if not master:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master not found"
        )
    
    master.is_verified = True
    db.commit()
    
    return {"message": "Master verified successfully"}
