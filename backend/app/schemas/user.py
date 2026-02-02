from datetime import datetime

from pydantic import BaseModel, EmailStr, UUID7


class UserBase(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: UUID7
    created_at: datetime
    updated_at: datetime


class UserAuth(BaseModel):
    email: EmailStr
    password: str
