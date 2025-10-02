from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from backend.models import UserRole, OrderStatus

# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum
from backend.models import User


from pydantic import BaseModel
from typing import Optional, List, ForwardRef

# Oldin User ni string qilib ishlatamiz
class MasterBase(BaseModel):
    id: int
    name: str

class Master(MasterBase):
    user: "User"   # 🔹 string sifatida yoziladi (forward reference)

class Order(BaseModel):
    id: int
    client: "User"   # 🔹 string sifatida yoziladi


class UserRole(str, Enum):
    CLIENT = "client"
    MASTER = "master"
    ADMIN = "admin"

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole = UserRole.CLIENT

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
    
class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True



# Category Schemas
class CategoryBase(BaseModel):
    name_uz: str
    name_ru: str
    name_en: str
    description: Optional[str] = None
    icon_url: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Master Schemas
class MasterBase(BaseModel):
    specialization: Optional[str] = None
    experience_years: int = 0
    description: Optional[str] = None
    base_price: float = 0.0
    work_hours_start: str = "09:00"
    work_hours_end: str = "18:00"
    work_days: str = "1,2,3,4,5,6"

class MasterCreate(MasterBase):
    category_id: int

class MasterUpdate(MasterBase):
    category_id: Optional[int] = None
    is_available: Optional[bool] = None

class Master(MasterBase):
    id: int
    user_id: int
    category_id: int
    rating: float
    total_reviews: int
    total_orders: int
    is_available: bool
    is_verified: bool
    created_at: datetime
    user: User
    category: Category
    
    class Config:
        from_attributes = True

# Service Schemas
class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    duration_hours: int = 1

class ServiceCreate(ServiceBase):
    category_id: int

class Service(ServiceBase):
    id: int
    master_id: int
    category_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Order Schemas
class OrderItemCreate(BaseModel):
    service_id: int
    quantity: int = 1

class OrderCreate(BaseModel):
    master_id: int
    description: Optional[str] = None
    address: str
    scheduled_date: datetime
    order_items: List[OrderItemCreate]

class OrderItem(BaseModel):
    id: int
    service_id: int
    quantity: int
    price: float
    service: Service
    
    class Config:
        from_attributes = True

class Order(BaseModel):
    id: int
    client_id: int
    master_id: int
    status: OrderStatus
    total_amount: float
    description: Optional[str] = None
    address: str
    scheduled_date: datetime
    completed_date: Optional[datetime] = None
    created_at: datetime
    client: User
    master: Master
    order_items: List[OrderItem]
    
    class Config:
        from_attributes = True

# Review Schemas
class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class Review(BaseModel):
    id: int
    client_id: int
    master_id: int
    order_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    client: User
    
    class Config:
        from_attributes = True

# Portfolio Schemas
class PortfolioCreate(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class Portfolio(BaseModel):
    id: int
    master_id: int
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
