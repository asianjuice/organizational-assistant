# backend/app/utils/config.py

from sqlalchemy.orm import declarative_base  # Updated import
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Define the database URL (using SQLite for local development)
DATABASE_URL = "sqlite:///./test.db"

# Create the database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a base class for declarative class definitions
Base = declarative_base()  # Updated usage

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)