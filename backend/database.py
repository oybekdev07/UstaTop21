from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite+aiosqlite:///./ustatop.db"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async_session_maker = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()

# Dependency
async def get_db():
    async with async_session_maker() as session:
        yield session
