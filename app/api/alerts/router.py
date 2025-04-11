from ninja import Router
from django.db import connection
from django.http import HttpResponse
from typing import List, Optional
import json

from app.api.alerts.schemas import AlertSchema

router = Router(tags=["alerts"])

@router.get("/", response=List[AlertSchema])
def list_alerts(request):
    """Get all alerts"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT alert_id, source, alert_type, alert_time, severity, status, incident_id
            FROM api_alert
            ORDER BY alert_time DESC
        """)
        alerts = []
        for result in cursor.fetchall():
            alert = {
                "alert_id": result[0],
                "source": result[1],
                "alert_type": result[2],
                "alert_time": result[3],
                "severity": result[4],
                "status": result[5],
                "incident_id": result[6]
            }
            alerts.append(alert)
        return alerts

@router.post("/", response=AlertSchema)
def create_alert(request, alert: AlertSchema):
    """Create a new alert"""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO api_alert (source, alert_type, alert_time, severity, status)
            VALUES (%s, %s, NOW(), %s, %s)
            RETURNING alert_id, source, alert_type, alert_time, severity, status, incident_id
            """,
            [alert.source, alert.alert_type, alert.severity, 'new']
        )
        row = cursor.fetchone()
        alert = {
            "alert_id": row[0],
            "source": row[1],
            "alert_type": row[2],
            "alert_time": row[3],
            "severity": row[4],
            "status": row[5],
            "incident_id": row[6],
        }
        return alert

@router.get("/{alert_id}", response=AlertSchema)
def get_alert(request, alert_id: int):
    """Get alert by ID"""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT alert_id, source, alert_type, alert_time, severity, status, incident_id FROM api_alert WHERE alert_id = %s",
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
            "alert_type": row[2],
            "alert_time": row[3],
            "severity": row[4],
            "status": row[5],
            "incident_id": row[6],
        }
        return alert


@router.put("/{alert_id}", response=AlertSchema)
def update_alert(request, alert_id: int, alert: AlertSchema):
    """Update an existing alert"""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT alert_id FROM api_alert WHERE alert_id = %s",
            [alert_id]
        )
        if not cursor.fetchone():
            return HttpResponse(
                status=404,
                content=json.dumps({"detail": "Alert not found"})
            )

        # Build update query dynamically based on provided fields
        update_fields = []
        params = []

        if alert.source:
            update_fields.append("source = %s")
            params.append(alert.source)

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
                "SELECT alert_id, source, alert_type, alert_time, severity, status, incident_id FROM api_alert WHERE alert_id = %s",
                [alert_id]
            )
            row = cursor.fetchone()
            alert = {
                "alert_id": row[0],
                "source": row[1],
                "alert_type": row[2],
                "alert_time": row[3],
                "severity": row[4],
                "status": row[5],
                "incident_id": row[6]
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
            RETURNING alert_id, source, alert_type, alert_time, severity, status, incident_id
            """,
            params
        )

        row = cursor.fetchone()
        alert = {
            "alert_id": row[0],
            "source": row[1],
            "alert_type": row[2],
            "alert_time": row[3],
            "severity": row[4],
            "status": row[5],
            "incident_id": row[6]
        }
        return alert

@router.delete("/{alert_id}", response=dict)
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