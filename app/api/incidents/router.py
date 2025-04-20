# app/api/incidents/router.py
import json
from datetime import datetime
from typing import Optional

from django.db import connection
from django.http import HttpResponse, Http404
from ninja import Router
from .schemas import (
    IncidentSchema,
    IncidentAssetSchema,
    IncidentDetailSchema,
    IncidentUpdateResponseSchema,
    IncidentDeleteResponseSchema,
    ThreatIncidentAssociationSchema
)
from ..schemas import ErrorSchema

router = Router(tags=["incidents"])

@router.get("/", response=list[IncidentDetailSchema])
def list_detailed_incidents(
        request,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        incident_type: Optional[str] = None,
        assigned_to_id: Optional[int] = None
):
    """List all incidents with detailed information and optional filtering"""
    results = []

    with connection.cursor() as cursor:
        # Build WHERE clause for filters
        where_clauses = []
        params = []

        if status:
            where_clauses.append("i.status = %s")
            params.append(status)
        if severity:
            where_clauses.append("i.severity = %s")
            params.append(severity)
        if incident_type:
            where_clauses.append("i.incident_type LIKE %s")
            params.append(f"%{incident_type}%")
        if assigned_to_id:
            where_clauses.append("i.assigned_to_id = %s")
            params.append(assigned_to_id)

        where_clause = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Get basic incident information
        cursor.execute(
            f"""
            SELECT i.incident_id, i.incident_type, i.description, i.severity, i.status,
                   i.reported_date, i.resolved_date, i.assigned_to_id, u.username
            FROM api_incident i
            LEFT JOIN api_user u ON i.assigned_to_id = u.user_id
            {where_clause}
            ORDER BY i.reported_date DESC
            """,
            params
        )

        incidents = cursor.fetchall()

        for inc in incidents:
            incident_id = inc[0]

            # Get related alerts
            cursor.execute(
                """
                SELECT alert_id, source, name, alert_type, alert_time, severity, status
                FROM api_alert
                WHERE incident_id = %s
                """,
                [incident_id]
            )
            alerts = [
                {
                    "alert_id": row[0],
                    "source": row[1],
                    "name": row[2],
                    "alert_type": row[3],
                    "alert_time": row[4],
                    "severity": row[5],
                    "status": row[6] if row[6] in ['new', 'acknowledged', 'resolved', 'closed'] else 'new',
                    "incident_id": incident_id
                }
                for row in cursor.fetchall()
            ]

            # Get related threats
            cursor.execute(
                """
                SELECT ti.threat_id, ti.threat_actor_name, ti.indicator_type,
                       ti.indicator_value, ti.confidence_level, ti.description, ti.related_cve
                FROM api_threatintelligence ti
                JOIN threat_incident_association tia ON ti.threat_id = tia.threat_id
                WHERE tia.incident_id = %s
                """,
                [incident_id]
            )
            threats = [
                {
                    "threat_id": row[0],
                    "threat_actor_name": row[1],
                    "indicator_type": row[2],
                    "indicator_value": row[3],
                    "confidence_level": row[4],
                    "description": row[5],
                    "related_cve": row[6]
                }
                for row in cursor.fetchall()
            ]

            # Get related assets
            cursor.execute(
                """
                SELECT a.asset_id, a.asset_name, a.asset_type, a.location, a.owner, a.criticality_level
                FROM api_asset a
                JOIN incident_assets ia ON a.asset_id = ia.asset_id
                WHERE ia.incident_id = %s
                """,
                [incident_id]
            )
            assets = [
                {
                    "asset_id": row[0],
                    "asset_name": row[1],
                    "asset_type": row[2],
                    "location": row[3],
                    "owner": row[4],
                    "criticality_level": row[5]
                }
                for row in cursor.fetchall()
            ]

            # Combine all data into a single incident record
            incident = {
                "incident_id": inc[0],
                "incident_type": inc[1],
                "description": inc[2],
                "severity": inc[3],
                "status": inc[4],
                "reported_date": inc[5],
                "resolved_date": inc[6],
                "assigned_to_id": inc[7],
                "assigned_to_username": inc[8] if inc[7] else None,
                "alerts": alerts,
                "threats": threats,
                "assets": assets
            }

            results.append(incident)

    return results
