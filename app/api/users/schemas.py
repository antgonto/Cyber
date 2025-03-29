# app/api/schemas.py
from typing import Optional, List
from datetime import datetime
from ninja import Schema


class UserSchema(Schema):
    user_id: int
    username: str
    email: str
    role: str
    last_login: Optional[datetime] = None


class UserCreateSchema(Schema):
    username: str
    email: str
    password: str
    role: Optional[str] = 'user'


class UserUpdateSchema(Schema):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None