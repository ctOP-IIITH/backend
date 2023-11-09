"""
This module contains a FastAPI application.
"""

from fastapi import FastAPI

app = FastAPI()


# Basic route
@app.get("/")
def home():
    """
    Returns a JSON response with a greeting message.
    """
    return {"Hello": "World"}
