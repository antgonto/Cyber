from datetime import datetime
from typing import Optional, List

from ninja import Schema
from pydantic import Field


class ThreatIntelligenceSchema(Schema):
    threat_id: Optional[int] = Field(None, description="Unique identifier of the threat")
    threat_actor_name: str = Field(..., description="Name of the threat actor")
    indicator_type: str = Field(..., description="Type of threat indicator")
    indicator_value: str = Field(..., description="Value of the threat indicator")
    confidence_level: str = Field(..., description="Confidence level of the threat intelligence")
    description: str = Field(..., description="Description of the threat")
    related_cve: Optional[str] = Field(None, description="Related CVE identifier")
    date_identified: Optional[datetime] = Field(default_factory=datetime.now, description="Date when threat was identified")
    last_updated: Optional[datetime] = Field(default_factory=datetime.now, description="Date when threat was last updated")
    assets: Optional[List[int]] = Field(None, description="List of associated asset IDs")
    vulnerabilities: Optional[List[int]] = Field(None, description="List of associated vulnerability IDs")
    incidents: Optional[List[int]] = Field(None, description="List of associated incident IDs")



class ThreatAssetAssociationSchema(Schema):
    threat_id: int = Field(..., description="ID of the threat intelligence")
    asset_id: int = Field(..., description="ID of the associated asset")
    notes: Optional[str] = Field(None, description="Additional notes about the association")


class ThreatVulnerabilityAssociationSchema(Schema):
    threat_id: int = Field(..., description="ID of the threat intelligence")
    vulnerability_id: int = Field(..., description="ID of the associated vulnerability")
    notes: Optional[str] = Field(None, description="Additional notes about the association")


class ThreatIntelligenceListSchema(Schema):
    threats: List[ThreatIntelligenceSchema] = Field(..., description="List of threat intelligence items")
    count: int = Field(..., description="Total count of threat intelligence items")

class ThreatIntelligenceCreateResponseSchema(Schema):
    threat_id: int = Field(..., description="ID of the created threat intelligence")
    message: str = Field("Threat intelligence created successfully", description="Success message")

class ThreatIntelligenceUpdateResponseSchema(Schema):
    message: str = Field("Threat intelligence updated successfully", description="Success message")

class ThreatIntelligenceListResponseSchema(Schema):
    threats: List[ThreatIntelligenceSchema] = Field(..., description="List of threat intelligence items")
    count: int = Field(..., description="Total count of threat intelligence items")

class ThreatIntelligenceDeleteResponseSchema(Schema):
    message: str = Field("Threat intelligence deleted successfully", description="Success message")


class ThreatIncidentAssociationSchema(Schema):
    threat_id: int = Field(..., description="ID of the threat intelligence")
    incident_id: int = Field(..., description="ID of the associated incident")
    notes: Optional[str] = Field(None, description="Additional notes about the association")


class ThreatAssetAssociationResponseSchema(Schema):
    association_id: int = Field(..., description="ID of the association")
    threat_id: int = Field(..., description="ID of the threat intelligence")
    asset_id: int = Field(..., description="ID of the associated asset")
    date_associated: str = Field(..., description="Date when the association was created")
