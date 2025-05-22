from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship # Import relationship
from src.app.core.db import Base # Import Base from the new location
# Ensure Item model is available for relationship, though not directly used here for definition
# from .item import Item # This might cause circular import if not handled carefully

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner", order_by="Item.id") # Added relationship
