# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.routers import auth, users, categories, masters, services, orders, reviews, search



# app = FastAPI(
#     title="Ustatop API",
#     description="Professional Services Platform API",
#     version="1.0.0"
# )

# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # In production, specify your frontend domain
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # Include routers
# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(users.router, prefix="/api/users", tags=["Users"])
# app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
# app.include_router(masters.router, prefix="/api/masters", tags=["Masters"])
# app.include_router(services.router, prefix="/api/services", tags=["Services"])
# app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
# app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
# app.include_router(search.router, prefix="/api/search", tags=["Search"])

# @app.get("/")
# async def root():
#     return {"message": "Ustatop API is running with SQLite!"}

# @app.get("/health")
# async def health_check():
#     return {"status": "healthy", "database": "SQLite"}


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import auth, users, categories, masters, services, orders, reviews, search

app = FastAPI(
    title="Ustatop API",
    description="Professional Services Platform API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # frontend domain yoziladi productionda
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
app.include_router(masters.router, prefix="/api/masters", tags=["Masters"])
app.include_router(services.router, prefix="/api/services", tags=["Services"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])

@app.get("/")
async def root():
    return {"message": "Ustatop API is running with SQLite!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "SQLite"}
