from fastapi import APIRouter
from api.v1 import chatbot,users


api_router = APIRouter()

api_router.include_router(users.router,prefix="/api/v1/users",tags=["Users"])

api_router.include_router(chatbot.router,prefix="/api/v1/chatbot",tags=["chatbot"])