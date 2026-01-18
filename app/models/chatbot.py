from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)

    documents = relationship("DocumentRecord", back_populates="service")


class DocumentRecord(Base):
    __tablename__ = "documents_records"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, unique=True, index=True)  # UUID
    filename = Column(String)
    file_path = Column(String)
    upload_date = Column(DateTime, default=datetime.utcnow)
    chunks_count = Column(Integer, default=0) 
    pages_count = Column(Integer, default=0)   
    status = Column(String, default="active")  # active, deleted, processing
    
    service_id = Column(Integer, ForeignKey("services.id"))
    service = relationship("Service", back_populates="documents")


