# app/api/schemas.py
from typing import Optional
from ninja import Schema


# app/api/vulnerabilities/schemas.py
from typing import Optional, List
from ninja import Schema
from datetime import date
from pydantic import Field


class VulnerabilitySchema(Schema):
    title: str = Field(..., description="Title of the vulnerability")
    description: str = Field(..., description="Detailed description of the vulnerability")
    severity: str = Field("Medium", description="Severity level of the vulnerability")
    cve_reference: str = Field("", description="CVE identifier reference")
    remediation_steps: str = Field("", description="Steps to remediate the vulnerability")
    discovery_date: Optional[date] = Field(None, description="Date when the vulnerability was discovered")
    patch_available: Optional[bool] = Field(False, description="Whether a patch is available for this vulnerability")



class VulnerabilityCreateSchema(Schema):
    title: str = Field(..., description="Title of the vulnerability")
    description: str = Field(..., description="Detailed description of the vulnerability")
    severity: str = Field("Medium", description="Severity level of the vulnerability")
    cve_reference: str = Field("", description="CVE identifier reference")
    remediation_steps: str = Field("", description="Steps to remediate the vulnerability")
    discovery_date: Optional[date] = Field(None, description="Date when the vulnerability was discovered")
    patch_available: Optional[bool] = Field(False, description="Whether a patch is available for this vulnerability")



class VulnerabilityUpdateSchema(Schema):
    title: Optional[str] = Field(None, description="Title of the vulnerability")
    description: Optional[str] = Field(None, description="Detailed description of the vulnerability")
    severity: Optional[str] = Field(None, description="Severity level of the vulnerability")
    cve_reference: Optional[str] = Field(None, description="CVE identifier reference")
    remediation_steps: Optional[str] = Field(None, description="Steps to remediate the vulnerability")
    discovery_date: Optional[date] = Field(None, description="Date when the vulnerability was discovered")
    patch_available: Optional[bool] = Field(None, description="Whether a patch is available for this vulnerability")

    class Config:
        update_exclude_none = True
