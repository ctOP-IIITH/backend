"""
This module contains the main FastAPI application.
"""

import sys
import time
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.user import router as user_router
from app.routes.verticals import router as verticals_router
from app.routes.subscribe import router as subscribe_router
from app.routes.import_conf import router as import_conf_router
from app.routes.token import router as token_router
from app.database import engine as database, Base, get_session, reset_database
from app.utils.initial_setup import initial_setup
from app.routes.nodes import router as nodes_router
from app.routes.cin import router as cin_router
from app.routes.sensor_types import router as sensor_types_router
from app.routes.stats import router as stats_router
from app.config.settings import OM2M_URL, ROOT_PATH

def initialize():
    """
    This function initializes the application by creating the database tables and creating an admin user if it does not exist.
    """
    # Wait for database to be ready
    for i in range(5):
        try:
            database.connect()
            break
        except Exception as e:
            print(f"Error connecting to database: {e}")
            print(f"Attempt {i+1} failed. Retrying in 10 seconds...")
            time.sleep(10)
    else:
        print("All attempts to connect to database failed. Exiting program.")
        sys.exit(1)

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
        for i in range(5):
            try:
                res = requests.get(OM2M_URL, timeout=5)
                # if 404
                if res.status_code == 404:
                    raise requests.exceptions.RequestException("Mobius not found")
                elif res.status_code == 503:
                    raise requests.exceptions.RequestException("Mobius not ready")
                print("Connection to Mobius successful.")
                break
            except requests.exceptions.RequestException:
                print(f"Attempt {i+1} failed. Retrying in 10 seconds...")
                time.sleep(10)
        else:
            print("All attempts to connect to Mobius failed. Exiting program.")
            sys.exit(1)
        initial_setup(db)

    except requests.RequestException as e:
        print(f"Unable to connect to {OM2M_URL}. Error: {e}")
        raise e


initialize()

app = FastAPI(root_path=ROOT_PATH)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.on_event("shutdown")
async def shutdown():
    """
    This function is called when the application shuts down. It disconnects from the database.
    """
    get_session().close()


# create a / endpoint
@app.get("/")
def read_root():
    return {"message": "Hello World"}


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
