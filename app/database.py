# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# ─────────────────────────────────────────────────────────────────────────────
# Database configuration: Initializes the SQLAlchemy engine and session
#─────────────────────────────────────────────────────────────────────────────

# Load environment variables from a .env file
load_dotenv()

# Get database connection URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Convert relative SQLite path to an absolute path for consistency
if DATABASE_URL and DATABASE_URL.startswith("sqlite:///./"):
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Base path of this file
    relative_path = DATABASE_URL.replace("sqlite:///./", "")
    abs_path = os.path.join(base_dir, relative_path)
    DATABASE_URL = f"sqlite:///{abs_path}"

# Optional debug print to verify connection string
print(f"Using database: {DATABASE_URL}")

# Create the SQLAlchemy engine with SQLite-specific settings
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create a session factory to be used throughout the app
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for defining ORM models
Base = declarative_base()
