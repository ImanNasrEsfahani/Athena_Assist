from src.log_config import loggerApp

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import User
from .database import get_async_session


async def create_user(user_data: dict) -> User:
    async for db in get_async_session():
        new_user = User(**user_data.dict())
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user


async def delete_user(chat_id: int) -> None:
    async for db in get_async_session():
        result = await db.execute(select(User).where(User.telegram_chat_id == chat_id))
        user = result.scalars().one_or_none()

        await db.delete(user)
        user = await db.commit()
        return user


async def get_user_by_chat_id(chat_id: int):
    async for db in get_async_session():
        result = await db.execute(select(User).where(User.telegram_chat_id == chat_id))
        return result.scalars().first()


async def get_user_by_id(user_id: int):
    async for db in get_async_session():
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()


async def get_user_by_email(email: str):
    async for db in get_async_session():
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()


async def get_user_by_mobile(mobile: str):
    async for db in get_async_session():
        result = await db.execute(select(User).where(User.mobile == mobile))
        return result.scalars().first()


async def get_all_active_users():
    async for db in get_async_session():
        result = await db.execute(select(User).where(User.active.is_(True)))
        users = result.scalars().all()
        return users


async def get_all_users():
    async for db in get_async_session():
        result = await db.execute(select(User))
        users = result.scalars().all()
        return users

# --------- sample old
# from .exceptions import item_not_found_exception
#
# async def create_item(item: Item, db: Session):
#     db_item = ItemModel(**item.dict())
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item
#
# async def get_item(item_id: int, db: Session):
#     item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
#     if not item:
#         item_not_found_exception()
#     return item
