"""
This module defines the Sensor types model.
"""

from sqlalchemy import Column, Integer, String,  ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class SensorTypes(Base):
    """
    This class defines the Sensor type model.
    """

    __tablename__ = "sensor_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    parameters = Column(ARRAY(String(50)), nullable=False)
    data_types = Column(ARRAY(String(50)), nullable=False)
    labels = Column(ARRAY(String(50)), nullable=False)

    vertical_id = Column(Integer, ForeignKey("verticals.id"))
    verticals = relationship("Vertical", back_populates="sensor_types")

    def __repr__(self):
        return f"<Sensor Type {self.name}>"
