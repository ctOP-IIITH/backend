"""
This module provides functionality for connecting to the database and creating a session factory.
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config.settings import DATABASE_URL

Base = declarative_base()


def get_session():
    """
    Returns a new session from the session factory.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_database():
    """
    Drops all tables and recreates them.
    """
    with engine.begin() as _:
        # Drop all tables
        meta = MetaData()
        meta.reflect(bind=engine)
        meta.drop_all(bind=engine)

        # Recreate all tables
        Base.metadata.create_all(bind=engine)


engine = create_engine(DATABASE_URL, pool_size=3, max_overflow=0)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
