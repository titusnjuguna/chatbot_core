from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.chatbot import Service ,DocumentRecord

class ChatbotRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_service(self, name: str, description: str = None) -> Service:
        service = Service(name=name, description=description)
        self.db.add(service)
        await self.db.commit()
        await self.db.refresh(service)
        return service

    async def get_services(self) -> list[Service]:
        result = await self.db.execute(select(Service))
        return result.scalars().all()
    
    async def get_document_record(self,doc_id):
        result = await self.db.execute(select(DocumentRecord).where(DocumentRecord.document_id == doc_id,DocumentRecord.status == "active"))
        return result.scalars().first
    
    async def get_service_by_id(self,service_id):
        result = await self.db.execute(select(Service).where(Service.id == service_id))
        return result.scalars().first
    
    async def create_document_record(self,document:dict):
        document = DocumentRecord(

            document_id= document.get("document_id"),
            filename = document.get("filename"),
            file_path = document.get("file_path"),
            service_id = document.get("service_id"),
            chunks_count = document.get("chunks_count"),
            pages_count = document.get("pages_count"),
            status = document.get("status")
        )
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    