@router.post("/", response=IncidentSchema)
def create_incident(request, incident: IncidentSchema):
    """Create a new incident"""
    with connection.cursor() as cursor:
        # Validate assigned_to user if provided
        if incident.assigned_to_id:
            cursor.execute("SELECT user_id FROM api_user WHERE user_id = %s", [incident.assigned_to_id])
            if not cursor.fetchone():
                return HttpResponse(
                    status=400,
                    content=json.dumps({"detail": "Referenced user not found"})
                )

        # Use current timestamp for reported_date
        cursor.execute(
            """
            INSERT INTO api_incident (
                incident_type, description, severity, status, 
                reported_date, resolved_date, assigned_to_id
            )
            VALUES (%s, %s, %s, %s, NOW(), %s, %s)
            RETURNING incident_id, incident_type, description, severity, status, 
                      reported_date, resolved_date, assigned_to_id
            """,
            [
                incident.incident_type,
                incident.description,
                incident.severity,
                incident.status or 'open',
                incident.resolved_date,
                incident.assigned_to_id
            ]
        )
        row = cursor.fetchone()

        # If assigned_to is not None, fetch the username
        username = None
        if row[7]:  # assigned_to
            cursor.execute("SELECT username FROM api_user WHERE user_id = %s", [row[7]])
            user_row = cursor.fetchone()
            username = user_row[0] if user_row else None

        incident = {
            "incident_id": row[0],
            "incident_type": row[1],
            "description": row[2],
            "severity": row[3],
            "status": row[4],
            "reported_date": row[5],
            "resolved_date": row[6],
            "assigned_to_id": row[7],
            "assigned_to_username": username
        }

    return incident

