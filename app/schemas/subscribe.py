"""
This module contains Pydantic models for user-related requests and responses.
"""

from pydantic import BaseModel


class Subscription(BaseModel):
    """
    Pydantic model for creating a new subscription.
    """

    url: str
    node_id: str


class SubscriptionDetails(BaseModel):
    """
    Pydantic model for getting subscription details
    """

    node_id: str