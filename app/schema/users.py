# class UserBase(BaseModel):
#     username: str = Field(..., min_length=1, max_length=50)
#     email: EmailStr
#     full_name: Optional[str] = Field(None, max_length=100)
#     bio: Optional[str] = None


# class UserCreate(UserBase):
#     password: str = Field(..., min_length=8)


# class UserUpdate(BaseModel):
#     email: Optional[EmailStr] = None
#     full_name: Optional[str] = Field(None, max_length=100)
#     bio: Optional[str] = None
#     password: Optional[str] = Field(None, min_length=8)



    
# class User(UserBase):
#     id: int
#     password_hash: str
#     is_active: bool
#     is_admin: bool
#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         from_attributes = True

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional,List


class UserBase(BaseModel):
    email: str
    name: str

class UserCreate(UserBase):
    password: str  

class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True  


class UserLogin(BaseModel):
    email: EmailStr
    password:str


class CustomerBase(BaseModel):
    name: str
    email: str
    phone: str

class CustomerCreate(CustomerBase):
    pass

class CustomerOut(CustomerBase):
    id: int

    class Config:
        from_attributes = True