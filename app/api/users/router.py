from datetime import timezone, datetime

from django.contrib.auth.hashers import make_password
from ninja import Router
from django.db import connection
from django.http import HttpResponse
from typing import List
import json
from .schemas import UserSchema, UserCreateSchema, UserUpdateSchema

router = Router(tags=["users"])

@router.get("/", response=List[UserSchema])
def list_users(request):
    """Get all users"""
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT user_id, username, email, role, last_login, is_active, date_joined FROM api_user")
        users = []
        for row in cursor.fetchall():
            user = {
                "user_id": row[0],
                "username": row[1],
                "email": row[2],
                "role": row[3],
                "last_login": row[4],
                "is_active": row[5],
                "date_joined": row[6],
            }
            users.append(user)
        return users


@router.post("/", response=UserSchema)
def create_user(request, user_data: UserCreateSchema):
    with connection.cursor() as cursor:
        # Check if username or email already exists
        cursor.execute(
            "SELECT user_id FROM api_user WHERE username = %s OR email = %s",
            [user_data.username, user_data.email]
        )
        if cursor.fetchone():
            return HttpResponse(
                status=400,
                content=json.dumps({"detail": "Username or email already exists"})
            )

        # Insert new user
        password_hash = make_password(user_data.password)
        now = datetime.now(timezone.utc)

        cursor.execute(
            """
            INSERT INTO api_user (username, email, role, password, is_active, date_joined, last_login)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING user_id, username, email, role, is_active, date_joined, last_login
            """,
            [
                user_data.username,
                user_data.email,
                user_data.role,
                password_hash,
                True if user_data.is_active is None else user_data.is_active,
                now,
                now
            ]
        )

        row = cursor.fetchone()
        print("user_id", row[0])
        user = {
            "user_id": row[0],
            "username": row[1],
            "email": row[2],
            "role": row[3],
            "is_active": row[4],
            "last_login": row[5],
            "date_joined": row[6],
        }
        return user


@router.get("/{user_id}", response=UserSchema)
def get_user(request, user_id: int):
    """Get user by ID"""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT user_id, username, email, role, last_login, is_active, date_joined FROM api_user WHERE user_id = %s",
            [user_id]
        )
        row = cursor.fetchone()
        if not row:
            return HttpResponse(status=404, content=json.dumps({"detail": "User not found"}))

        user = {
            "user_id": row[0],
            "username": row[1],
            "email": row[2],
            "role": row[3],
            "last_login": row[4],
            "is_active": row[5],
            "date_joined": row[6],
        }

        return user

@router.put("/{user_id}", response=UserSchema)
def update_user(request, user_id: int, user_data: UserUpdateSchema):
    with connection.cursor() as cursor:
        # Check if user exists
        cursor.execute("SELECT user_id FROM api_user WHERE user_id = %s", [user_id])
        if not cursor.fetchone():
            return HttpResponse(status=404, content=json.dumps({"detail": "User not found"}))

        # Build update query dynamically based on provided fields
        update_fields = []
        params = []

        if user_data.username:
            update_fields.append("username = %s")
            params.append(user_data.username)

        if user_data.email:
            update_fields.append("email = %s")
            params.append(user_data.email)

        if user_data.password:
            update_fields.append("password = %s")
            params.append(make_password(user_data.password))

        if user_data.role:
            update_fields.append("role = %s")
            params.append(user_data.role)

        if user_data.is_active:
            update_fields.append("is_active = %s")
            params.append(user_data.is_active)

        if not update_fields:
            # If no fields to update, just return the current user
            cursor.execute(
                "SELECT user_id, username, email, role, last_login, is_active, date_joined FROM api_user WHERE user_id = %s",
                [user_id]
            )
            row = cursor.fetchone()
            user = {
                "user_id": row[0],
                "username": row[1],
                "email": row[2],
                "role": row[3],
                "is_active": row[4],
                "last_login": row[5],
                "date_joined": row[6],
            }
            return user

        # Add asset_id to params for WHERE clause
        params.append(user_id)

        # Execute update query
        cursor.execute(
            f"""
            UPDATE api_user
            SET {", ".join(update_fields)}
            WHERE user_id = %s
            RETURNING user_id, username, email, role, last_login, is_active, date_joined
            """,
            params
        )

        row = cursor.fetchone()
        user = {
            "user_id": row[0],
            "username": row[1],
            "email": row[2],
            "role": row[3],
            "last_login": row[4],
            "is_active": row[5],
            "date_joined": row[6],
        }
        return user


@router.delete("/{user_id}")
def delete_user(request, user_id: int):
    """Delete a user"""
    with connection.cursor() as cursor:
        # Check if user exists
        cursor.execute("SELECT user_id FROM api_user WHERE user_id = %s", [user_id])
        if not cursor.fetchone():
            return HttpResponse(status=404, content=json.dumps({"detail": "User not found"}))

        # Delete user
        cursor.execute("DELETE FROM api_user WHERE user_id = %s", [user_id])
        return {"success": True}


@router.post("/activity/log", response=dict)
def log_user_activity(request, activity: dict):
    """Log user activity"""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO user_activity_logs
            (user_id, activity_type, timestamp, description)
            VALUES (%s, %s, %s, %s)
            """,
            [
                request.user.id,
                activity["action"],
                datetime.now(timezone.utc),
                json.dumps(activity["details"])
            ]
        )

    return {"success": True, "message": "Activity logged"}