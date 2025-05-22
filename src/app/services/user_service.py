import logging # Import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.app.models.user import User
from src.app.schemas.user import UserCreate
from src.app.core.security import get_password_hash

logger = logging.getLogger(__name__) # Get logger for this module

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    logger.info(f"User created with email: {db_user.email}", extra={"props": {"user_id": db_user.id}}) # Added log message
    return db_user
