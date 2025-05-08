# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Load the environment variables from .env file
load_dotenv()

# Get the DB connection string
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create a session factory (like DbContext)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models (tables)
Base = declarative_base()
