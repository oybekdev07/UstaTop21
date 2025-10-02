from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from backend.database import get_db
from backend.models import Review, Order, Master, User, UserRole, OrderStatus
from backend.schemas import Review as ReviewSchema, ReviewCreate
from backend.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=ReviewSchema)
async def create_review(
    review_data: ReviewCreate,
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a review for a completed order
    """
    # Verify order exists and is completed
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if user is the client of this order
    if order.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review your own orders"
        )
    
    # Check if order is completed
    if order.status != OrderStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only review completed orders"
        )
    
    # Check if review already exists
    existing_review = db.query(Review).filter(Review.order_id == order_id).first()
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review already exists for this order"
        )
    
    # Create review
    db_review = Review(
        client_id=current_user.id,
        master_id=order.master_id,
        order_id=order_id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    # Update master rating
    await update_master_rating(order.master_id, db)
    
    # Load complete review with relationships
    review = db.query(Review).options(
        joinedload(Review.client),
        joinedload(Review.master).joinedload(Master.user)
    ).filter(Review.id == db_review.id).first()
    
    return review

@router.get("/", response_model=List[ReviewSchema])
async def get_reviews(
    skip: int = 0,
    limit: int = 100,
    master_id: Optional[int] = Query(None),
    client_id: Optional[int] = Query(None),
    min_rating: Optional[int] = Query(None, ge=1, le=5),
    db: Session = Depends(get_db)
):
    """
    Get reviews with filtering options
    """
    query = db.query(Review).options(
        joinedload(Review.client),
        joinedload(Review.master).joinedload(Master.user)
    )
    
    # Apply filters
    if master_id:
        query = query.filter(Review.master_id == master_id)
    
    if client_id:
        query = query.filter(Review.client_id == client_id)
    
    if min_rating:
        query = query.filter(Review.rating >= min_rating)
    
    reviews = query.order_by(Review.created_at.desc()).offset(skip).limit(limit).all()
    return reviews

@router.get("/{review_id}", response_model=ReviewSchema)
async def get_review(review_id: int, db: Session = Depends(get_db)):
    """
    Get specific review details
    """
    review = db.query(Review).options(
        joinedload(Review.client),
        joinedload(Review.master).joinedload(Master.user)
    ).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return review

@router.put("/{review_id}", response_model=ReviewSchema)
async def update_review(
    review_id: int,
    review_update: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a review (only by the client who created it)
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check permissions
    if review.client_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reviews"
        )
    
    # Update review
    review.rating = review_update.rating
    review.comment = review_update.comment
    
    db.commit()
    db.refresh(review)
    
    # Update master rating
    await update_master_rating(review.master_id, db)
    
    # Load complete review with relationships
    review = db.query(Review).options(
        joinedload(Review.client),
        joinedload(Review.master).joinedload(Master.user)
    ).filter(Review.id == review_id).first()
    
    return review

@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a review (only by the client who created it or admin)
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check permissions
    if review.client_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews"
        )
    
    master_id = review.master_id
    db.delete(review)
    db.commit()
    
    # Update master rating
    await update_master_rating(master_id, db)
    
    return {"message": "Review deleted successfully"}

@router.get("/master/{master_id}/stats")
async def get_master_review_stats(master_id: int, db: Session = Depends(get_db)):
    """
    Get review statistics for a master
    """
    master = db.query(Master).filter(Master.id == master_id).first()
    if not master:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master not found"
        )
    
    # Get review statistics
    reviews = db.query(Review).filter(Review.master_id == master_id).all()
    
    if not reviews:
        return {
            "master_id": master_id,
            "total_reviews": 0,
            "average_rating": 0.0,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }
    
    total_reviews = len(reviews)
    average_rating = sum(review.rating for review in reviews) / total_reviews
    
    rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        rating_distribution[review.rating] += 1
    
    return {
        "master_id": master_id,
        "total_reviews": total_reviews,
        "average_rating": round(average_rating, 2),
        "rating_distribution": rating_distribution
    }

async def update_master_rating(master_id: int, db: Session):
    """
    Update master's average rating and total reviews count
    """
    # Calculate new average rating
    result = db.query(
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('total_reviews')
    ).filter(Review.master_id == master_id).first()
    
    master = db.query(Master).filter(Master.id == master_id).first()
    if master:
        master.rating = round(result.avg_rating or 0.0, 2)
        master.total_reviews = result.total_reviews or 0
        db.commit()
