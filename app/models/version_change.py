"""
This module defines the Version Change model.
"""

import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class VersionChange(Base):
    """
    This class defines the Version Change model.
    """

    __tablename__ = "version_changes"

    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey("nodes.id"),  nullable=False)
    node = relationship("Node", back_populates="version_changes")

    version_num = Column(String(20), nullable=False)
    time_deployed = Column(DateTime, nullable=False,
                           default=datetime.datetime.now)

    def __repr__(self):
        return f"<VersionChange Node={self.node_id} to Version {self.version_num}>"
