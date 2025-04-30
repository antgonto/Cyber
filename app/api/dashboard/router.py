from ninja import Router, Schema
from ninja.pagination import paginate
from typing import Optional
from django.db import connection
from datetime import datetime


# Router definition
router = Router(tags=["dashboard"])

# Schema definitions
class IncidentDashboardResponse(Schema):
    incident_id: Optional[int] = None
    incident_type: Optional[str] = None
    incident_description: Optional[str] = None
    incident_severity: Optional[str] = None
    incident_status: Optional[str] = None
    reported_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None
    assigned_user_id: Optional[int] = None
    assigned_username: Optional[str] = None
    assigned_email: Optional[str] = None
    assigned_user_role: Optional[str] = None
    affected_assets_count: Optional[int] = None
    affected_asset_names: Optional[str] = None
    highest_asset_criticality: Optional[str] = None
    related_vulnerabilities_count: Optional[int] = None
    vulnerability_titles: Optional[str] = None
    related_cves: Optional[str] = None
    related_threats_count: Optional[int] = None
    threat_actors: Optional[str] = None
    highest_threat_confidence: Optional[str] = None
    related_alerts_count:Optional[int] = None
    highest_alert_severity: Optional[str] = None
    unacknowledged_alerts_count: Optional[int] = None
    last_activity_time: Optional[datetime] = None
    activity_count: Optional[int] = None
    resolution_time_hours: Optional[float] = None


class IncidentDashboardFilterParams(Schema):
    incident_status: Optional[str] = None
    incident_severity: Optional[str] = None
    assigned_user_id: Optional[int] = None
    min_resolution_time_hours: Optional[float] = None
    max_resolution_time_hours: Optional[float] = None


@router.get("/dashboard/", response=IncidentDashboardResponse)
@paginate(IncidentDashboardResponse)
def get_dashboard_incidents(request, filters: IncidentDashboardFilterParams):
    """Get incidents from the incident_management_dashboard view with optional filtering"""

    try:
        query = "SELECT * FROM incident_management_dashboard WHERE 1=1"
        params = []

        # Apply filters
        if filters.incident_status:
            query += " AND incident_status = %s"
            params.append(filters.incident_status)

        if filters.incident_severity:
            query += " AND incident_severity = %s"
            params.append(filters.incident_severity)

        if filters.assigned_user_id:
            query += " AND assigned_user_id = %s"
            params.append(filters.assigned_user_id)

        if filters.min_resolution_time_hours is not None:
            query += " AND resolution_time_hours >= %s"
            params.append(filters.min_resolution_time_hours)

        if filters.max_resolution_time_hours is not None:
            query += " AND resolution_time_hours <= %s"
            params.append(filters.max_resolution_time_hours)

        # Count total for pagination
        count_query = f"SELECT COUNT(*) FROM ({query}) AS count_query"
        with connection.cursor() as cursor:
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]

        # Apply sorting (default to reported_date DESC if not specified)
        query += " ORDER BY reported_date DESC"

        # Apply pagination
        page = getattr(filters, 'page', 1)
        per_page = getattr(filters, 'per_page', 10)

        offset = (page - 1) * per_page
        query += f" LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        # Execute query
        items = []
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]

            for row in cursor.fetchall():
                item = dict(zip(columns, row))
                items.append(item)

        return {"items": items, "count": total}

    except Exception as e:
        # Handle error in a way that conforms to response schema
        return {"items": [], "count": 0}