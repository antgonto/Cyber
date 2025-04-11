# app/api/incidents/router.py
from datetime import datetime
from typing import Optional

from django.db import connection
from ninja import Router
from .schemas import (
    IncidentSchema, IncidentAssetSchema,
    IncidentListSchema, IncidentDetailSchema,
    IncidentCreateResponseSchema, IncidentUpdateResponseSchema, IncidentDeleteResponseSchema,
    ThreatIncidentAssociationSchema
)
from ..alerts.schemas import AlertListSchema

router = Router(tags=["incidents"])


@router.get("/", response=IncidentListSchema)
def list_incidents(request, status: Optional[str] = None, severity: Optional[str] = None,
                   incident_type: Optional[str] = None, assigned_to_id: Optional[int] = None,
                   search: Optional[str] = None, limit: int = 50, offset: int = 0):

    # Start building the SQL query
    sql = "SELECT * FROM api_incident"
    params = []
    where_clauses = []

    # Add filter conditions
    if status:
        where_clauses.append("status = %s")
        params.append(status)
    if severity:
        where_clauses.append("severity = %s")
        params.append(severity)
    if incident_type:
        where_clauses.append("incident_type = %s")
        params.append(incident_type)
    if assigned_to_id:
        where_clauses.append("assigned_to_id = %s")
        params.append(assigned_to_id)
    if search:
        where_clauses.append("(LOWER(incident_type) LIKE LOWER(%s) OR LOWER(description) LIKE LOWER(%s))")
        params.append(f"%{search}%")
        params.append(f"%{search}%")

    # Assemble WHERE clause if needed
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    # Count query
    count_sql = f"SELECT COUNT(*) FROM ({sql}) AS count_query"
    with connection.cursor() as cursor:
        cursor.execute(count_sql, params)
        count = cursor.fetchone()[0]

    # Final query with ordering and pagination
    sql += " ORDER BY reported_date DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        incidents = [
            {
                "incident_id": row[0],
                "incident_type": row[1],
                "description": row[2],
                "severity": row[3],
                "status": row[4],
                "assigned_to_id": row[5],
                "reported_date": row[6],
                "resolved_date": row[7]
            } for row in cursor.fetchall()
        ]

    return {
        "incidents": incidents,
        "count": count
    }

@router.post("/", response=IncidentCreateResponseSchema)
def create_incident(request, payload: IncidentSchema):
    """Create a new incident"""
    from django.db import connection

    incident_data = payload.dict(exclude_unset=True, exclude_none=True)

    # Check if assigned user exists
    if incident_data.get("assigned_to_id"):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM auth_user WHERE id = %s", [incident_data["assigned_to_id"]])
            if cursor.fetchone()[0] == 0:
                from django.http import Http404
                raise Http404("User not found")

    # Build SQL insert
    fields = incident_data.keys()
    placeholders = ["%s" for _ in fields]
    values = [incident_data[field] for field in fields]

    insert_sql = f"""
    INSERT INTO api_incident ({', '.join(fields)})
    VALUES ({', '.join(placeholders)})
    RETURNING incident_id
    """

    with connection.cursor() as cursor:
        cursor.execute(insert_sql, values)
        incident_id = cursor.fetchone()[0]

    return {"incident_id": incident_id}


