# Ustatop.uz Backend API

Professional Services Platform - FastAPI backend with SQLite database.

## Features

- User authentication and authorization (JWT)
- Master profiles and services management
- Order management system
- Review and rating system
- Category-based service search
- Admin panel for platform management

## Tech Stack

- **Backend Framework**: FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens with passlib
- **API Documentation**: Swagger UI (auto-generated)

## Database

This project uses **SQLite** for data storage with async support via aiosqlite.

### Admin Credentials

- **Email**: admin@ustatop.uz
- **Password**: admin123

## Installation

1. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

2. Run database migrations:
\`\`\`bash
alembic upgrade head
\`\`\`

3. Seed initial data:
\`\`\`bash
python scripts/seed_data.py
\`\`\`

4. Start the server:
\`\`\`bash
uvicorn backend.main:app --reload
\`\`\`

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## Project Structure

\`\`\`
├── backend/
│   ├── main.py           # FastAPI application
│   ├── database.py       # SQLite database configuration
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   └── auth.py           # Authentication utilities
├── app/
│   └── routers/          # API route handlers
│       ├── auth.py
│       ├── users.py
│       ├── categories.py
│       ├── masters.py
│       ├── services.py
│       ├── orders.py
│       └── reviews.py
├── scripts/
│   └── seed_data.py      # Database seeding script
├── alembic/              # Database migrations
└── ustatop.db            # SQLite database file
\`\`\`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/token` - Get access token

### Users
- `GET /api/users` - List all users (admin only)
- `GET /api/users/{id}` - Get user by ID
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user (admin only)

### Categories
- `GET /api/categories` - List all categories
- `POST /api/categories` - Create category (admin only)
- `PUT /api/categories/{id}` - Update category (admin only)
- `DELETE /api/categories/{id}` - Delete category (admin only)

### Masters
- `GET /api/masters` - List all masters
- `GET /api/masters/{id}` - Get master by ID
- `POST /api/masters` - Create master profile
- `PUT /api/masters/{id}` - Update master profile
- `DELETE /api/masters/{id}` - Delete master profile

### Services
- `GET /api/services` - List all services
- `GET /api/services/{id}` - Get service by ID
- `POST /api/services` - Create service
- `PUT /api/services/{id}` - Update service
- `DELETE /api/services/{id}` - Delete service

### Orders
- `GET /api/orders` - List orders
- `GET /api/orders/{id}` - Get order by ID
- `POST /api/orders` - Create order
- `PUT /api/orders/{id}` - Update order status
- `DELETE /api/orders/{id}` - Cancel order

### Reviews
- `GET /api/reviews` - List reviews
- `POST /api/reviews` - Create review
- `PUT /api/reviews/{id}` - Update review
- `DELETE /api/reviews/{id}` - Delete review

## User Roles

- **CLIENT**: Regular users who can book services
- **MASTER**: Service providers who offer their services
- **ADMIN**: Platform administrators with full access

## License

MIT
# UstaTop21
# UstaTop21
