from fastapi import APIRouter,Depends,HTTPException,UploadFile,File,Form
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.chatbot import ChatbotRepository
from services.chatbot import ChatbotService
from repositories.users import UserRepository
from services.users import UserService
from config.database import get_db


router = APIRouter()

async def get_chat_service(db: AsyncSession = Depends(get_db)):
    chatRepo =  ChatbotRepository(db)
    return ChatbotService(chatRepo)
async def get_user_service(db: AsyncSession = Depends(get_db)):
    userRepo = UserRepository(db)
    return UserService(userRepo)

@router.get("/dashboard-cards")
async def get_dashboard_cards(
    chatbot_service: ChatbotService = Depends(get_chat_service),
    user_service: UserService = Depends(get_user_service)
):
    services = await chatbot_service.get_services()
    users = await user_service.get_users()
    queries = await chatbot_service.get_all_customer_queries()
    
    return {
        "total_services": len(services),
        "total_users": len(users),
        "total_documents": sum(s.document_count for s in services),
        "total_customer_queries": len(queries)
    }
