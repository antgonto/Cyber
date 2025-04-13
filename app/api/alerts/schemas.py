from typing import Optional, List
from datetime import datetime
from enum import Enum
from ninja import Schema
from pydantic import Field, field_validator, model_validator


class SeverityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @classmethod
    def _missing_(cls, value):
        # Allow case-insensitive lookup
        for member in cls:
            if isinstance(value, str) and member.value.lower() == value.lower():
                return member
        return None


class StatusEnum(str, Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CLOSED = "closed"

    @classmethod
    def _missing_(cls, value):
        # Allow case-insensitive lookup
        for member in cls:
            if isinstance(value, str) and member.value.lower() == value.lower():
                return member
        return None




class AlertSchema(Schema):
    alert_id: Optional[int] = Field(None, description="ID of the alert")
    source: str = Field(..., description="Source of the alert", min_length=1, max_length=255)
    name: str = Field(..., description="Name of the alert", min_length=1, max_length=255)
    alert_type: str = Field(..., description="Type of the alert", min_length=1, max_length=100, alias="type")
    alert_time: Optional[datetime] = Field(None, description="Time when the alert was created")
    severity: SeverityEnum = Field(..., description="Severity level of the alert")
    status: StatusEnum = Field(StatusEnum.NEW, description="Current status of the alert")
    incident_id: Optional[int] = Field(None, description="ID of the associated incident")


    @field_validator('source', 'alert_type')
    def validate_non_empty_string(cls, value):
        if not value.strip():
            raise ValueError("Field cannot be empty or just whitespace")
        return value

    @model_validator(mode="after")
    def enforce_incident_if_critical(self):
        if self.severity == SeverityEnum.CRITICAL and not self.incident_id:
            raise ValueError("Incident ID must be provided for critical alerts.")
        return self

    model_config = {
        "json_exclude_none": True,
        "populate_by_name": True,
        "json_schema_extra": {
            "input_exclude": ["alert_id", "alert_time"],
            "update_include": ["source", "alert_type", "severity", "status", "incident_id"]
        }
    }

class AlertListSchema(Schema):
    alerts: List[AlertSchema]
    count: int