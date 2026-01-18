from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Path,Depends,File,Form
from sqlalchemy.ext.asyncio import AsyncSession 
from schema.chatbot import UploadResponse,ServiceRead,QueryRequest, AnswerResponse,ServiceCreate,ServiceQueryRequest
from utils.security import sanitize_filename
from config.config import settings
from config.dependancies import get_rag_service
from config.database import get_db
import shutil
from config.rag_service import RAGService
from repositories.chatbot import  ChatbotRepository
from services.chatbot import ChatbotService
from fastapi.responses import StreamingResponse
from config.database import get_db
from loguru import logger
from models.chatbot import DocumentRecord
import httpx
import uuid
import asyncio




router = APIRouter()

async def get_chat_service(db: AsyncSession = Depends(get_db)):
    chatRepo =  ChatbotRepository(db)
    return ChatbotService(chatRepo)


def get_rag_service():
    return RAGService()


@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    service_type: int = Form(...),
    chatbot_service : ChatbotService = Depends(get_chat_service),
    rag_service: RAGService = Depends(get_rag_service)):
   
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files are allowed")
    
    service = await chatbot_service.get_service_by_id(service_type)
    if not service:
        raise HTTPException(404, f"Service {service_type} not found")
    
    # Generate UUID for document
    document_id = str(uuid.uuid4())
    print(document_id)
    
    # Save file with UUID in name to avoid conflicts
    safe_filename = f"{document_id}_{file.filename}"
    file_path = settings.upload_dir / safe_filename
    
    try:
        # Save file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        process_result = await rag_service.process_pdf(
            file_path, 
            document_id,
            file.filename
        )
        #add document records
        document={
            "document_id":document_id,
            "filename" : file.filename,
            "file_path": str(file_path),
            "service_id":service_type,
            "chunks_count":process_result["chunks_count"],
            "pages_count":process_result["pages_count"],
            "status":"active"}
        resul = await chatbot_service.add_document_record(document)      
        return {
            "message": "PDF uploaded and processed successfully",
            "document_id": document_id,
            "filename": file.filename,
            "chunks_created": process_result["chunks_count"],
            "pages": process_result["pages_count"],
            "service": service,
            "result": resul
        }
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(500, f"Upload failed: {str(e)}")

    


@router.post("/create-service", response_model=ServiceRead)
async def create_service(
    request: ServiceCreate,
    service: ChatbotService = Depends(get_chat_service)
):
    return await service.create_service(request)

@router.get("/get-services", response_model=list[ServiceRead])
async def get_services(
    service: ChatbotService = Depends(get_chat_service)
):
    return await service.get_services()


@router.post("/query-service")
async def query_service(
    request: ServiceQueryRequest,
    rag_service: RAGService = Depends(get_rag_service),
    chatbot_service : ChatbotService = Depends(get_chat_service)
):
    """Query all documents in a service"""
    try:
        result = await rag_service.query_service(
            request.service_id,
            request.question,
        )
        return result
        
    except ValueError as ve:
        raise HTTPException(404, str(ve))
    except RuntimeError as re:
        raise HTTPException(502, str(re))
    except Exception as e:
        logger.error(f"Service query failed: {str(e)}")
        raise HTTPException(500, f"Query processing failed: {str(e)}")



@router.post("/query-document-stream")
async def query_document_stream(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service),
    chatbot_service: ChatbotService = Depends(get_chat_service)):
    async def generate():
        try:
            # Verify document
            doc_record = await chatbot_service.verify_document(doc_id=request.document_id)
            if not doc_record:
                yield "data: {\"error\": \"Document not found\"}\n\n"
                return

            # Retrieve context (non-blocking)
            context_chunks = await asyncio.to_thread(
                rag_service.vector_store.retrieve,
                request.document_id,
                request.question,
                top_k=5
            )
            context = "\n\n".join(context_chunks)

            prompt = f"""Answer using ONLY the context below.

            Context:
            {context}
            Question: {request.question}
            Answer:"""
            # Stream from DeepSeek
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    "https://api.deepseek.com/v1/chat/completions",  # ✅ Fixed URL
                    headers={
                        "Authorization": f"Bearer {settings.deepseek_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2,
                        "stream": True
                    }
                ) as response:
                    
                    # Handle API errors
                    if response.status_code != 200:
                        error_detail = await response.aread()
                        yield f"data: {{\"error\": \"DeepSeek API error: {error_detail.decode()}\"}}\n\n"
                        return

                    # Stream SSE chunks
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            yield f"{line}\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )






    


