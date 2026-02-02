"""Application entrypoint for the botCore FastAPI app."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from api.v1.chatbot import router as chatbot_router
from config.database import get_db,AsyncSessionLocal
from api.api import api_router
from config.config import settings
from sqlalchemy import text  
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

app = FastAPI(title="botCore API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.on_event("startup")
async def on_startup():
    """Verify database connectivity on application start"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1")) 
        logger.info("✓ Database connection verified successfully")
    except Exception as exc:
        logger.error("✗ Database initialization FAILED: %s", str(exc))
        # CRITICAL: Raise to prevent app starting with broken DB
        raise RuntimeError("Database unavailable - aborting startup") from exc


app.include_router(api_router) #, prefix=settings.API_V1_STR)
