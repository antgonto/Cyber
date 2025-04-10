# Django Ninja Schemas
from ninja import Schema
from typing import List, Optional
from datetime import datetime
from pydantic import Field

from app.api.alerts.schemas import AlertSchema
from app.api.threat_intelligence.schemas import ThreatIntelligenceSchema


class IncidentSchema(Schema):
    incident_id: Optional[int] = Field(None, description="ID of the incident")
    incident_type: str = Field(..., description="Type of the incident")
    description: str = Field(..., description="Detailed description of the incident")
    severity: str = Field(..., description="Severity level of the incident")
    status: Optional[str] = Field("open", description="Current status of the incident")
    assigned_to_id: Optional[int] = Field(None, description="User ID of the assignee")
    reported_date: Optional[datetime] = Field(None, description="Date when the incident was reported")
    resolved_date: Optional[datetime] = Field(None, description="Date when the incident was resolved")

    class Config:
        input_exclude = {"incident_id", "reported_date", "resolved_date"}
        update_include = {"incident_type", "description", "severity", "status", "resolved_date", "assigned_to_id"}
        update_exclude_none = True


class IncidentAssetSchema(Schema):
    incident_id: int = Field(..., description="ID of the incident")
    asset_id: int = Field(..., description="ID of the asset")
    impact_level: str = Field(..., description="Impact level of the asset in the incident")


# List response schemas
class IncidentListSchema(Schema):
    incidents: List[IncidentSchema]
    count: int


class ThreatIncidentAssociationSchema(Schema):
    threat_id: int = Field(..., description="ID of the threat intelligence")
    incident_id: int = Field(..., description="ID of the associated incident")
    notes: Optional[str] = Field(None, description="Additional notes about the association")



class IncidentDetailSchema(IncidentSchema):
    assets: List[IncidentAssetSchema] = Field([], description="Assets affected by this incident")
    alerts: List[AlertSchema] = Field([], description="Alerts associated with this incident")
    threats: List[ThreatIntelligenceSchema] = Field([], description="Threats related to this incident")


class IncidentCreateResponseSchema(Schema):
    incident_id: int
    message: str = "Incident created successfully"


class IncidentUpdateResponseSchema(Schema):
    message: str = "Incident updated successfully"


class IncidentDeleteResponseSchema(Schema):
    message: str = "Incident deleted successfully"
