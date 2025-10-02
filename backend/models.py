from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from bson import ObjectId
from sqlalchemy import select


from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SqlEnum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

# models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SqlEnum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    CLIENT = "client"
    MASTER = "master"
    ADMIN = "admin"

from sqlalchemy import Column, Integer, String
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)




class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class UserRole(str, Enum):
    CLIENT = "client"
    MASTER = "master"
    ADMIN = "admin"

class OrderStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: str = Field(..., index=True)
    phone: Optional[str] = Field(None, index=True)
    password_hash: str
    first_name: str
    last_name: str
    role: UserRole = UserRole.CLIENT
    is_active: bool = True
    is_verified: bool = False
    avatar_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "phone": "+998901234567",
                "first_name": "John",
                "last_name": "Doe",
                "role": "client"
            }
        }

class Category(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name_uz: str
    name_ru: str
    name_en: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Master(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    category_id: PyObjectId
    specialization: Optional[str] = None
    experience_years: int = 0
    description: Optional[str] = None
    base_price: float = 0.0
    rating: float = 0.0
    total_reviews: int = 0
    total_orders: int = 0
    is_available: bool = True
    is_verified: bool = False
    work_hours_start: str = "09:00"
    work_hours_end: str = "18:00"
    work_days: str = "1,2,3,4,5,6"  # 1=Monday, 7=Sunday
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Service(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    master_id: PyObjectId
    category_id: PyObjectId
    name: str
    description: Optional[str] = None
    price: float
    duration_hours: int = 1
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class OrderItem(BaseModel):
    service_id: PyObjectId
    quantity: int = 1
    price: float

class Order(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    client_id: PyObjectId
    master_id: PyObjectId
    status: OrderStatus = OrderStatus.PENDING
    total_amount: float
    description: Optional[str] = None
    address: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    order_items: List[OrderItem] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Review(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    client_id: PyObjectId
    master_id: PyObjectId
    order_id: PyObjectId
    rating: int = Field(..., ge=1, le=5)  # 1-5
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Portfolio(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    master_id: PyObjectId
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
