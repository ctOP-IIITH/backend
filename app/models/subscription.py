import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.database import Base

class Subscription(Base):
    """This class represents the subscription table in the database."""

    __tablename__ = "subscription"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    node_id = Column(String(450), nullable=False)
    url = Column(String(450), nullable=False)

    created_date = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, user_id, node_id, url, status):
        self.user_id = user_id
        self.node_id = node_id
        self.url = url

    def __repr__(self):
        return f"<Subscription(user_id={self.user_id}, node_id={self.node_id}, \
    url={self.url}, status={self.status})>"