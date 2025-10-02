from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from backend.database import get_db
from backend.models import Order, OrderItem, Service, Master, User, UserRole, OrderStatus
from backend.schemas import (
    Order as OrderSchema, 
    OrderCreate, 
    OrderItem as OrderItemSchema
)
from backend.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=OrderSchema)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new order with multiple services
    """
    # Verify master exists
    master = db.query(Master).filter(Master.id == order_data.master_id).first()
    if not master:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master not found"
        )
    
    if not master.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Master is not available"
        )
    
    # Calculate total amount
    total_amount = 0
    order_items_data = []
    
    for item in order_data.order_items:
        service = db.query(Service).filter(
            Service.id == item.service_id,
            Service.master_id == order_data.master_id,
            Service.is_active == True
        ).first()
        
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service with id {item.service_id} not found or not available"
            )
        
        item_total = service.price * item.quantity
        total_amount += item_total
        
        order_items_data.append({
            "service_id": service.id,
            "quantity": item.quantity,
            "price": service.price
        })
    
    # Create order
    db_order = Order(
        client_id=current_user.id,
        master_id=order_data.master_id,
        total_amount=total_amount,
        description=order_data.description,
        address=order_data.address,
        scheduled_date=order_data.scheduled_date,
        status=OrderStatus.PENDING
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Create order items
    for item_data in order_items_data:
        db_order_item = OrderItem(
            order_id=db_order.id,
            **item_data
        )
        db.add(db_order_item)
    
    db.commit()
    
    # Load complete order with relationships
    order = db.query(Order).options(
        joinedload(Order.client),
        joinedload(Order.master).joinedload(Master.user),
        joinedload(Order.order_items).joinedload(OrderItem.service)
    ).filter(Order.id == db_order.id).first()
    
    return order

@router.get("/", response_model=List[OrderSchema])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = Query(None),
    master_id: Optional[int] = Query(None),
    client_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get orders with filtering options
    """
    query = db.query(Order).options(
        joinedload(Order.client),
        joinedload(Order.master).joinedload(Master.user),
        joinedload(Order.order_items).joinedload(OrderItem.service)
    )
    
    # Apply role-based filtering
    if current_user.role == UserRole.CLIENT:
        query = query.filter(Order.client_id == current_user.id)
    elif current_user.role == UserRole.MASTER:
        master = db.query(Master).filter(Master.user_id == current_user.id).first()
        if master:
            query = query.filter(Order.master_id == master.id)
        else:
            return []
    # Admin can see all orders
    
    # Apply additional filters
    if status:
        query = query.filter(Order.status == status)
    
    if master_id and current_user.role == UserRole.ADMIN:
        query = query.filter(Order.master_id == master_id)
    
    if client_id and current_user.role == UserRole.ADMIN:
        query = query.filter(Order.client_id == client_id)
    
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific order details
    """
    order = db.query(Order).options(
        joinedload(Order.client),
        joinedload(Order.master).joinedload(Master.user),
        joinedload(Order.order_items).joinedload(OrderItem.service)
    ).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.CLIENT and order.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    elif current_user.role == UserRole.MASTER:
        master = db.query(Master).filter(Master.user_id == current_user.id).first()
        if not master or order.master_id != master.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    return order

@router.put("/{order_id}/status", response_model=OrderSchema)
async def update_order_status(
    order_id: int,
    new_status: OrderStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update order status (masters and admins only)
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check permissions
    can_update = False
    if current_user.role == UserRole.ADMIN:
        can_update = True
    elif current_user.role == UserRole.MASTER:
        master = db.query(Master).filter(Master.user_id == current_user.id).first()
        if master and order.master_id == master.id:
            can_update = True
    elif current_user.role == UserRole.CLIENT and order.client_id == current_user.id:
        # Clients can only cancel pending orders
        if order.status == OrderStatus.PENDING and new_status == OrderStatus.CANCELLED:
            can_update = True
    
    if not can_update:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Validate status transitions
    valid_transitions = {
        OrderStatus.PENDING: [OrderStatus.ACCEPTED, OrderStatus.CANCELLED],
        OrderStatus.ACCEPTED: [OrderStatus.IN_PROGRESS, OrderStatus.CANCELLED],
        OrderStatus.IN_PROGRESS: [OrderStatus.COMPLETED, OrderStatus.CANCELLED],
        OrderStatus.COMPLETED: [],  # Final state
        OrderStatus.CANCELLED: []   # Final state
    }
    
    if new_status not in valid_transitions.get(order.status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot change status from {order.status.value} to {new_status.value}"
        )
    
    # Update status
    order.status = new_status
    
    # Set completion date if completed
    if new_status == OrderStatus.COMPLETED:
        order.completed_date = datetime.utcnow()
        
        # Update master statistics
        master = db.query(Master).filter(Master.id == order.master_id).first()
        if master:
            master.total_orders += 1
    
    db.commit()
    
    # Load complete order with relationships
    order = db.query(Order).options(
        joinedload(Order.client),
        joinedload(Order.master).joinedload(Master.user),
        joinedload(Order.order_items).joinedload(OrderItem.service)
    ).filter(Order.id == order_id).first()
    
    return order

@router.delete("/{order_id}")
async def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel an order (only pending orders can be cancelled)
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check permissions
    can_cancel = False
    if current_user.role == UserRole.ADMIN:
        can_cancel = True
    elif current_user.role == UserRole.CLIENT and order.client_id == current_user.id:
        can_cancel = True
    elif current_user.role == UserRole.MASTER:
        master = db.query(Master).filter(Master.user_id == current_user.id).first()
        if master and order.master_id == master.id:
            can_cancel = True
    
    if not can_cancel:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if order.status not in [OrderStatus.PENDING, OrderStatus.ACCEPTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending or accepted orders can be cancelled"
        )
    
    order.status = OrderStatus.CANCELLED
    db.commit()
    
    return {"message": "Order cancelled successfully"}

@router.get("/master/{master_id}/stats")
async def get_master_order_stats(
    master_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get order statistics for a master
    """
    master = db.query(Master).filter(Master.id == master_id).first()
    if not master:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master not found"
        )
    
    # Check permissions
    if (current_user.role == UserRole.MASTER and 
        master.user_id != current_user.id and 
        current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get order statistics
    total_orders = db.query(Order).filter(Order.master_id == master_id).count()
    completed_orders = db.query(Order).filter(
        Order.master_id == master_id,
        Order.status == OrderStatus.COMPLETED
    ).count()
    pending_orders = db.query(Order).filter(
        Order.master_id == master_id,
        Order.status == OrderStatus.PENDING
    ).count()
    in_progress_orders = db.query(Order).filter(
        Order.master_id == master_id,
        Order.status == OrderStatus.IN_PROGRESS
    ).count()
    
    return {
        "master_id": master_id,
        "total_orders": total_orders,
        "completed_orders": completed_orders,
        "pending_orders": pending_orders,
        "in_progress_orders": in_progress_orders,
        "completion_rate": completed_orders / total_orders if total_orders > 0 else 0
    }
