from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from src.app.models.item import Item
from src.app.schemas.item import ItemCreate
from src.app.tasks.scraper import scrape_price_task # Import the Celery task

async def create_user_item(db: AsyncSession, item: ItemCreate, user_id: int) -> Item:
    db_item = Item(
        url=str(item.url), # Ensure HttpUrl is converted to string for DB
        desired_price=item.desired_price,
        owner_id=user_id
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)

    # Trigger the Celery task
    if db_item.id is not None and db_item.url is not None: # Ensure id and url are not None
        scrape_price_task.delay(db_item.id, db_item.url)
    
    return db_item

async def get_user_items(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> List[Item]:
    result = await db.execute(
        select(Item)
        .filter(Item.owner_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())

async def get_item(db: AsyncSession, item_id: int, user_id: int) -> Optional[Item]:
    result = await db.execute(
        select(Item).filter(Item.id == item_id, Item.owner_id == user_id)
    )
    return result.scalars().first()

async def delete_user_item(db: AsyncSession, item_id: int, user_id: int) -> Optional[Item]:
    item_to_delete = await get_item(db, item_id, user_id)
    if item_to_delete:
        await db.delete(item_to_delete)
        await db.commit()
        return item_to_delete
    return None
