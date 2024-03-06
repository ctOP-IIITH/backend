"""
This module defines the Vertical model.
"""

from sqlalchemy import inspect, Column, Integer, String, ARRAY
import json
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
    if Base.metadata.bind and "postgresql" in str(Base.metadata.bind.url):
        labels = Column(ARRAY(String(50)), nullable=True)
    else:
        labels = Column(String(50), nullable=True)
    orid = Column(String(50), nullable=False)

    @property
    def labels(self):
        if Base.metadata.bind and "postgresql" in str(Base.metadata.bind.url):
            return self._labels
        else:
            return json.loads(self._labels)

    @labels.setter
    def labels(self, value):
        if Base.metadata.bind and "postgresql" in str(Base.metadata.bind.url):
            self._labels = value
        else:
            self._labels = json.dumps(value)

    def __repr__(self):
        return f"<Vertical {self.res_name}>"
