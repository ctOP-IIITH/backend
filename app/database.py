"""
This module provides functionality for connecting to the database and creating a session factory.
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from app.config.settings import DATABASE_URL

Base = declarative_base()

engine = None


def get_session():
    """
    Returns a new session from the session factory.
    """
    SessionLocal = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )
    db = SessionLocal()
    engine.dispose()
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
    print("Database has been reset")


def init_db(db_url):
    global engine

    if db_url.startswith("sqlite:"):
        engine = create_engine(db_url)
    else:
        engine = create_engine(db_url, pool_size=3, max_overflow=0)


# Initialize the database with the default DATABASE_URL
init_db(DATABASE_URL)
