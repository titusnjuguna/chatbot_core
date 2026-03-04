import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select,func,outerjoin
from models.chatbot import Service ,DocumentRecord,CustomerInfo,Service,customerQuery
from sqlalchemy.orm import aliased
from sqlalchemy import select,func,outerjoin

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
        doc_alias = aliased(DocumentRecord)
        query = (
            select(
            Service.id,
            Service.name,
            Service.description,
            func.count(doc_alias.id).label('document_count'))
        .outerjoin(doc_alias, Service.id == doc_alias.service_id)
        .group_by(Service.id, Service.name, Service.description)
        .order_by(Service.id))
        result = await self.db.execute(query)
        rows = result.all()
        services_list = [
            {
                "id": row.id,
                "name": row.name,
                "description": row.description,
                "document_count": row.document_count
            }
            for row in rows
        ]
        return services_list
    
   
    
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

    

    async def add_customer_info(self,request):
        customer_info = CustomerInfo(
            name = request.name,
            email = request.email,
            phone = request.phone,
            additional_info = request.additional_info
        )
        query = customerQuery(
            question = request.query,
            service_id = request.service_id,
            customer_info = customer_info
        )
        self.db.add(customer_info)
        self.db.add(query)      
        await self.db.commit()
        await self.db.refresh(customer_info)
        await self.db.refresh(query)
        return customer_info
    
    async def get_all_customer_queries(self):
        result = await self.db.execute(select(customerQuery))
        return result.scalars().all()