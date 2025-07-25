from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

# Общие настройки
PASSWORD_MIN_LENGTH = 8
NAME_MAX_LENGTH = 50


class SUserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: Optional[str]


class SUserLogin(BaseModel):
    email: EmailStr
    password: str


class SUserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: Optional[str]
    is_active: bool
    created_at: datetime
    role_id: int

    class Config:
        from_attributes = True


class SUserUpdate(BaseModel):
    first_name: str
    last_name: str
    password: str
