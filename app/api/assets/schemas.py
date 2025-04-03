# app/api/schemas.py
from typing import Optional
from ninja import Schema


class AssetSchema(Schema):
    asset_id: int
    asset_name: str
    asset_type: str
    location: Optional[str] = None
    owner: Optional[int] = None
    criticality_level: str


class AssetCreateSchema(Schema):
    asset_name: str
    asset_type: str
    location: Optional[str] = None
    owner: Optional[int] = None
    criticality_level: str


class AssetUpdateSchema(Schema):
    asset_name: Optional[str] = None
    asset_type: Optional[str] = None
    location: Optional[str] = None
    owner: Optional[int] = None
    criticality_level: Optional[str] = None
    role: Optional[str] = None