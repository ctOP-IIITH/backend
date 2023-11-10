"""
This module defines the User model.
"""

from sqlalchemy import Column, Integer, String
from app.database import Base


class User(Base):
    """
    This class defines the User model.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"
