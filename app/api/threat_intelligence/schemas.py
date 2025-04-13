from datetime import datetime
from typing import Optional, List

from ninja import Schema
from pydantic import Field


class ThreatIntelligenceSchema(Schema):
    threat_id: Optional[int] = None
    threat_actor_name: str
    indicator_type: str
    indicator_value: str
    confidence_level: str
    description: str
    related_cve: Optional[str] = None
    date_identified: Optional[datetime] = None
    last_updated: Optional[datetime] = None

class ThreatAssetAssociationSchema(Schema):
    threat_id: int = Field(..., description="ID of the threat intelligence")
    asset_id: int = Field(..., description="ID of the associated asset")

class ThreatVulnerabilityAssociationSchema(Schema):
    threat_id: int = Field(..., description="ID of the threat intelligence")
    vulnerability_id: int = Field(..., description="ID of the associated vulnerability")

class ThreatIntelligenceListSchema(Schema):
    threats: List[ThreatIntelligenceSchema]
    count: int

class ThreatIntelligenceCreateResponseSchema(Schema):
    threat_id: int
    message: str = "Threat intelligence created successfully"

class ThreatIntelligenceUpdateResponseSchema(Schema):
    message: str = "Threat intelligence updated successfully"

class ThreatIntelligenceListResponseSchema(Schema):
    threats: List[ThreatIntelligenceSchema]
    count: int

class ThreatIntelligenceDeleteResponseSchema(Schema):
    pass

class ThreatIncidentAssociationSchema(Schema):
    threat_id: int
    incident_id: int
    notes: Optional[str] = None
