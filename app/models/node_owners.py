from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from app.database import Base


class NodeOwners(Base):
    """
    This class defines the Node model.
    """

    __tablename__ = "node_owners"

    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, nullable=False)
    vendor_id = Column(Integer, ForeignKey("users.id"))
