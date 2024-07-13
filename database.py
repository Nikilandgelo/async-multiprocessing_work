import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlmodel import SQLModel
from models import People
from sqlalchemy.exc import PendingRollbackError


async def init_async_orm():
    DATABASE: AsyncEngine = create_async_engine(f'postgresql+asyncpg://'
                                f'{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@'
                                f'{os.getenv("POSTGRES_HOST")}:{os.getenv("POSTGRES_PORT")}/'
                                f'{os.getenv("POSTGRES_DB")}'
    )
    async with DATABASE.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
    
    async_session = async_sessionmaker(DATABASE, expire_on_commit=False)
    return async_session


async def insert_data(pack_peoples: list[dict], session: AsyncSession):
    db_peoples: list[People] = [People(**people_dict) for people_dict in pack_peoples]
    session.add_all(db_peoples)
    try:
        await session.commit()
    except PendingRollbackError as error:
        pass