"""
This module defines the Node model.
"""

from sqlalchemy import Column, Integer, String, Float, ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Node(Base):
    """
    This class defines the Node model.
    """

    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True)
    sensor_type_id = Column(Integer, ForeignKey("sensor_types.id"))
    """ID of the sensor type this node belongs to"""
    sensor_node_number = Column(Integer)
    """The ID number of this node in the given sensor type"""

    # sensor_types = relationship("SensorType", back_populates="nodes")
    labels = Column(ARRAY(String(50)), nullable=False)
    lat = Column(Float, nullable=True)
    long = Column(Float, nullable=True)
    location = Column(String(100), nullable=True)
    area = Column(String(100), nullable=True)
    orid = Column(String(50), nullable=False)
    token_num = Column(Integer, nullable=True)
    node_name = Column(String(50), nullable=True)
    node_data_orid = Column(String(50), nullable=True)
    name = Column(String(50), nullable=False)

    def __repr__(self):
        return f"<Node {self.id}>"  # TODO: Return resource name
