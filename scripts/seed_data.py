#!/usr/bin/env python3
"""
Seed script to populate the database with initial data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, User, Category, Master, Service, UserRole
from app.auth import get_password_hash

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")

def seed_categories(db: Session):
    """Seed categories"""
    categories_data = [
        {
            "name_uz": "Qurilish va ta'mirlash",
            "name_ru": "Строительство и ремонт", 
            "name_en": "Construction and repair",
            "description": "Uy qurilishi, ta'mirlash va qayta qurish xizmatlari",
            "icon_url": "/icons/construction.svg"
        },
        {
            "name_uz": "Elektr va santexnika",
            "name_ru": "Электрика и сантехника",
            "name_en": "Electrical and plumbing",
            "description": "Elektr va suv tizimlarini o'rnatish va ta'mirlash",
            "icon_url": "/icons/electrical.svg"
        },
        {
            "name_uz": "Sovutish va isitish",
            "name_ru": "Охлаждение и отопление",
            "name_en": "Cooling and heating",
            "description": "Konditsioner va isitish tizimlarini xizmat ko'rsatish",
            "icon_url": "/icons/cooling.svg"
        },
        {
            "name_uz": "Tozalash",
            "name_ru": "Уборка",
            "name_en": "Cleaning",
            "description": "Uy va ofis tozalash xizmatlari",
            "icon_url": "/icons/cleaning.svg"
        },
        {
            "name_uz": "Mebel",
            "name_ru": "Мебель",
            "name_en": "Furniture",
            "description": "Mebel yig'ish va ta'mirlash xizmatlari",
            "icon_url": "/icons/furniture.svg"
        },
        {
            "name_uz": "Avtomobil xizmatlari",
            "name_ru": "Автомобильные услуги",
            "name_en": "Auto services",
            "description": "Avtomobil ta'mirlash va xizmat ko'rsatish",
            "icon_url": "/icons/auto.svg"
        },
        {
            "name_uz": "Bog' xizmatlari",
            "name_ru": "Садовые услуги",
            "name_en": "Garden services",
            "description": "Bog'dorchilik va landshaft dizayni",
            "icon_url": "/icons/garden.svg"
        },
        {
            "name_uz": "Texnologiya va kompyuter",
            "name_ru": "Технологии и компьютеры",
            "name_en": "Technology and computers",
            "description": "Kompyuter va texnologiya xizmatlari",
            "icon_url": "/icons/technology.svg"
        }
    ]
    
    for cat_data in categories_data:
        existing = db.query(Category).filter(Category.name_uz == cat_data["name_uz"]).first()
        if not existing:
            category = Category(**cat_data)
            db.add(category)
    
    db.commit()
    print("✅ Categories seeded successfully")

def seed_admin_user(db: Session):
    """Create admin user"""
    admin_email = "admin@ustatop.uz"
    existing_admin = db.query(User).filter(User.email == admin_email).first()
    
    if not existing_admin:
        admin_user = User(
            email=admin_email,
            phone="+998901234567",
            password_hash=get_password_hash("admin123"),
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)
        db.commit()
        print("✅ Admin user created successfully")
        print(f"   Email: {admin_email}")
        print("   Password: admin123")
    else:
        print("ℹ️  Admin user already exists")

def seed_sample_masters(db: Session):
    """Create sample master users"""
    masters_data = [
        {
            "user": {
                "email": "sarvar.azamov@example.com",
                "phone": "+998901111111",
                "first_name": "Sarvar",
                "last_name": "Azamov",
                "password": "master123"
            },
            "master": {
                "category_name": "Qurilish va ta'mirlash",
                "specialization": "Uy qurilishi va ta'mirlash",
                "experience_years": 15,
                "description": "15 yillik tajribaga ega professional qurilishchi. Uy qurilishi, ta'mirlash va qayta qurish ishlarini sifatli bajaraman.",
                "base_price": 300.0
            }
        },
        {
            "user": {
                "email": "mansur.saidov@example.com", 
                "phone": "+998902222222",
                "first_name": "Mansur",
                "last_name": "Saidov",
                "password": "master123"
            },
            "master": {
                "category_name": "Elektr va santexnika",
                "specialization": "Elektr va santexnika",
                "experience_years": 8,
                "description": "Elektr va santexnika bo'yicha malakali mutaxassis. Barcha turdagi elektr va suv tizimlarini o'rnatish va ta'mirlash.",
                "base_price": 250.0
            }
        },
        {
            "user": {
                "email": "begzod.nazarov@example.com",
                "phone": "+998903333333", 
                "first_name": "Begzod",
                "last_name": "Nazarov",
                "password": "master123"
            },
            "master": {
                "category_name": "Sovutish va isitish",
                "specialization": "Konditsioner va isitish tizimlari",
                "experience_years": 12,
                "description": "Konditsioner va isitish tizimlarini o'rnatish, ta'mirlash va texnik xizmat ko'rsatish bo'yicha mutaxassis.",
                "base_price": 200.0
            }
        },
        {
            "user": {
                "email": "bakrom.axamov@example.com",
                "phone": "+998904444444",
                "first_name": "Bakrom", 
                "last_name": "Axamov",
                "password": "master123"
            },
            "master": {
                "category_name": "Avtomobil xizmatlari",
                "specialization": "Avtomobil ta'mirlash",
                "experience_years": 10,
                "description": "Avtomobil mexanikasi. Barcha turdagi avtomobil ta'mirlash ishlarini bajaraman.",
                "base_price": 150.0
            }
        }
    ]
    
    for master_data in masters_data:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == master_data["user"]["email"]).first()
        if existing_user:
            continue
            
        # Create user
        user = User(
            email=master_data["user"]["email"],
            phone=master_data["user"]["phone"],
            password_hash=get_password_hash(master_data["user"]["password"]),
            first_name=master_data["user"]["first_name"],
            last_name=master_data["user"]["last_name"],
            role=UserRole.MASTER,
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Find category
        category = db.query(Category).filter(Category.name_uz == master_data["master"]["category_name"]).first()
        if not category:
            continue
            
        # Create master profile
        master = Master(
            user_id=user.id,
            category_id=category.id,
            specialization=master_data["master"]["specialization"],
            experience_years=master_data["master"]["experience_years"],
            description=master_data["master"]["description"],
            base_price=master_data["master"]["base_price"],
            rating=4.5,  # Default rating
            total_reviews=0,
            total_orders=0,
            is_available=True,
            is_verified=True
        )
        db.add(master)
        
        # Create sample services
        services_data = [
            {
                "name": f"{master_data['master']['specialization']} - Asosiy xizmat",
                "description": f"{master_data['master']['specialization']} bo'yicha asosiy xizmat",
                "price": master_data["master"]["base_price"],
                "duration_hours": 4
            },
            {
                "name": f"{master_data['master']['specialization']} - Tezkor xizmat", 
                "description": f"{master_data['master']['specialization']} bo'yicha tezkor xizmat",
                "price": master_data["master"]["base_price"] * 0.7,
                "duration_hours": 2
            }
        ]
        
        db.commit()
        db.refresh(master)
        
        for service_data in services_data:
            service = Service(
                master_id=master.id,
                category_id=category.id,
                **service_data
            )
            db.add(service)
    
    db.commit()
    print("✅ Sample masters and services created successfully")

def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create tables
        create_tables()
        
        # Seed data
        seed_categories(db)
        seed_admin_user(db)
        seed_sample_masters(db)
        
        print("🎉 Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