@router.get("/{incident_id}", response=IncidentDetailSchema)
def get_incident(request, incident_id: int):
    # Fetch incident
    incident_sql = "SELECT * FROM api_incident WHERE incident_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(incident_sql, [incident_id])
        incident_row = cursor.fetchone()

        if not incident_row:
            from django.http import Http404
            raise Http404("Incident not found")

        incident = {
            "incident_id": incident_row[0],
            "incident_type": incident_row[1],
            "description": incident_row[2],
            "severity": incident_row[3],
            "status": incident_row[4],
            "assigned_to_id": incident_row[5],
            "reported_date": incident_row[6],
            "resolved_date": incident_row[7]
        }

    # Get related assets
    assets_sql = "SELECT * FROM incident_assets WHERE incident_id = %s"
    assets_data = []
    with connection.cursor() as cursor:
        cursor.execute(assets_sql, [incident_id])
        for row in cursor.fetchall():
            assets_data.append({
                "incident_id": row[0],
                "asset_id": row[1],
                "impact_level": row[2]
            })

    # Get related alerts
    alerts_sql = "SELECT * FROM api_alert WHERE incident_id = %s"
    alerts_data = []
    with connection.cursor() as cursor:
        cursor.execute(alerts_sql, [incident_id])
        for row in cursor.fetchall():
            alerts_data.append({
                "alert_id": row[0],
                "source": row[1],
                "alert_type": row[2],
                "severity": row[3],
                "status": row[4],
                "incident_id": row[5],
                "alert_time": row[6]
            })

    # Get related threats
    threats_sql = """
        SELECT t.threat_id, t.threat_actor_name, t.indicator_type, t.indicator_value,
               t.confidence_level, t.description, t.related_cve
        FROM api_threatintelligence t
        JOIN threat_incident_association a ON t.threat_id = a.threat_id
        WHERE a.incident_id = %s
    """
    threats_data = []
    with connection.cursor() as cursor:
        cursor.execute(threats_sql, [incident_id])
        for row in cursor.fetchall():
            threats_data.append({
                "threat_id": row[0],
                "threat_actor_name": row[1],
                "indicator_type": row[2],
                "indicator_value": row[3],
                "confidence_level": row[4],
                "description": row[5],
                "related_cve": row[6]
            })

    incident.update({
        "assets": assets_data,
        "alerts": alerts_data,
        "threats": threats_data
    })

    return incident


@router.put("/{incident_id}", response=IncidentUpdateResponseSchema)
def update_incident(request, incident_id: int, payload: IncidentSchema):
    """Update an existing incident"""
    from django.db import connection
    from django.http import Http404

    # Check if incident exists
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM api_incident WHERE incident_id = %s", [incident_id])
        if cursor.fetchone()[0] == 0:
            raise Http404("Incident not found")

    # Extract only fields in the update schema
    update_data = payload.dict(
        exclude_unset=True,
        exclude_none=True,
        include=set(payload.Config.update_include)
    )

    # If status is changed to resolved, set resolved_date if not specified
    if "status" in update_data and update_data["status"] == "resolved" and not update_data.get("resolved_date"):
        update_data["resolved_date"] = datetime.now()

    # Check if assigned user exists
    if update_data.get("assigned_to_id"):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM auth_user WHERE id = %s", [update_data["assigned_to_id"]])
            if cursor.fetchone()[0] == 0:
                raise Http404("User not found")

    # Build SQL update
    if update_data:
        set_clauses = [f"{field} = %s" for field in update_data.keys()]
        values = list(update_data.values())
        values.append(incident_id)

        update_sql = f"""
        UPDATE api_incident
        SET {', '.join(set_clauses)}
        WHERE incident_id = %s
        """

        with connection.cursor() as cursor:
            cursor.execute(update_sql, values)

    return {"message": "Incident updated successfully"}


@router.delete("/{incident_id}", response=IncidentDeleteResponseSchema)
def delete_incident(request, incident_id: int):
    """Delete an incident"""
    from django.db import connection
    from django.http import Http404

    # Check if incident exists and delete it
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM api_incident WHERE incident_id = %s", [incident_id])
        if cursor.fetchone()[0] == 0:
            raise Http404("Incident not found")

        cursor.execute("DELETE FROM api_incident WHERE incident_id = %s", [incident_id])

    return {"message": "Incident deleted successfully"}