@router.get("/{incident_id}/", response=IncidentDetailSchema)
def get_incident(request, incident_id: int):
    """Get incident by ID with related alerts and user details"""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT i.incident_id, i.incident_type, i.description, i.severity, i.status, 
                   i.reported_date, i.resolved_date, i.assigned_to_id, u.username
            FROM api_incident i
            LEFT JOIN api_user u ON i.assigned_to_id = u.user_id
            WHERE i.incident_id = %s
            """,
            [incident_id]
        )
        row = cursor.fetchone()
        if not row:
            return HttpResponse(
                status=404,
                content=json.dumps({"detail": "Incident not found"})
            )

        # Get related alerts
        cursor.execute(
            """
            SELECT alert_id, source, name, alert_type, alert_time, severity, status
            FROM api_alert
            WHERE incident_id = %s
            """,
            [incident_id]
        )
        alert_rows = cursor.fetchall()

        alerts = [
            {
                "alert_id": row[0],
                "source": row[1],
                "name": row[2],
                "alert_type": row[3],
                "alert_time": row[4],
                "severity": row[5],
                "status": row[6] if row[6] in ['new', 'acknowledged', 'resolved', 'closed'] else 'new',
                # Map invalid status to valid status
                "incident_id": incident_id
            }
            for row in alert_rows
        ]

        # Get related threat intelligence
        cursor.execute(
            """
            SELECT ti.threat_id, ti.threat_actor_name, ti.indicator_type, 
                   ti.indicator_value, ti.confidence_level, ti.description, ti.related_cve
            FROM api_threatintelligence ti
            JOIN threat_incident_association tia ON ti.threat_id = tia.threat_id
            WHERE tia.incident_id = %s
            """,
            [incident_id]
        )
        threat_rows = cursor.fetchall()

        threats = [
            {
                "threat_id": row[0],
                "threat_actor_name": row[1],
                "indicator_type": row[2],
                "indicator_value": row[3],
                "confidence_level": row[4],
                "description": row[5],
                "related_cve": row[6]
            }
            for row in threat_rows
        ]

        # Get related assets
        cursor.execute(
            """
            SELECT a.asset_id, a.asset_name, a.asset_type, a.location, a.owner, a.criticality_level, ia.impact_level
            FROM api_asset a
            JOIN incident_assets ia ON a.asset_id = ia.asset_id
            WHERE ia.incident_id = %s
            """,
            [incident_id]
        )
        asset_rows = cursor.fetchall()

        assets = [
            {
                "asset_id": row[0],
                "asset_name": row[1],
                "asset_type": row[2],
                "location": row[3],
                "owner": row[4],
                "criticality_level": row[5]
            }
            for row in asset_rows
        ]

        incident = {
            "incident_id": row[0],
            "incident_type": row[1],
            "description": row[2],
            "severity": row[3],
            "status": row[4],
            "reported_date": row[5],
            "resolved_date": row[6],
            "assigned_to_id": row[7],
            "assigned_to_username": row[8] if row[7] else None,
            "alerts": alerts,
            "threats": threats,
            "assets": assets
        }

        return incident

@router.put("/{incident_id}/", response=IncidentUpdateResponseSchema)
def update_incident(request, incident_id: int, incident_data: IncidentSchema):

    # Check if incident exists
    with connection.cursor() as cursor:
        cursor.execute("SELECT incident_id FROM api_incident WHERE incident_id = %s", [incident_id])
        if not cursor.fetchone():
            return HttpResponse(
                status=404,
                content=json.dumps({"detail": "Incident not found"})
            )

        # Automatically set resolved_date when status changes to resolved
        if incident_data.status == 'resolved':
            cursor.execute("SELECT status FROM api_incident WHERE incident_id = %s", [incident_id])
            current_status = cursor.fetchone()[0]  # Access the first element of the tuple
            if current_status != 'resolved':
                # Status is changing to resolved, set resolved_date to now
                incident_data.resolved_date = datetime.now()

        # Validate assigned_to user if provided
        if incident_data.assigned_to_id is not None:
            cursor.execute("SELECT user_id FROM api_user WHERE user_id = %s", [incident_data.assigned_to_id])
            if not cursor.fetchone():
                return HttpResponse(
                    status=400,
                    content=json.dumps({"detail": "Referenced user not found"})
                )

        # Build update query dynamically based on provided fields
        update_fields = []
        params = []

        if incident_data.incident_type:
            update_fields.append("incident_type = %s")
            params.append(incident_data.incident_type)

        if incident_data.description:
            update_fields.append("description = %s")
            params.append(incident_data.description)

        if incident_data.severity:
            update_fields.append("severity = %s")
            params.append(incident_data.severity)

        if incident_data.status:
            update_fields.append("status = %s")
            params.append(incident_data.status)

        if incident_data.reported_date:
            update_fields.append("reported_date = %s")
            params.append(incident_data.reported_date)

        if incident_data.resolved_date:
            update_fields.append("resolved_date = %s")
            params.append(incident_data.resolved_date)

        if incident_data.assigned_to_id is not None:  # Allow setting to None (unassigning)
            update_fields.append("assigned_to_id = %s")
            params.append(incident_data.assigned_to_id)

        # Build SQL update
        if not update_fields:
            # If no fields to update, just return the current incident
            return get_incident(request, incident_id)

        # Combine params with incident_id
        params.append(incident_id)

        # Execute update query
        cursor.execute(
            f"""
             UPDATE api_incident
             SET {", ".join(update_fields)}
             WHERE incident_id = %s
             """,
            params
        )

    return {"message": "Incident updated successfully"}


@router.delete("/{incident_id}/", response=IncidentDeleteResponseSchema)
def delete_incident(request, incident_id: int):
    """Delete an incident"""
    # Check if incident exists and delete it
    with connection.cursor() as cursor:
        cursor.execute("SELECT incident_id FROM api_incident WHERE incident_id = %s", [incident_id])
        row = cursor.fetchone()
        if not row:
            return HttpResponse(
                status=404,
                content=json.dumps({"detail": "Incident not found"})
            )

        # Delete related associations first to maintain referential integrity
        cursor.execute("DELETE FROM incident_assets WHERE incident_id = %s", [incident_id])
        cursor.execute("DELETE FROM threat_incident_association WHERE incident_id = %s", [incident_id])
        cursor.execute("UPDATE api_alert SET incident_id = NULL WHERE incident_id = %s", [incident_id])

        # Now delete the incident
        cursor.execute("DELETE FROM api_incident WHERE incident_id = %s", [incident_id])

    return {"message": "Incident deleted successfully"}


@router.get("/assets/{incident_id}/", response={200: list[IncidentAssetSchema], 400: ErrorSchema})
def get_assets_from_incident(request, incident_id: int):

    assets = []

    # Verify incident exists
    with connection.cursor() as cursor:
        cursor.execute("SELECT incident_id FROM api_incident WHERE incident_id = %s", [incident_id])
        if not cursor.fetchone():
            return HttpResponse(
                status=404,
                content=json.dumps({"detail": "Incident not found"})
            )

        # Get all assets for the incident
        cursor.execute(
            """
            SELECT incident_id, asset_id, impact_level 
            FROM incident_assets  
            WHERE incident_id = %s
            """,
            [incident_id]
        )

        for row in cursor.fetchall():
            assets.append({
                "incident_id": row[0],
                "asset_id": row[1],
                "impact_level": row[2]
            })

    return assets

@router.post("/assets/", response={201: IncidentAssetSchema, 400: ErrorSchema})
def add_asset_to_incident(request, incident_asset_data: IncidentAssetSchema):
    # Verify incident exists
    with connection.cursor() as cursor:
        # Check if association already exists
        cursor.execute(
            "SELECT incident_id FROM incident_assets WHERE incident_id = %s AND asset_id = %s",
            [incident_asset_data.incident_id, incident_asset_data.asset_id]
        )

        if cursor.fetchone():
            return HttpResponse(
                status=400,
                content=json.dumps({"detail": "Asset already associated with this incident"})
            )

        # Validate that the incident and asset exist
        cursor.execute("SELECT incident_id FROM api_incident WHERE incident_id = %s",
                       [incident_asset_data.incident_id])
        if not cursor.fetchone():
            return HttpResponse(
                status=400,
                content=json.dumps({"detail": "Referenced incident not found"})
            )

        # Verify asset exists
        cursor.execute("SELECT asset_id FROM api_asset WHERE asset_id = %s",
                       [incident_asset_data.asset_id])
        if not cursor.fetchone():
            return HttpResponse(
                status=400,
                content=json.dumps({"detail": "Referenced asset not found"})
            )

        # Create new association
        cursor.execute("""
            INSERT INTO incident_assets (incident_id, asset_id, impact_level) VALUES (%s, %s, %s)
            RETURNING id, incident_id, asset_id, impact_level
            """,
        [incident_asset_data.incident_id, incident_asset_data.asset_id, incident_asset_data.impact_level]
        )

    return incident_asset_data

@router.put("/assets/", response={200: IncidentAssetSchema, 404: ErrorSchema, 400: ErrorSchema})
def update_asset_in_incident(request, incident_asset_data: IncidentAssetSchema,
                          original_incident_id: Optional[int] = None,
                          original_asset_id: Optional[int] = None):

    with connection.cursor() as cursor:
        # Verify the original association exists
        cursor.execute(
            "SELECT incident_id FROM incident_assets WHERE incident_id = %s AND asset_id = %s",
            [original_incident_id, original_asset_id]
        )

        if not cursor.fetchone():
            return HttpResponse(
                status=404,
                content=json.dumps({"detail": "Original asset association not found"})
            )

        # Verify that the incident and asset exist
        cursor.execute("SELECT incident_id FROM api_incident WHERE incident_id = %s",
                       [incident_asset_data.incident_id])

        if not cursor.fetchone():
            return HttpResponse(
                status=400,
                content=json.dumps({"detail": "Referenced incident not found"})
            )

        cursor.execute("SELECT asset_id FROM api_asset WHERE asset_id = %s",
                       [incident_asset_data.asset_id])
        if not cursor.fetchone():
            return HttpResponse(
                status=400,
                content=json.dumps({"detail": "Referenced asset not found"})
            )

        # Check if we're updating an existing association
        if ((original_incident_id != incident_asset_data.incident_id) or (original_asset_id != incident_asset_data.asset_id)):
            # Update the association (either same pair with new impact_level or completely new pair)
            cursor.execute(
                """DELETE FROM incident_assets WHERE incident_id = %s AND asset_id = %s""",
                [original_incident_id, original_asset_id]
            )
            # Update the association (either same pair with new data or a completely new pair)
            cursor.execute(
                """INSERT INTO incident_assets (incident_id, asset_id, impact_level) 
                   VALUES (%s, %s, %s)""",
                [incident_asset_data.incident_id, incident_asset_data.asset_id,
                 incident_asset_data.impact_level]
            )
        else:
            # Just update impact_level for existing association
            cursor.execute(
                "SELECT incident_id FROM incident_assets WHERE incident_id = %s AND asset_id = %s",
                [incident_asset_data.incident_id, incident_asset_data.asset_id]
            )
            if not cursor.fetchone():
                return HttpResponse(
                    status=404,
                    content=json.dumps({"detail": "Asset association not found"})
                )

            # Update just the impact level
            cursor.execute(
                "UPDATE incident_assets SET impact_level = %s WHERE incident_id = %s AND asset_id = %s",
                [incident_asset_data.impact_level, incident_asset_data.incident_id, incident_asset_data.asset_id]
            )

    return incident_asset_data

@router.delete("/assets/{incident_id}/{asset_id}/", response={200: dict, 404: ErrorSchema})
def remove_asset_from_incident(request, incident_id: int, asset_id: int):
    # Check if association exists
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT incident_id FROM incident_assets WHERE incident_id = %s AND asset_id = %s",
            [incident_id, asset_id]
        )
        if not cursor.fetchone():
            return HttpResponse(
                status=404,
                content=json.dumps({"detail": "Asset association not found"})
            )

        # Delete the association
        cursor.execute(
            "DELETE FROM incident_assets WHERE incident_id = %s AND asset_id = %s",
            [incident_id, asset_id]
        )

    return {"success": True}

@router.get("/threats/{incident_id}/", response=list[ThreatIncidentAssociationSchema])
def get_threats_by_incident(request, incident_id: int):
    """Get all threat associations for an incident"""
    associations = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT incident_id FROM api_incident WHERE incident_id = %s", [incident_id])
        if not cursor.fetchone():
            return HttpResponse(
                status=404,
                content=json.dumps({"detail": "Incident not found"})
            )

        # Get associations
        cursor.execute("SELECT threat_id, incident_id, notes FROM threat_incident_association WHERE incident_id = %s",
            [incident_id]
        )

        for row in cursor.fetchall():
            associations.append({
                "threat_id": row[0],
                "incident_id": row[1],
                "notes": row[2]
            })

    return associations

@router.post("/threats/", response=ThreatIncidentAssociationSchema)
def add_threat_to_incident(request, threat_incident_data: ThreatIncidentAssociationSchema):
    with connection.cursor() as cursor:
        cursor.execute("SELECT incident_id FROM api_incident WHERE incident_id = %s",
                      [threat_incident_data.incident_id])

        if not cursor.fetchone():
            return HttpResponse(
                status=400,
                content=json.dumps({"detail": "Referenced incident not found"})
            )

        cursor.execute("SELECT threat_id FROM api_threatintelligence WHERE threat_id = %s",
                      [threat_incident_data.threat_id])

        if not cursor.fetchone():
            return HttpResponse(
                status=400,
                content=json.dumps({"detail": "Threat not found"})
            )

        # Check if association already exists
        cursor.execute(
            "SELECT threat_id FROM threat_incident_association WHERE threat_id = %s AND incident_id = %s",
            [threat_incident_data.threat_id, threat_incident_data.incident_id]
        )

        if cursor.fetchone():
            return HttpResponse(
                status=400,
                content=json.dumps({"detail": "Threat already associated with this incident"})
            )

        # Create new association
        notes = threat_incident_data.notes or ""
        cursor.execute(
            "INSERT INTO threat_incident_association (threat_id, incident_id, notes) VALUES (%s, %s, %s)",
            [threat_incident_data.threat_id, threat_incident_data.incident_id, notes]
        )

    return threat_incident_data

@router.put("/threats/", response=ThreatIncidentAssociationSchema)
def update_incident_threat(request, threat_incident_data: ThreatIncidentAssociationSchema,
                           original_threat_id: Optional[int] = None,
                           original_incident_id: Optional[int] = None):
    with connection.cursor() as cursor:
        # Check if we're updating an existing association
        if original_threat_id and original_incident_id:
            # Verify that the new threat and incident exist
            cursor.execute("SELECT incident_id FROM api_incident WHERE incident_id = %s",
                           [threat_incident_data.incident_id])
            if not cursor.fetchone():
                return HttpResponse(
                    status=400,
                    content=json.dumps({"detail": "Referenced incident not found"})
                )

            cursor.execute("SELECT threat_id FROM api_threatintelligence WHERE threat_id = %s",
                           [threat_incident_data.threat_id])
            if not cursor.fetchone():
                return HttpResponse(
                    status=400,
                    content=json.dumps({"detail": "Referenced threat not found"})
                )

            # Verify the original association exists
            cursor.execute(
                "SELECT threat_id FROM threat_incident_association WHERE threat_id = %s AND incident_id = %s",
                [original_threat_id, original_incident_id]
            )
            if not cursor.fetchone():
                return HttpResponse(
                    status=404,
                    content=json.dumps({"detail": "Original threat association not found"})
                )

            # Check if the new association would create a duplicate
            if (original_threat_id != threat_incident_data.threat_id or
                    original_incident_id != threat_incident_data.incident_id):
                cursor.execute(
                    "SELECT threat_id FROM threat_incident_association WHERE threat_id = %s AND incident_id = %s",
                    [threat_incident_data.threat_id, threat_incident_data.incident_id]
                )
                if cursor.fetchone():
                    return HttpResponse(
                        status=400,
                        content=json.dumps({"detail": "This threat is already associated with this incident"})
                    )

                # Update the association with new threat/incident pair
                cursor.execute(
                    """DELETE FROM threat_incident_association 
                       WHERE threat_id = %s AND incident_id = %s""",
                    [original_threat_id, original_incident_id]
                )

                notes = threat_incident_data.notes if hasattr(threat_incident_data, 'notes') else ""
                cursor.execute(
                    """INSERT INTO threat_incident_association (threat_id, incident_id, notes)
                       VALUES (%s, %s, %s)""",
                    [threat_incident_data.threat_id, threat_incident_data.incident_id, notes]
                )
            else:
                # Just update notes for the same threat/incident pair
                notes = threat_incident_data.notes if hasattr(threat_incident_data, 'notes') else ""
                cursor.execute(
                    "UPDATE threat_incident_association SET notes = %s WHERE threat_id = %s AND incident_id = %s",
                    [notes, original_threat_id, original_incident_id]
                )
        else:
            # Just update notes for existing association
            cursor.execute(
                "SELECT incident_id FROM threat_incident_association WHERE threat_id = %s AND incident_id = %s",
                [threat_incident_data.threat_id, threat_incident_data.incident_id]
            )
            if not cursor.fetchone():
                return HttpResponse(
                    status=404,
                    content=json.dumps({"detail": "Threat association not found"})
                )

            # Update just the notes
            cursor.execute(
                "UPDATE threat_incident_association SET notes = %s WHERE threat_id = %s AND incident_id = %s",
                [threat_incident_data.notes, threat_incident_data.threat_id, threat_incident_data.incident_id]
            )

    return threat_incident_data

@router.delete("/threats/{incident_id}/{threat_id}/")
def remove_threat_from_incident(request, incident_id: int, threat_id: int):
    # Check if association exists
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT threat_id FROM threat_incident_association WHERE threat_id = %s AND incident_id = %s",
            [threat_id, incident_id]
        )
        if not cursor.fetchone():
            return HttpResponse(
                status=404,
                content=json.dumps({"detail": "Threat association not found"})
            )

        # Delete association
        cursor.execute(
            "DELETE FROM threat_incident_association WHERE threat_id = %s AND incident_id = %s",
            [threat_id, incident_id]
        )

    return {"message": "Threat removed successfully"}
