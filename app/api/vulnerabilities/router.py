from ninja import Router
from django.db import connection
from django.http import HttpResponse
from typing import List
import json

from app.api.vulnerabilities.schemas import VulnerabilitySchema, VulnerabilityCreateSchema, VulnerabilityUpdateSchema

router = Router(tags=["vulnerabilities"])


@router.get("/", response=List[VulnerabilitySchema])
def list_vulnerabilities(request):
    """Get all vulnerabilities"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT vulnerability_id, title, description, severity, cve_reference, remediation_steps, discovery_date, patch_available FROM api_vulnerability")
        vulnerabilities = []
        for row in cursor.fetchall():
            vulnerability = {
                "vulnerability_id": row[0],
                "title": row[1],
                "description": row[2],
                "severity": row[3],
                "cve_reference": row[4],
                "remediation_steps": row[5],
                "discovery_date": row[6],
                "patch_available": row[7],
            }
            vulnerabilities.append(vulnerability)
        return vulnerabilities

@router.post("/", response=VulnerabilitySchema)
def create_vulnerability(request, vulnerability_data: VulnerabilityCreateSchema):
    """Create a new vulnerability"""
    with connection.cursor() as cursor:
        # Check if vulnerability_name already exists
        cursor.execute(
            "SELECT vulnerability_id FROM api_vulnerability WHERE title = %s",
            [vulnerability_data.title]
        )
        if cursor.fetchone():
            return HttpResponse(
                status=400,
                content=json.dumps({"detail": "Vulnerability name already exists"})
            )

        # Insert new vulnerability
        cursor.execute(
            """
            INSERT INTO api_vulnerability (title, description, severity, cve_reference, remediation_steps, discovery_date, patch_available)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING vulnerability_id, title, description, severity, cve_reference, remediation_steps, discovery_date, patch_available
            """,
            [vulnerability_data.title, vulnerability_data.description, vulnerability_data.severity, vulnerability_data.cve_reference, vulnerability_data.remediation_steps, vulnerability_data.discovery_date, vulnerability_data.patch_available]
        )

        row = cursor.fetchone()
        vulnerability = {
            "vulnerability_id": row[0],
            "title": row[1],
            "description": row[2],
            "severity": row[3],
            "cve_reference": row[4],
            "remediation_steps": row[5],
            "discovery_date": row[6],
            "patch_available": row[7],
        }
        return vulnerability

@router.get("/{vulnerability_id}", response=VulnerabilitySchema)
def get_vulnerability(request, vulnerability_id: int):
    """Get vulnerability by ID"""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT vulnerability_id, title, description, severity, cve_reference, remediation_steps, discovery_date, patch_available FROM api_vulnerability WHERE vulnerability_id = %s",
            [vulnerability_id]
        )
        row = cursor.fetchone()
        if not row:
            return HttpResponse(status=404, content=json.dumps({"detail": "Vulnerability not found"}))

        vulnerability = {
            "vulnerability_id": row[0],
            "title": row[1],
            "description": row[2],
            "severity": row[3],
            "cve_reference": row[4],
            "remediation_steps": row[5],
            "discovery_date": row[6],
            "patch_available": row[7],
        }
        return vulnerability

@router.put("/{vulnerability_id}", response=VulnerabilitySchema)
def update_vulnerability(request, vulnerability_id: int, vulnerability_data: VulnerabilityUpdateSchema):
    """Update an existing vulnerability"""
    with connection.cursor() as cursor:
        # Check if vulnerability exists
        cursor.execute("SELECT vulnerability_id FROM api_vulnerability WHERE vulnerability_id = %s", [vulnerability_id])
        if not cursor.fetchone():
            return HttpResponse(status=404, content=json.dumps({"detail": "Vulnerability not found"}))

        # Build update query dynamically based on provided fields
        update_fields = []
        params = []

        if vulnerability_data.description:
            update_fields.append("description = %s")
            params.append(vulnerability_data.description)

        if vulnerability_data.severity:
            update_fields.append("severity = %s")
            params.append(vulnerability_data.severity)

        if vulnerability_data.cve_reference:
            update_fields.append("cve_reference = %s")
            params.append(vulnerability_data.cve_reference)

        if vulnerability_data.remediation_steps:
            update_fields.append("remediation_steps = %s")
            params.append(vulnerability_data.remediation_steps)

        if vulnerability_data.discovery_date:
            update_fields.append("discovery_date = %s")
            params.append(vulnerability_data.discovery_date)

        if vulnerability_data.patch_available:
            update_fields.append("patch_available = %s")
            params.append(vulnerability_data.patch_available)

        if not update_fields:
            # If no fields to update, just return the current vulnerability
            cursor.execute(
                "SELECT vulnerability_id, title, description, severity, cve_reference, remediation_steps, discovery_date, patch_available FROM api_vulnerability WHERE vulnerability_id = %s",
                [vulnerability_id]
            )
            row = cursor.fetchone()
            vulnerability = {
                "vulnerability_id": row[0],
                "title": row[1],
                "description": row[2],
                "severity": row[3],
                "cve_reference": row[4],
                "remediation_steps": row[5],
                "discovery_date": row[6],
                "patch_available": row[7],
            }
            return vulnerability

        # Add vulnerability_id to params for WHERE clause
        params.append(vulnerability_id)

        # Execute update query
        cursor.execute(
            f"""
            UPDATE api_vulnerability
            SET {", ".join(update_fields)}
            WHERE vulnerability_id = %s
            RETURNING vulnerability_id, title, description, severity, cve_reference, remediation_steps, discovery_date, patch_available
            """,
            params
        )

        row = cursor.fetchone()
        vulnerability = {
            "vulnerability_id": row[0],
            "title": row[1],
            "description": row[2],
            "severity": row[3],
            "cve_reference": row[4],
            "remediation_steps": row[5],
            "discovery_date": row[6],
            "patch_available": row[7],
        }
        return vulnerability

@router.delete("/{vulnerability_id}")
def delete_vulnerability(request, vulnerability_id: int):
    """Delete a vulnerability"""
    with connection.cursor() as cursor:
        # Check if vulnerability exists
        cursor.execute("SELECT vulnerability_id FROM api_vulnerability WHERE vulnerability_id = %s", [vulnerability_id])
        if not cursor.fetchone():
            return HttpResponse(status=404, content=json.dumps({"detail": "Vulnerability not found"}))

        # Delete vulnerability
        cursor.execute("DELETE FROM api_vulnerability WHERE vulnerability_id = %s", [vulnerability_id])
        return {"success": True}