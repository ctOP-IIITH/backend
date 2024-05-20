"""
This module defines the Vertical model.
"""

from sqlalchemy import Column, Integer, String, ARRAY
from app.database import Base


class Vertical(Base):
    """
    This class defines the Vertical model.
    """

    __tablename__ = "verticals"

    id = Column(Integer, primary_key=True)
    res_name = Column(String(50), nullable=False)
    res_short_name = Column(String(10), nullable=False)
    description = Column(String(50), nullable=True)
    labels = Column(ARRAY(String(50)), nullable=True)
    orid = Column(String(50), nullable=False)

    def __repr__(self):
        return f"<Vertical {self.res_name}>"
