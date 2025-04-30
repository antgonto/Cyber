from ninja import Router
from django.db import connection
from django.http import HttpResponse
from typing import List, Optional
import json

from app.api.alerts.schemas import AlertListSchema, AlertSchema

router = Router(tags=["alerts"])

def transform_alert_data(alert_data):
    """Transform alert data from database format to schema format."""
    severity_mapping = {
        "Low": "low",
        "Medium": "medium",
        "High": "high",
        "Critical": "critical"
    }

    status_mapping = {
        "Active": "new",
        "Acknowledged": "acknowledged",
        "Resolved": "resolved",
        "Closed": "closed"
    }

    if alert_data.get("severity"):
        alert_data["severity"] = severity_mapping.get(alert_data["severity"], alert_data["severity"].lower())

    if alert_data.get("status"):
        alert_data["status"] = status_mapping.get(alert_data["status"], alert_data["status"].lower())

    return alert_data

@router.get("/", response=AlertListSchema)
def list_alerts(
    request,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    source: Optional[str] = None
):
    print("Listing alerts with filters:", severity, status, source)
    """List all alerts with optional filtering"""
    with connection.cursor() as cursor:
        query = "SELECT alert_id, source, name, alert_type, alert_time, severity, status, incident_id FROM api_alert"
        params = []

        # Build WHERE clause for filters
        where_clauses = []
        if severity:
            where_clauses.append("severity = %s")
            params.append(severity)
        if status:
            where_clauses.append("status = %s")
            params.append(status)
        if source:
            where_clauses.append("source = %s")
            params.append(source)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        # Add ordering
        query += " ORDER BY alert_time DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        alerts = [
            transform_alert_data({
                "alert_id": row[0],
                "source": row[1],
                "name": row[2],
                "alert_type": row[3],
                "alert_time": row[4],
                "severity": row[5],
                "status": row[6],
                "incident_id": row[7]
            })
            for row in rows
        ]

        return {"alerts": alerts, "count": len(alerts)}

@router.post("/", response=AlertSchema)
def create_alert(request, alert: AlertSchema):
    # print("alert: ", alert)
    """Create a new alert"""
    with connection.cursor() as cursor:
        # Validate incident_id if provided
        if alert.incident_id:
            cursor.execute("SELECT incident_id FROM api_incident WHERE incident_id = %s",
                          [alert.incident_id])
            if not cursor.fetchone():
                return HttpResponse(
                    status=400,
                    content=json.dumps({"detail": "Referenced incident not found"})
                )

        cursor.execute(
            """
            INSERT INTO api_alert (source, name, alert_type, alert_time, severity, status, incident_id)
            VALUES (%s, %s, %s, NOW(), %s, %s, %s)
            RETURNING alert_id, source, name, alert_type, alert_time, severity, status, incident_id
            """,
            [alert.source, alert.name, alert.alert_type, alert.severity, 'new', alert.incident_id]
        )
        row = cursor.fetchone()
        alert = {
            "alert_id": row[0],
            "source": row[1],
            "name": row[2],
            "alert_type": row[3],
            "alert_time": row[4],
            "severity": row[5],
            "status": row[6],
            "incident_id": row[7]
        }
        return alert


@router.get("/{alert_id}/", response=AlertSchema)
def get_alert(request, alert_id: int):
    print(alert_id)
    """Get alert by ID"""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT alert_id, source, name, alert_type, alert_time, severity, status, incident_id FROM api_alert WHERE alert_id = %s",
            [alert_id]
        )
        row = cursor.fetchone()
        if not row:
            return HttpResponse(
                status=404,
                content=json.dumps({"detail": "Alert not found"}))

        alert = {
            "alert_id": row[0],
            "source": row[1],
            "name": row[2],
            "alert_type": row[3],
            "alert_time": row[4],
            "severity": row[5],
            "status": row[6],
            "incident_id": row[7]
        }

        return transform_alert_data(alert)


