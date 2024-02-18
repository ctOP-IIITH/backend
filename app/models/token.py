"""This module defines the Token class."""

import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey
from app.database import Base


class Token(Base):
    """This class represents the token in the database."""

    __tablename__ = "tokens"

    sensor_type = Column(Integer, ForeignKey(
        "sensor_types.id"), primary_key=True, nullable=False)

    token_id = Column(Integer, primary_key=True)
    assigned_to = Column(Integer, ForeignKey("users.id"))

    status = Column(Boolean, default=False)
    """Issued; Deployed"""

    issue_time = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, sensor_type, token_id, assigned_to):
        self.sensor_type = sensor_type
        self.token_id = token_id
        self.assigned_to = assigned_to
        self.status = False
        self.issue_time = datetime.datetime.now()

    def __repr__(self):
        return f"<Type: {self.node_type}, ID: {self.token_id}>"
