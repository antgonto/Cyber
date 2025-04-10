from datetime import date
from typing import Optional
from ninja import Schema
from pydantic import Field

class AssetSchema(Schema):
    asset_id: int = Field(..., description="Unique identifier for the asset")
    asset_name: str = Field(..., description="Name of the asset")
    asset_type: str = Field(..., description="Type or category of the asset")
    location: Optional[str] = Field(None, description="Physical or logical location of the asset")
    owner: Optional[int] = Field(None, description="ID of the owner/responsible person for this asset")
    criticality_level: str = Field(..., description="Level of criticality for the asset")

    class Config:
        input_exclude = {"asset_id"}

class AssetCreateSchema(Schema):
    asset_name: str = Field(..., description="Name of the asset")
    asset_type: str = Field(..., description="Type or category of the asset")
    location: Optional[str] = Field(None, description="Physical or logical location of the asset")
    owner: Optional[int] = Field(None, description="ID of the owner/responsible person for this asset")
    criticality_level: str = Field(..., description="Level of criticality for the asset")

class AssetUpdateSchema(Schema):
    asset_name: Optional[str] = Field(None, description="Name of the asset")
    asset_type: Optional[str] = Field(None, description="Type or category of the asset")
    location: Optional[str] = Field(None, description="Physical or logical location of the asset")
    owner: Optional[int] = Field(None, description="ID of the owner/responsible person for this asset")
    criticality_level: Optional[str] = Field(None, description="Level of criticality for the asset")

    class Config:
        update_exclude_none = True

class AssetVulnerabilitySchema(Schema):
    asset_id: int = Field(..., description="ID of the asset")
    vulnerability_id: int = Field(..., description="ID of the vulnerability")
    status: str = Field(..., description="Status of the asset vulnerability")
    date_discovered: Optional[date] = Field(None, description="Date when the vulnerability was discovered")

    class Config:
        input_exclude = {"date_discovered"}