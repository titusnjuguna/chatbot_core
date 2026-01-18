"""Application entrypoint for the botCore FastAPI app."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from api.v1.chatbot import router as chatbot_router
from config.database import get_db
from api.api import api_router
from config.config import settings

logger = logging.getLogger(__name__)

app = FastAPI(title="botCore API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    """Initialize resources on application startup."""
    try:
        await get_db()
        logger.info("Database initialized")
    except Exception as exc:
        logger.warning("Database initialization failed: %s", exc)


app.include_router(api_router) #, prefix=settings.API_V1_STR)
