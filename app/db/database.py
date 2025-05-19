# app/database.py

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

APP_ENV = os.getenv("APP_ENV", "local")
if APP_ENV == "cloud":
    DATABASE_URL = os.getenv("POSTGRES_URL")
else:
    DATABASE_URL = os.getenv("SQLITE_URL", "sqlite+aiosqlite:///./tree.db")

# Convert relative SQLite path to absolute (optional, for dev convenience)
if DATABASE_URL.startswith("sqlite+aiosqlite:///./"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    relative_path = DATABASE_URL.replace("sqlite+aiosqlite:///./", "")
    abs_path = os.path.join(base_dir, relative_path)
    DATABASE_URL = f"sqlite+aiosqlite:///{abs_path}"

print(f"Using database: {DATABASE_URL}")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Async session
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Declarative base for models
Base = declarative_base()

# Dependency override for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
