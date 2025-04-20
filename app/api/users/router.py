from datetime import timezone, datetime

from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from ninja import Router
from django.db import connection
from django.http import HttpResponse
from typing import List
import json

from .models import User, UserActivityLog
from .schemas import UserSchema, UserCreateSchema, UserUpdateSchema, UserActivityLogFullSchema, \
    UserActivityLogCreateSchema, UserActivityLogFilterSchema, UserActivityLogUpdateSchema

router = Router(tags=["users"])

@router.get("/", response=List[UserSchema])
def list_users(request):
    print("list_users")
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


@router.post("/activity-logs/", response=UserActivityLogFullSchema)
def create_activity_log(request, payload: UserActivityLogCreateSchema):
    with connection.cursor() as cursor:
        # Check if user exists
        cursor.execute("SELECT user_id FROM api_user WHERE user_id = %s", [payload.user_id])
        if not cursor.fetchone():
            return HttpResponse(status=404, content=json.dumps({"detail": "User not found"}))

        now = datetime.now(timezone.utc)
        cursor.execute(
            """
            INSERT INTO user_activity_logs 
            (user_id, activity_type, timestamp, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, user_id, activity_type, timestamp, description
            """,
            [
                payload.user_id,
                payload.activity_type,
                now,
                payload.description,
                payload.ip_address,
                payload.resource_type,
                payload.resource_id
            ]
        )

        row = cursor.fetchone()
        return {
            "log_id": row[0],
            "user_id": row[1],
            "activity_type": row[2],
            "timestamp": row[3],
            "description": row[4],
            "ip_address": row[5],
            "resource_type": row[6],
            "resource_id": row[7]
        }


@router.get("/activity-logs/", response=List[UserActivityLogFullSchema])
def list_activity_logs(request, filters: UserActivityLogFilterSchema = None):
    with connection.cursor() as cursor:
        query = "SELECT id, user_id, activity_type, timestamp, description FROM user_activity_logs"
        conditions = []
        params = []

        if filters:
            if filters.user_id:
                conditions.append("user_id = %s")
                params.append(filters.user_id)
            if filters.activity_type:
                conditions.append("activity_type = %s")
                params.append(filters.activity_type)
            if filters.resource_type:
                conditions.append("resource_type = %s")
                params.append(filters.resource_type)
            if filters.from_date:
                from_date = datetime.strptime(filters.from_date, "%Y-%m-%d")
                conditions.append("timestamp >= %s")
                params.append(from_date)
            if filters.to_date:
                to_date = datetime.strptime(filters.to_date, "%Y-%m-%d")
                conditions.append("timestamp <= %s")
                params.append(to_date)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY timestamp DESC"

        cursor.execute(query, params)

        results = []
        for row in cursor.fetchall():
            results.append({
                "log_id": row[0],
                "user_id": row[1],
                "activity_type": row[2],
                "timestamp": row[3],
                "description": row[4],
                "ip_address": row[5],
                "resource_type": row[6],
                "resource_id": row[7]
            })

        return results


@router.get("/activity-logs/{log_id}/", response=UserActivityLogFullSchema)
def get_activity_log(request, log_id: int):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, user_id, activity_type, timestamp, description
            FROM user_activity_logs WHERE id = %s
            """,
            [log_id]
        )
        row = cursor.fetchone()
        if not row:
            return HttpResponse(status=404, content=json.dumps({"detail": "Activity log not found"}))

        return {
            "log_id": row[0],
            "user_id": row[1],
            "activity_type": row[2],
            "timestamp": row[3],
            "description": row[4],
            "ip_address": row[5],
            "resource_type": row[6],
            "resource_id": row[7]
        }


@router.put("/activity-logs/{log_id}/", response=UserActivityLogFullSchema)
def update_activity_log(request, log_id: int, payload: UserActivityLogUpdateSchema):
    with connection.cursor() as cursor:
        # Check if activity log exists
        cursor.execute("SELECT id FROM user_activity_logs WHERE id = %s", [log_id])
        if not cursor.fetchone():
            return HttpResponse(status=404, content=json.dumps({"detail": "Activity log not found"}))

        # Build update query dynamically based on provided fields
        update_fields = []
        params = []

        for field, value in payload.dict(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = %s")
                params.append(value)

        if not update_fields:
            # No fields to update, return current log
            cursor.execute(
                """
                SELECT id, user_id, activity_type, timestamp, description
                FROM user_activity_logs WHERE id = %s
                """,
                [log_id]
            )
            row = cursor.fetchone()
            return {
                "log_id": row[0],
                "user_id": row[1],
                "activity_type": row[2],
                "timestamp": row[3],
                "description": row[4],
                "ip_address": row[5],
                "resource_type": row[6],
                "resource_id": row[7]
            }

        # Add log_id to params for WHERE clause
        params.append(log_id)

        # Execute update query
        cursor.execute(
            f"""
            UPDATE user_activity_logs
            SET {", ".join(update_fields)}
            WHERE log_id = %s
            RETURNING log_id, user_id, activity_type, timestamp, description, ip_address, resource_type, resource_id
            """,
            params
        )

        row = cursor.fetchone()
        return {
            "log_id": row[0],
            "user_id": row[1],
            "activity_type": row[2],
            "timestamp": row[3],
            "description": row[4],
            "ip_address": row[5],
            "resource_type": row[6],
            "resource_id": row[7]
        }


@router.delete("/activity-logs/{log_id}/", response={204: None})
def delete_activity_log(request, log_id: int):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM user_activity_logs WHERE id = %s", [log_id])
        if not cursor.fetchone():
            return HttpResponse(status=404, content=json.dumps({"detail": "Activity log not found"}))

        cursor.execute("DELETE FROM user_activity_logs WHERE id = %s", [log_id])
        return 204, None