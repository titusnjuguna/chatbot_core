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


class CustomerInfo(Base):
    __tablename__ = "customer_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    additional_info = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    customerQuery = relationship("customerQuery", back_populates="customer_info")

    def __repr__(self):
        return f"<CustomerInfo(name={self.name}, email={self.email}, phone={self.phone})>"
    
class customerQuery(Base):
    __tablename__ = "customer_queries"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text)
    is_answered = Column(Integer, default=0)  # 0 for unanswered, 1 for answered
    service_id = Column(Integer, ForeignKey("services.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    CustomerInfo_id = Column(Integer, ForeignKey("customer_info.id"))
    customer_info = relationship("CustomerInfo", backref="queries")
 