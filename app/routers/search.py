from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from backend.database import get_db
from backend.models import Master, User, Category, Service
from backend.schemas import Master as MasterSchema, Service as ServiceSchema

router = APIRouter()

@router.get("/masters", response_model=List[MasterSchema])
async def search_masters(
    q: Optional[str] = Query(None, description="Search query"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    max_rating: Optional[float] = Query(None, ge=0, le=5, description="Maximum rating"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum base price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum base price"),
    min_experience: Optional[int] = Query(None, ge=0, description="Minimum years of experience"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    is_available: Optional[bool] = Query(None, description="Filter by availability"),
    sort_by: Optional[str] = Query("rating", description="Sort by: rating, price, experience, reviews"),
    sort_order: Optional[str] = Query("desc", description="Sort order: asc, desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Advanced search for masters with multiple filters and sorting options
    """
    query = db.query(Master).options(
        joinedload(Master.user),
        joinedload(Master.category)
    ).filter(
        Master.user.has(is_active=True),
        Master.is_available == True if is_available is None else Master.is_available == is_available
    )
    
    # Text search
    if q:
        search_terms = q.split()
        search_conditions = []
        
        for term in search_terms:
            term_conditions = or_(
                Master.specialization.ilike(f"%{term}%"),
                Master.description.ilike(f"%{term}%"),
                Master.user.has(User.first_name.ilike(f"%{term}%")),
                Master.user.has(User.last_name.ilike(f"%{term}%")),
                Master.category.has(Category.name_uz.ilike(f"%{term}%")),
                Master.category.has(Category.name_ru.ilike(f"%{term}%")),
                Master.category.has(Category.name_en.ilike(f"%{term}%"))
            )
            search_conditions.append(term_conditions)
        
        if search_conditions:
            query = query.filter(and_(*search_conditions))
    
    # Category filter
    if category_id:
        query = query.filter(Master.category_id == category_id)
    
    # Rating filters
    if min_rating is not None:
        query = query.filter(Master.rating >= min_rating)
    if max_rating is not None:
        query = query.filter(Master.rating <= max_rating)
    
    # Price filters
    if min_price is not None:
        query = query.filter(Master.base_price >= min_price)
    if max_price is not None:
        query = query.filter(Master.base_price <= max_price)
    
    # Experience filter
    if min_experience is not None:
        query = query.filter(Master.experience_years >= min_experience)
    
    # Verification filter
    if is_verified is not None:
        query = query.filter(Master.is_verified == is_verified)
    
    # Sorting
    if sort_by == "rating":
        order_column = Master.rating
    elif sort_by == "price":
        order_column = Master.base_price
    elif sort_by == "experience":
        order_column = Master.experience_years
    elif sort_by == "reviews":
        order_column = Master.total_reviews
    else:
        order_column = Master.rating
    
    if sort_order == "desc":
        query = query.order_by(desc(order_column))
    else:
        query = query.order_by(order_column)
    
    masters = query.offset(skip).limit(limit).all()
    return masters

@router.get("/services", response_model=List[ServiceSchema])
async def search_services(
    q: Optional[str] = Query(None, description="Search query"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    master_id: Optional[int] = Query(None, description="Filter by master"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    min_duration: Optional[int] = Query(None, ge=1, description="Minimum duration in hours"),
    max_duration: Optional[int] = Query(None, ge=1, description="Maximum duration in hours"),
    sort_by: Optional[str] = Query("price", description="Sort by: price, duration, name"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc, desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Advanced search for services with multiple filters and sorting options
    """
    query = db.query(Service).filter(Service.is_active == True)
    
    # Text search
    if q:
        search_terms = q.split()
        search_conditions = []
        
        for term in search_terms:
            term_conditions = or_(
                Service.name.ilike(f"%{term}%"),
                Service.description.ilike(f"%{term}%")
            )
            search_conditions.append(term_conditions)
        
        if search_conditions:
            query = query.filter(and_(*search_conditions))
    
    # Filters
    if category_id:
        query = query.filter(Service.category_id == category_id)
    
    if master_id:
        query = query.filter(Service.master_id == master_id)
    
    if min_price is not None:
        query = query.filter(Service.price >= min_price)
    if max_price is not None:
        query = query.filter(Service.price <= max_price)
    
    if min_duration is not None:
        query = query.filter(Service.duration_hours >= min_duration)
    if max_duration is not None:
        query = query.filter(Service.duration_hours <= max_duration)
    
    # Sorting
    if sort_by == "price":
        order_column = Service.price
    elif sort_by == "duration":
        order_column = Service.duration_hours
    elif sort_by == "name":
        order_column = Service.name
    else:
        order_column = Service.price
    
    if sort_order == "desc":
        query = query.order_by(desc(order_column))
    else:
        query = query.order_by(order_column)
    
    services = query.offset(skip).limit(limit).all()
    return services

@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=2, description="Search query for suggestions"),
    type: str = Query("all", description="Suggestion type: masters, services, categories, all"),
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db)
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get search suggestions based on query
    """
    suggestions = {
        "masters": [],
        "services": [],
        "categories": []
    }
    
    if type in ["masters", "all"]:
        # Master suggestions
        masters = db.query(Master).options(
            joinedload(Master.user)
        ).filter(
            Master.user.has(is_active=True),
            or_(
                Master.specialization.ilike(f"%{q}%"),
                Master.user.has(User.first_name.ilike(f"%{q}%")),
                Master.user.has(User.last_name.ilike(f"%{q}%"))
            )
        ).limit(limit).all()
        
        suggestions["masters"] = [
            {
                "id": master.id,
                "name": f"{master.user.first_name} {master.user.last_name}",
                "specialization": master.specialization,
                "rating": master.rating,
                "type": "master"
            }
            for master in masters
        ]
    
    if type in ["services", "all"]:
        # Service suggestions
        services = db.query(Service).filter(
            Service.is_active == True,
            or_(
                Service.name.ilike(f"%{q}%"),
                Service.description.ilike(f"%{q}%")
            )
        ).limit(limit).all()
        
        suggestions["services"] = [
            {
                "id": service.id,
                "name": service.name,
                "price": service.price,
                "type": "service"
            }
            for service in services
        ]
    
    if type in ["categories", "all"]:
        # Category suggestions
        categories = db.query(Category).filter(
            Category.is_active == True,
            or_(
                Category.name_uz.ilike(f"%{q}%"),
                Category.name_ru.ilike(f"%{q}%"),
                Category.name_en.ilike(f"%{q}%")
            )
        ).limit(limit).all()
        
        suggestions["categories"] = [
            {
                "id": category.id,
                "name_uz": category.name_uz,
                "name_ru": category.name_ru,
                "name_en": category.name_en,
                "type": "category"
            }
            for category in categories
        ]
    
    return suggestions

@router.get("/popular")
async def get_popular_items(
    type: str = Query("masters", description="Type: masters, services, categories"),
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get popular items based on ratings, orders, etc.
    """
    if type == "masters":
        masters = db.query(Master).options(
            joinedload(Master.user),
            joinedload(Master.category)
        ).filter(
            Master.user.has(is_active=True),
            Master.is_available == True
        ).order_by(
            desc(Master.rating),
            desc(Master.total_orders)
        ).limit(limit).all()
        
        return [
            {
                "id": master.id,
                "name": f"{master.user.first_name} {master.user.last_name}",
                "specialization": master.specialization,
                "rating": master.rating,
                "total_orders": master.total_orders,
                "category": master.category.name_uz,
                "type": "master"
            }
            for master in masters
        ]
    
    elif type == "services":
        # Get services from top-rated masters
        services = db.query(Service).join(Master).filter(
            Service.is_active == True,
            Master.rating >= 4.0
        ).order_by(
            desc(Master.rating),
            Service.price
        ).limit(limit).all()
        
        return [
            {
                "id": service.id,
                "name": service.name,
                "price": service.price,
                "duration_hours": service.duration_hours,
                "type": "service"
            }
            for service in services
        ]
    
    elif type == "categories":
        # Get categories with most masters
        categories = db.query(
            Category,
            func.count(Master.id).label('master_count')
        ).join(Master).filter(
            Category.is_active == True
        ).group_by(Category.id).order_by(
            desc('master_count')
        ).limit(limit).all()
        
        return [
            {
                "id": category.Category.id,
                "name_uz": category.Category.name_uz,
                "name_ru": category.Category.name_ru,
                "name_en": category.Category.name_en,
                "master_count": category.master_count,
                "type": "category"
            }
            for category in categories
        ]
    
    return []
