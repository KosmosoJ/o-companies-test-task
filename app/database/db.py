from dotenv import find_dotenv, load_dotenv
from os import getenv
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


if find_dotenv():
    load_dotenv()
    DB_PATH = getenv("DB_PATH")


engine = create_async_engine(DB_PATH, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
