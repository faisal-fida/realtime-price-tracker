from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.app.schemas.item import Item, ItemCreate
from src.app.core.db import get_db
from src.app.api.dependencies import get_current_user
from src.app.models.user import User as UserModel # Alias to avoid confusion with schema
from src.app.models.item import Item as ItemModel # Alias
from src.app.services import item_service

router = APIRouter()

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_in: ItemCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new item for the current user.
    """
    return await item_service.create_user_item(db=db, item=item_in, user_id=current_user.id)

@router.get("/", response_model=List[Item])
async def read_items(
    db: AsyncSession = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user), 
    skip: int = 0, 
    limit: int = 100
):
    """
    Retrieve items for the current user.
    """
    return await item_service.get_user_items(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{item_id}", response_model=Item)
async def read_item(
    item_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get a specific item by ID for the current user.
    """
    db_item = await item_service.get_item(db=db, item_id=item_id, user_id=current_user.id)
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return db_item

@router.delete("/{item_id}", response_model=Item)
async def delete_item(
    item_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete an item by ID for the current user.
    """
    deleted_item = await item_service.delete_user_item(db=db, item_id=item_id, user_id=current_user.id)
    if deleted_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return deleted_item
