import httpx
from pathlib import Path
from typing import List, Optional
from loguru import logger
from sqlalchemy.orm import Session
from config.config import settings
from utils.pdf_parser import extract_text_from_pdf, chunk_text
from config.vector_store import VectorStore

class RAGService:
    def __init__(self):
        self.vector_store = VectorStore(settings.chroma_persist_dir)

    async def process_pdf(
        self, 
        file_path: Path, 
        document_id: str,  # Use UUID instead of filename
        filename: str
    ) -> dict:
        """Process PDF and store in vector database"""
        text = extract_text_from_pdf(file_path)
        chunks = chunk_text(text)
        
        # Store with document_id as the key
        chunks_stored = self.vector_store.store_document(document_id, chunks)
        
        return {
            "chunks_count": chunks_stored,
            "pages_count": len(text.split('\f'))  # Form feed = page break
        }

    async def query_document(
        self, 
        document_id: str, 
        question: str) -> dict:
        """Query a specific document by its UUID"""
        
        # Verify document exists
        doc_record = [] #db.query(DocumentRecord).filter(
        #     DocumentRecord.document_id == document_id,
        #     DocumentRecord.status == "active"
        # ).first()
        
        if not doc_record:
            raise ValueError(f"Document {document_id} not found or inactive")
        
        # Retrieve relevant chunks
        context_chunks = self.vector_store.retrieve(document_id, question, top_k=5)
        
        if not context_chunks:
            return {
                "answer": "No relevant information found in the document.",
                "sources": [],
                "document_id": document_id,
                "filename": doc_record.filename,
                "confidence": 0.0
            }
        
        context = "\n\n".join(context_chunks)
        answer = await self._get_llm_response(context, question)
        
        return {
            "answer": answer,
            "sources": context_chunks,
            "document_id": document_id,
            "filename": doc_record.filename,
            "confidence": self._calculate_confidence(context_chunks)
        }

    async def query_service(
        self, 
        service_id: int, 
        question: str) -> dict:
        """Query all documents in a service"""
        
        # Get all active documents in service
        # doc_records = db.query(DocumentRecord).filter(
        #     DocumentRecord.service_id == service_id,
        #     DocumentRecord.status == "active"
        # ).all()
        doc_records = []
        
        if not doc_records:
            raise ValueError(f"No documents found in service {service_id}")
        
        # Retrieve from all documents
        all_chunks = []
        for doc in doc_records:
            chunks = self.vector_store.retrieve(doc.document_id, question, top_k=3)
            all_chunks.extend([(doc.document_id, doc.filename, chunk) for chunk in chunks])
        
        # Sort by relevance and take top chunks
        # (In production, you'd use actual similarity scores)
        top_chunks = all_chunks[:10]
        
        context = "\n\n".join([f"[{filename}]: {chunk}" for _, filename, chunk in top_chunks])
        answer = await self._get_llm_response(context, question)
        
        return {
            "answer": answer,
            "sources": [chunk for _, _, chunk in top_chunks],
            "documents_searched": len(doc_records),
            "service_id": service_id
        }

    async def _get_llm_response(self, context: str, question: str) -> str:
        """Get response from DeepSeek LLM"""
        
        prompt = f"""Answer the question using ONLY the provided context. If the answer is not in the context, respond with: "I cannot answer that based on the provided documents."

        Context:
        {context}

        Question: {question}

        Answer:"""

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    "https://api.deepseek.com/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.deepseek_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2,
                        "max_tokens": 1000
                    }
                )
                response.raise_for_status()
                answer = response.json()["choices"][0]["message"]["content"].strip()
                return answer
                
            except httpx.HTTPStatusError as e:
                logger.error(f"DeepSeek API error: {e.response.text}")
                raise RuntimeError("Failed to get response from LLM") from e
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise

    def _calculate_confidence(self, chunks: List[str]) -> float:
        """Simple confidence based on number of relevant chunks"""
        if not chunks:
            return 0.0
        # Simple heuristic: more chunks = higher confidence (up to 5 chunks)
        return min(len(chunks) / 5.0, 1.0)
