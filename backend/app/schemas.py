from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str
    role: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class ExamBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration_minutes: int

class ExamCreate(ExamBase):
    pass

class Exam(ExamBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
