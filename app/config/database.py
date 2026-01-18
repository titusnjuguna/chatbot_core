from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,declarative_base,Session
from typing import Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import os
from dotenv import load_dotenv

Base = declarative_base()

load_dotenv()

user = os.getenv("DB_USER", "postgres")
password = os.getenv("DB_PASS", "postgres")
host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", "5432")
name = os.getenv("DB_NAME", "postgres")


DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"
print(DATABASE_URL)
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine,class_=AsyncSession,expire_on_commit=False)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def startup_event():
    print("Creating database tables...")
    await create_tables()
    print("Tables created successfully!")


async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
