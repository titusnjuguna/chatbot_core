from pydantic import BaseModel, Field, validator
from typing import List,Optional
from datetime import datetime

class QueryRequest(BaseModel):
    document_id: str = Field(..., description="UUID of the document")
    question: str = Field(..., min_length=1)
    service_id: Optional[int] = None  # Optional: filter by service
    
class ServiceQueryRequest(BaseModel):
    service_id: int = Field(..., description="Query all docs in a service")
    question: str = Field(..., min_length=1)

class AnswerResponse(BaseModel):
    answer: str
    sources: List[str]
    document_id: str
    filename: str
    confidence: Optional[float] = None

class UploadResponse(BaseModel):
    filename: str
    status: str
    chunks_stored: int

# class QueryRequest(BaseModel):
#     question: str = Field(..., min_length=1, max_length=1000)
#     doc_id:str
#     # doc_id: str = Field(..., pattern=r"^[a-zA-Z0-9._-]+\.pdf$")


class ServiceBase(BaseModel):
    name: str
    description: str


class ServiceOut(ServiceBase):
    id: int

    class Config:
        from_attributes = True


class DocumentRecordBase(BaseModel):
    document_id: str
    filename: str
    file_path: str
    service_id: int
    owner_id: Optional[int] = None

class DocumentRecordCreate(DocumentRecordBase):
    pass

class DocumentRecordOut(DocumentRecordBase):
    id: int
    upload_date: datetime

    class Config:
        from_attributes = True


class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ServiceRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    document_count: int

    class Config:
        from_attributes = True  

class CustomerInfoRequest(BaseModel):
    name: str
    email: str
    phone: str
    additional_info: Optional[str] = None
    query: str
    service_id: Optional[int] = None

    #validate query to prevent empty string and malicious input, illegal characters, etc.
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        if len(v) > 1000:
            raise ValueError('Query is too long')
        # Add more validation rules as needed (e.g., regex for allowed characters)
        if any(char in v for char in ['<', '>', '{', '}', '$', ';']):
            raise ValueError('Query contains illegal characters')
        return v