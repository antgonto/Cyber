from typing import Optional
from datetime import datetime
from ninja import Schema
from pydantic import Field

class UserSchema(Schema):
    user_id: int = Field(..., description="Unique identifier for the user")
    username: str = Field(..., description="User's username")
    email: str = Field(..., description="User's email address")
    role: str = Field(..., description="User's role in the system")
    is_active: bool = Field(True, description="Whether the user account is active")
    last_login: Optional[datetime] = Field(None, description="Timestamp of user's last login")
    date_joined: Optional[datetime] = Field(None, description="Timestamp when user joined")

    class Config:
        schema_extra = {"examples": [{"username": "example_user", "email": "user@example.com", "role": "user"}]}
        validate_assignment = True

class UserCreateSchema(Schema):
    username: str = Field(..., description="Username for the new user")
    email: str = Field(..., description="Email address for the new user")
    password: str = Field(..., description="Password for the new user")
    role: str = Field("user", description="Role for the new user")
    is_active: bool = Field(True, description="Whether the user account is active")

class UserUpdateSchema(Schema):

    username: Optional[str] = Field(None, description="Updated username")
    email: Optional[str] = Field(None, description="Updated email address")
    password: Optional[str] = Field(None, description="Updated password")
    role: Optional[str] = Field(None, description="Updated role")
    is_active: Optional[bool] = Field(None, description="Whether the user account is active")

    class Config:
        validate_assignment = True

class UserActivityLogSchema(Schema):
    activity_id: Optional[int] = Field(None, description="ID of the activity log")
    user_id: int = Field(..., description="ID of the user")
    activity_type: str = Field(..., description="Type of the activity performed by the user")
    description: Optional[str] = Field(None, description="Detailed description of the activity")
    timestamp: Optional[datetime] = Field(None, description="Timestamp of the activity")

    class Config:
        input_exclude = {"activity_id", "timestamp"}