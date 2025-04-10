from typing import Optional, List

from ninja import Schema
from pydantic import Field


class ThreatIntelligenceSchema(Schema):
    threat_actor_name: str = Field(..., description="Name of the threat actor")
    indicator_type: str = Field(..., description="Type of the indicator")
    indicator_value: str = Field(..., description="Value of the indicator")
    confidence_level: str = Field(..., description="Confidence level of the threat intelligence")
    description: str = Field(..., description="Detailed description of the threat intelligence")
    related_cve: Optional[str] = Field(None, description="Related CVE identifier")

    threat_id: Optional[int] = Field(None, description="ID of the threat intelligence")

    class Config:
        input_exclude = {"threat_id"}


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


class ThreatIntelligenceDeleteResponseSchema(Schema):
    message: str = "Threat intelligence deleted successfully"