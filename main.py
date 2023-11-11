"""
This module contains the main FastAPI application.
"""

from fastapi import FastAPI
from app.routes.user import router as user_router
from app.database import engine as database, get_session, Base

app = FastAPI()


@app.on_event("startup")
async def startup():
    """
    This function is called when the application starts up.
    It connects to the database and creates a default admin user if it doesn't exist.
    """
    Base.metadata.create_all(bind=database)
    # connect to the database
    try:
        database.connect()
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise e


@app.on_event("shutdown")
async def shutdown():
    """
    This function is called when the application shuts down. It disconnects from the database.
    """
    get_session().close()


# include user_router with prefix /user
app.include_router(user_router, prefix="/user")


# Include get_session as a dependency globally
app.dependency_overrides[get_session] = get_session