@router.post("/assets/", response=IncidentAssetSchema)
def add_asset_to_incident(request, payload: IncidentAssetSchema):
    """Associate an asset with an incident"""
    from django.db import connection
    from django.http import Http404

    incident_asset_data = payload.dict()

    # Verify incident exists
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM api_incident WHERE incident_id = %s",
                       [incident_asset_data["incident_id"]])
        if cursor.fetchone()[0] == 0:
            raise Http404("Incident not found")

    # Check if association already exists
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM incident_assets WHERE incident_id = %s AND asset_id = %s",
            [incident_asset_data["incident_id"], incident_asset_data["asset_id"]]
        )
        exists = cursor.fetchone()[0] > 0

        if exists:
            # Update existing association
            cursor.execute(
                "UPDATE incident_assets SET impact_level = %s WHERE incident_id = %s AND asset_id = %s",
                [incident_asset_data["impact_level"], incident_asset_data["incident_id"],
                 incident_asset_data["asset_id"]]
            )
        else:
            # Create new association
            cursor.execute(
                "INSERT INTO incident_assets (incident_id, asset_id, impact_level) VALUES (%s, %s, %s)",
                [incident_asset_data["incident_id"], incident_asset_data["asset_id"],
                 incident_asset_data["impact_level"]]
            )

    return incident_asset_data


@router.delete("/assets/{incident_id}/{asset_id}")
def remove_asset_from_incident(request, incident_id: int, asset_id: int):
    """Remove an asset association from an incident"""
    from django.db import connection
    from django.http import Http404

    # Check if association exists
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM incident_assets WHERE incident_id = %s AND asset_id = %s",
            [incident_id, asset_id]
        )
        if cursor.fetchone()[0] == 0:
            raise Http404("Asset association not found")

        # Delete the association
        cursor.execute(
            "DELETE FROM incident_assets WHERE incident_id = %s AND asset_id = %s",
            [incident_id, asset_id]
        )

    return {"success": True}


@router.get("/alerts/", response=AlertListSchema)
def list_alerts(request, status: Optional[str] = None, severity: Optional[str] = None,
                source: Optional[str] = None, limit: int = 50, offset: int = 0):

    # Start building the SQL query
    sql = "SELECT * FROM api_alert"
    params = []
    where_clauses = []

    # Add filter conditions
    if status:
        where_clauses.append("status = %s")
        params.append(status)
    if severity:
        where_clauses.append("severity = %s")
        params.append(severity)
    if source:
        where_clauses.append("source = %s")
        params.append(source)

    # Assemble WHERE clause if needed
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    # Count query
    count_sql = f"SELECT COUNT(*) FROM ({sql}) AS count_query"
    with connection.cursor() as cursor:
        cursor.execute(count_sql, params)
        count = cursor.fetchone()[0]

    # Final query with ordering and pagination
    sql += " ORDER BY alert_time DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    alerts = []
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        for row in cursor.fetchall():
            alerts.append({
                "alert_id": row[0],
                "source": row[1],
                "type": row[2],
                "severity": row[3],
                "status": row[4],
                "incident_id": row[5],
                "alert_time": row[6]
            })

    return {
        "alerts": alerts,
        "count": count
    }


@router.post("/threats/association/", response=ThreatIncidentAssociationSchema)
def associate_threat_with_incident(request, payload: ThreatIncidentAssociationSchema):
    """Associate a threat with an incident"""
    from django.db import connection
    from django.http import Http404

    association_data = payload.dict(exclude_none=True)

    # Verify incident and threat exist
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM api_incident WHERE incident_id = %s",
                       [association_data["incident_id"]])
        if cursor.fetchone()[0] == 0:
            raise Http404("Incident not found")

        cursor.execute("SELECT COUNT(*) FROM api_threatintelligence WHERE threat_id = %s",
                       [association_data["threat_id"]])
        if cursor.fetchone()[0] == 0:
            raise Http404("Threat not found")

    # Check if association already exists
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM threat_incident_association WHERE threat_id = %s AND incident_id = %s",
            [association_data["threat_id"], association_data["incident_id"]]
        )
        exists = cursor.fetchone()[0] > 0

        if exists and "notes" in association_data:
            # Update existing association
            cursor.execute(
                "UPDATE threat_incident_association SET notes = %s WHERE threat_id = %s AND incident_id = %s",
                [association_data["notes"], association_data["threat_id"], association_data["incident_id"]]
            )
        elif not exists:
            # Create new association
            notes = association_data.get("notes", "")
            cursor.execute(
                "INSERT INTO threat_incident_association (threat_id, incident_id, notes) VALUES (%s, %s, %s)",
                [association_data["threat_id"], association_data["incident_id"], notes]
            )

    return association_data


