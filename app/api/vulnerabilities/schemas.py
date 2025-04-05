# app/api/schemas.py
from typing import Optional
from ninja import Schema


class VulnerabilitySchema(Schema):
    vulnerability_id: int
    title: str
    description: str
    severity: str
    cve_reference: str
    remediation_steps: str


class VulnerabilityCreateSchema(Schema):
    title: str
    description: str
    severity: str
    cve_reference: str
    remediation_steps: str

class VulnerabilityUpdateSchema(Schema):
    title: str
    description: str
    severity: str
    cve_reference: str
    remediation_steps: str