@router.put("/{alert_id}/", response=AlertSchema)
def update_alert(request, alert_id: int, alert: AlertSchema):
    """Update an existing alert"""
    with connection.cursor() as cursor:
        # Check if alert exists
        cursor.execute("SELECT alert_id FROM api_alert WHERE alert_id = %s", [alert_id])
        if not cursor.fetchone():
            return HttpResponse(
                status=404,
                content=json.dumps({"detail": "Alert not found"})
            )

        # Validate incident_id if provided
        if alert.incident_id:
            cursor.execute("SELECT incident_id FROM api_incident WHERE incident_id = %s",
                           [alert.incident_id])
            if not cursor.fetchone():
                return HttpResponse(
                    status=400,
                    content=json.dumps({"detail": "Referenced incident not found"})
                )

        # Build update query dynamically based on provided fields
        update_fields = []
        params = []

        if alert.source:
            update_fields.append("source = %s")
            params.append(alert.source)

        if alert.name:
            update_fields.append("name = %s")
            params.append(alert.name)

        if alert.alert_type:
            update_fields.append("alert_type = %s")
            params.append(alert.alert_type)

        if alert.severity:
            update_fields.append("severity = %s")
            params.append(alert.severity)

        if alert.status:
            update_fields.append("status = %s")
            params.append(alert.status)

        if alert.incident_id:
            update_fields.append("incident_id = %s")
            params.append(alert.incident_id)

        if not update_fields:
            # If no fields to update, just return the current alert
            cursor.execute(
                "SELECT alert_id, source, name, alert_type, alert_time, severity, status, incident_id FROM api_alert WHERE alert_id = %s",
                [alert_id]
            )
            row = cursor.fetchone()
            alert = {
                "alert_id": row[0],
                "source": row[1],
                "name": row[2],
                "alert_type": row[3],
                "alert_time": row[4],
                "severity": row[5],
                "status": row[6],
                "incident_id": row[7]
            }
            return alert

        # Add alert_id to params for WHERE clause
        params.append(alert_id)

        # Execute update query
        cursor.execute(
            f"""
            UPDATE api_alert
            SET {", ".join(update_fields)}
            WHERE alert_id = %s
            RETURNING alert_id, source, name, alert_type, alert_time, severity, status, incident_id
            """,
            params
        )

        row = cursor.fetchone()
        alert = {
            "alert_id": row[0],
            "source": row[1],
            "name": row[2],
            "alert_type": row[3],
            "alert_time": row[4],
            "severity": row[5],
            "status": row[6],
            "incident_id": row[7]
        }
        return alert

@router.delete("/{alert_id}/", response=dict)
def delete_alert(request, alert_id: int):
    """Delete an alert"""
    with connection.cursor() as cursor:
        # Check if alert exists
        cursor.execute("SELECT alert_id FROM api_alert WHERE alert_id = %s", [alert_id])
        if not cursor.fetchone():
            return HttpResponse(status=404, content=json.dumps({"detail": "Alert not found"}))

        # Delete the alert
        cursor.execute("DELETE FROM api_alert WHERE alert_id = %s", [alert_id])
        return {"success": True, "message": "Alert deleted"}

@router.post("/{alert_id}/assign-incident/{incident_id}/")
def assign_incident_to_alert(request, alert_id: int, incident_id: int):
    """Assign an incident to an alert"""
    with connection.cursor() as cursor:
        # Check if alert exists
        cursor.execute("SELECT alert_id FROM api_alert WHERE alert_id = %s", [alert_id])
        if not cursor.fetchone():
            return HttpResponse(
                status=404,
                content=json.dumps({"detail": "Alert not found"})
            )

        # Check if incident exists
        cursor.execute("SELECT incident_id FROM api_incident WHERE incident_id = %s", [incident_id])
        if not cursor.fetchone():
            return HttpResponse(
                status=404,
                content=json.dumps({"detail": "Incident not found"})
            )

        # Update the alert with the incident_id
        cursor.execute(
            """
            UPDATE api_alert 
            SET incident_id = %s 
            WHERE alert_id = %s
            RETURNING alert_id, source, name, alert_type, alert_time, severity, status, incident_id
            """,
            [incident_id, alert_id]
        )

        row = cursor.fetchone()
        alert = {
            "alert_id": row[0],
            "source": row[1],
            "name": row[2],
            "alert_type": row[3],
            "alert_time": row[4],
            "severity": row[5],
            "status": row[6],
            "incident_id": row[7],
            "message": "Incident successfully assigned to alert"
        }

        return alert

@router.post("/{alert_id}/remove-incident/")
def remove_incident_from_alert(request, alert_id: int):
    """Remove incident assignment from an alert"""
    with connection.cursor() as cursor:
        # Check if alert exists
        cursor.execute("SELECT alert_id, incident_id FROM api_alert WHERE alert_id = %s", [alert_id])
        row = cursor.fetchone()
        if not row:
            return HttpResponse(
                status=404,
                content=json.dumps({"detail": "Alert not found"})
            )

        if not row[1]:  # If incident_id is already null
            return HttpResponse(
                status=400,
                content=json.dumps({"detail": "Alert already has no incident assigned"})
            )

        # Update the alert to remove the incident_id
        cursor.execute(
            """
            UPDATE api_alert 
            SET incident_id = NULL 
            WHERE alert_id = %s
            RETURNING alert_id, source, name, alert_type, alert_time, severity, status, incident_id
            """,
            [alert_id]
        )

        row = cursor.fetchone()
        alert = {
            "alert_id": row[0],
            "source": row[1],
            "name": row[2],
            "alert_type": row[3],
            "alert_time": row[4],
            "severity": row[5],
            "status": row[6],
            "incident_id": row[7],
            "message": "Incident association successfully removed from alert"
        }
        return alert