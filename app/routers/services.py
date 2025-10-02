from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from backend.database import get_db
from backend.models import Service, Master, User, UserRole, Category
from backend.schemas import Service as ServiceSchema, ServiceCreate
from backend.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[ServiceSchema])
async def get_services(
    skip: int = 0,
    limit: int = 100,
    master_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Service).filter(Service.is_active == True)
    
    # Apply filters
    if master_id:
        query = query.filter(Service.master_id == master_id)
    
    if category_id:
        query = query.filter(Service.category_id == category_id)
    
    if min_price:
        query = query.filter(Service.price >= min_price)
    
    if max_price:
        query = query.filter(Service.price <= max_price)
    
    if search:
        query = query.filter(
            Service.name.contains(search) | 
            Service.description.contains(search)
        )
    
    services = query.offset(skip).limit(limit).all()
    return services

@router.get("/{service_id}", response_model=ServiceSchema)
async def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.is_active == True
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return service

@router.post("/", response_model=ServiceSchema)
async def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if user has a master profile
    master = db.query(Master).filter(Master.user_id == current_user.id).first()
    if not master:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a master profile to create services"
        )
    
    # Verify category exists
    category = db.query(Category).filter(Category.id == service_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    db_service = Service(
        master_id=master.id,
        **service_data.dict()
    )
    
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    
    return db_service

@router.put("/{service_id}", response_model=ServiceSchema)
async def update_service(
    service_id: int,
    service_update: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Check permissions
    master = db.query(Master).filter(Master.id == service.master_id).first()
    if current_user.id != master.user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    update_data = service_update.dict()
    for field, value in update_data.items():
        setattr(service, field, value)
    
    db.commit()
    db.refresh(service)
    
    return service

@router.delete("/{service_id}")
async def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Check permissions
    master = db.query(Master).filter(Master.id == service.master_id).first()
    if current_user.id != master.user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Soft delete
    service.is_active = False
    db.commit()
    
    return {"message": "Service deleted successfully"}
