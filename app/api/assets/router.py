from ninja import Router
from django.db import connection
from django.http import HttpResponse
from typing import List
import json
from .schemas import AssetSchema, AssetCreateSchema, AssetUpdateSchema

router = Router()


@router.get("/", response=List[AssetSchema])
def list_assets(request):
    """Get all assets"""
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT asset_id, asset_name, asset_type, location, owner, criticality_level FROM api_asset")
        assets = []
        for row in cursor.fetchall():
            asset = {
                "asset_id": row[0],
                "asset_name": row[1],
                "asset_type": row[2],
                "location": row[3],
                "owner": row[4],
                "criticality_level": row[5],
            }
            assets.append(asset)
        return assets


@router.get("/{asset_id}", response=AssetSchema)
def get_asset(request, asset_id: int):
    """Get asset by ID"""
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT asset_id, asset_name, asset_type, location, owner, criticality_level FROM api_asset WHERE user_id = %s",
            [asset_id]
        )
        row = cursor.fetchone()
        if not row:
            return HttpResponse(status=404, content=json.dumps({"detail": "Asset not found"}))

        asset = {
            "asset_id": row[0],
            "asset_name": row[1],
            "asset_type": row[2],
            "location": row[3],
            "owner": row[4],
            "criticality_level": row[5],
        }
        return asset


@router.post("/", response=AssetSchema)
def create_asset(request, asset_data: AssetCreateSchema):
    """Create a new asset"""
    with connection.cursor() as cursor:
        # Check if asset_name already exists
        cursor.execute(
            "SELECT asset_id FROM api_asset WHERE asset_name = %s",
            [asset_data.asset_name]
        )
        if cursor.fetchone():
            return HttpResponse(
                status=400,
                content=json.dumps({"detail": "Asset name already exists"})
            )

        # Insert new asset
        cursor.execute(
            """
            INSERT INTO api_asset (asset_name, asset_type, location, owner, criticality_level)
            VALUES (%s, %s, %s, %s)
            RETURNING asset_id, asset_name, asset_type, location, owner, criticality_level
            """,
            [asset_data.asset_name, asset_data.asset_type, asset_data.location, asset_data.owner, asset_data.criticality_level]
        )

        row = cursor.fetchone()
        asset = {
            "asset_id": row[0],
            "asset_name": row[1],
            "asset_type": row[2],
            "location": row[3],
            "owner": row[4],
            "criticality_level": row[5],
        }
        return asset


@router.put("/{asset_id}", response=AssetSchema)
def update_asset(request, asset_id: int, asset_data: AssetUpdateSchema):
    """Update an existing asset"""
    with connection.cursor() as cursor:
        # Check if asset exists
        cursor.execute("SELECT asset_id FROM api_asset WHERE asset_id = %s", [asset_id])
        if not cursor.fetchone():
            return HttpResponse(status=404, content=json.dumps({"detail": "Asset not found"}))

        # Build update query dynamically based on provided fields
        update_fields = []
        params = []

        if asset_data.asset_name:
            update_fields.append("asset_name = %s")
            params.append(asset_data.asset_name)

        if asset_data.asset_type:
            update_fields.append("asset_type = %s")
            params.append(asset_data.asset_name)

        if asset_data.location:
            update_fields.append("location = %s")
            params.append(asset_data.location)

        if asset_data.owner:
            update_fields.append("owner = %s")
            params.append(asset_data.owner)

        if asset_data.criticality_level:
            update_fields.append("criticality_level = %s")
            params.append(asset_data.criticality_level)

        if not update_fields:
            # If no fields to update, just return the current asset
            cursor.execute(
                f"SELECT asset_id, asset_name, asset_type, location, owner, criticality_level FROM api_asset WHERE user_id = %s",
                [asset_id]
            )
            row = cursor.fetchone()
            asset = {
                "asset_id": row[0],
                "asset_name": row[1],
                "asset_type": row[2],
                "location": row[3],
                "owner": row[4],
                "criticality_level": row[5],
            }
            return asset

        # Add asset_id to params for WHERE clause
        params.append(asset_id)

        # Execute update query
        cursor.execute(
            f"""
            UPDATE api_asset 
            SET {", ".join(update_fields)}
            WHERE asset_id = %s
            RETURNING asset_id, asset_name, asset_type, location, owner, criticality_level            
            """,
            params
        )

        row = cursor.fetchone()
        asset = {
            "asset_id": row[0],
            "asset_name": row[1],
            "asset_type": row[2],
            "location": row[3],
            "owner": row[4],
            "criticality_level": row[5],
        }
        return asset


@router.delete("/{asset_id}")
def delete_asset(request, asset_id: int):
    """Delete a asset"""
    with connection.cursor() as cursor:
        # Check if asset exists
        cursor.execute("SELECT asset_id FROM api_asset WHERE asset_id = %s", [asset_id])
        if not cursor.fetchone():
            return HttpResponse(status=404, content=json.dumps({"detail": "Asset not found"}))

        # Delete asset
        cursor.execute("DELETE FROM api_asset WHERE asset_id = %s", [asset_id])
        return {"success": True}