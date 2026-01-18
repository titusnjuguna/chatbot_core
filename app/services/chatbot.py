from schema.chatbot import ServiceCreate, ServiceRead
from repositories.chatbot import ChatbotRepository
from models.chatbot import Service

class ChatbotService:
    def __init__(self, chatbot_repo: ChatbotRepository):
        self.chat_repo = chatbot_repo

    async def create_service(self, service_in: ServiceCreate) -> ServiceRead:
        service = await self.chat_repo.create_service(
            name=service_in.name,
            description=service_in.description
        )
        return ServiceRead.model_validate(service)

    async def get_services(self) -> list[ServiceRead]:
        services = await self.chat_repo.get_services()
        return [ServiceRead.model_validate(s) for s in services]
    
    async def verify_document(self,doc_id):
        doc =  await self.chat_repo.get_document_record(doc_id)
        return doc

    async def get_service_by_id(self,service_id):
        return await self.chat_repo.get_service_by_id(service_id)
    
    async def add_document_record(self,document:dict):
        return await self.chat_repo.create_document_record(document)

    