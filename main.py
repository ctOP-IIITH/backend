"""
This module contains the main FastAPI application.
"""

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.user import router as user_router
from app.routes.verticals import router as verticals_router
from app.routes.subscribe import router as subscribe_router
from app.routes.import_conf import router as import_conf_router
from app.routes.token import router as token_router
from app.database import engine as database, get_session, Base, reset_database
from app.utils.initial_setup import initial_setup
from app.routes.nodes import router as nodes_router
from app.routes.cin import router as cin_router
from app.routes.sensor_types import router as sensor_types_router
from app.routes.stats import router as stats_router
from app.config.settings import OM2M_URL

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


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
        db = next(get_session())

        # ########################################################
        # ## WARNING: DO NOT UNCOMMENT THE FOLLOWING LINE      ##
        # ## UNLESS YOU KNOW EXACTLY WHAT YOU ARE DOING!       ##
        # ## THIS COULD POTENTIALLY CAUSE SERIOUS ISSUES.      ##
        # ## ENSURE YOU MANUALLY CLEAR ONEM2M DB AFTER THIS.   ##
        # ########################################################
        # reset_database()

    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise e

    try:
        requests.get(OM2M_URL, timeout=5)
        print("Connection to OM2M successful.")
        initial_setup(db)

    except requests.RequestException as e:
        print(f"Unable to connect to {OM2M_URL}. Error: {e}")
        raise e


@app.on_event("shutdown")
async def shutdown():
    """
    This function is called when the application shuts down. It disconnects from the database.
    """
    get_session().close()


# include user_router with prefix /user
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(verticals_router, prefix="/verticals", tags=["Verticals"])
app.include_router(nodes_router, prefix="/nodes", tags=["Nodes"])
app.include_router(import_conf_router, prefix="/import", tags=["Import Configurations"])
app.include_router(cin_router, prefix="/cin", tags=["Content Instance"])
app.include_router(sensor_types_router, prefix="/sensor-types", tags=["Sensor Types"])
app.include_router(token_router, prefix="/token")
app.include_router(stats_router, prefix="/stats")
app.include_router(subscribe_router, prefix="/subscription")

# Include get_session as a dependency globally
app.dependency_overrides[get_session] = get_session
