from typing import Optional
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime

class ItemBase(BaseModel):
    url: HttpUrl
    desired_price: Optional[float] = Field(default=None, gt=0)

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_id: int
    is_active: bool = True
    created_at: datetime
    last_updated: datetime

    class Config:
        orm_mode = True # Pydantic V1
        # from_attributes = True # Pydantic V2
