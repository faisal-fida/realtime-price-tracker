from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.app.core.db import Base
from src.app.models.user import User # Ensure User is imported

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True, nullable=False)
    desired_price = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Corrected table name to 'users'
    owner = relationship("User", back_populates="items")

# Add the 'items' relationship to the User model if it's not already there
# This typically goes in src/app/models/user.py
# User.items = relationship("Item", back_populates="owner", order_by=Item.id)
