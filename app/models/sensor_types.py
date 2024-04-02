"""
This module defines the Sensor types model.
"""

from sqlalchemy import Column, Integer, String, ARRAY, ForeignKey, UniqueConstraint
from app.database import Base


class SensorTypes(Base):
    """
    This class defines the Sensor type model.
    """

    __tablename__ = "sensor_types"

    id = Column(Integer, primary_key=True)
    res_name = Column(String(50), nullable=False)
    parameters = Column(ARRAY(String(50)), nullable=True)
    data_types = Column(ARRAY(String(50)), nullable=True)
    labels = Column(ARRAY(String(50)), nullable=True)
    vertical_id = Column(Integer, ForeignKey("verticals.id"))
    # combination of vertical_id and res_name should be unique
    __table_args__ = (
        UniqueConstraint("vertical_id", "res_name", name="unique_sensor_type"),
    )

    def __repr__(self):
        return f"<Sensor Type (id = {self.id}, res_name = {self.res_name}>, parameters={self.parameters},data_types = {self.data_types}, labels= {self.labels}, vertical_id= {self.vertical_id} )"
