from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from backend.database import get_db
from backend.models import User, UserRole, PyObjectId
from backend.schemas import User as UserSchema, UserCreate
from backend.auth import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[UserSchema])
async def get_users(
    skip: int = 0, 
    limit: int = 100, 
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only admin can view all users
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    cursor = db.users.find().skip(skip).limit(limit)
    users = await cursor.to_list(length=limit)
    return users

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: str, 
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Users can only view their own profile, admins can view any
    if str(current_user.id) != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: str,
    user_update: UserCreate,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Users can only update their own profile, admins can update any
    if str(current_user.id) != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.users.update_one(
            {"_id": ObjectId(user_id)}, 
            {"$set": update_data}
        )
    
    # Return updated user
    updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
    return updated_user

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only admin can delete users
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Soft delete - just deactivate the user
    await db.users.update_one(
        {"_id": ObjectId(user_id)}, 
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "User deactivated successfully"}

@router.post("/{user_id}/activate")
async def activate_user(
    user_id: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only admin can activate users
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await db.users.update_one(
        {"_id": ObjectId(user_id)}, 
        {"$set": {"is_active": True, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "User activated successfully"}

@router.post("/{user_id}/verify")
async def verify_user(
    user_id: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only admin can verify users
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await db.users.update_one(
        {"_id": ObjectId(user_id)}, 
        {"$set": {"is_verified": True, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "User verified successfully"}
