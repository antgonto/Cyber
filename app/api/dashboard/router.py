from ninja import Router, Schema, Query
from typing import Optional, List
from django.db import connection
from datetime import datetime

router = Router(tags=["dashboard"])

class IncidentDashboardResponse(Schema):
    incident_id: Optional[int]
    incident_type: Optional[str]
    incident_description: Optional[str]
    incident_severity: Optional[str]
    incident_status: Optional[str]
    reported_date: Optional[datetime]
    resolved_date: Optional[datetime]
    assigned_user_id: Optional[int]
    assigned_username: Optional[str]
    assigned_email: Optional[str]
    assigned_user_role: Optional[str]
    affected_assets_count: Optional[int]
    affected_asset_names: Optional[str]
    highest_asset_criticality: Optional[str]
    related_vulnerabilities_count: Optional[int]
    vulnerability_titles: Optional[str]
    related_cves: Optional[str]
    related_threats_count: Optional[int]
    threat_actors: Optional[str]
    highest_threat_confidence: Optional[str]
    related_alerts_count: Optional[int]
    highest_alert_severity: Optional[str]
    unacknowledged_alerts_count: Optional[int]
    last_activity_time: Optional[datetime]
    activity_count: Optional[int]
    resolution_time_hours: Optional[float]

class IncidentDashboardFilterParams(Schema):
    incident_status: Optional[str] = None
    incident_severity: Optional[str] = None
    assigned_user_id: Optional[int] = None
    min_resolution_time_hours: Optional[float] = None
    max_resolution_time_hours: Optional[float] = None

class PaginatedIncidentDashboard(Schema):
    items: List[IncidentDashboardResponse]
    count: int

@router.get("/", response=PaginatedIncidentDashboard)
def get_dashboard_incidents(
    request,
    incident_status: Optional[str] = Query(None),
    incident_severity: Optional[str] = Query(None),
    assigned_user_id: Optional[int] = Query(None),
    min_resolution_time_hours: Optional[float] = Query(None),
    max_resolution_time_hours: Optional[float] = Query(None),
    page: int = Query(1, alias="page", ge=1),
    per_page: int = Query(10, alias="per_page", ge=1),
):
    # pack into your filter schema (optional, but keeps your code DRY)
    filters = IncidentDashboardFilterParams(
        incident_status=incident_status.capitalize() if incident_status else None,
        incident_severity=incident_severity.capitalize() if incident_severity else None,
        assigned_user_id=assigned_user_id,
        min_resolution_time_hours=min_resolution_time_hours,
        max_resolution_time_hours=max_resolution_time_hours,
    )

    base_q = "SELECT * FROM incident_management_dashboard WHERE 1=1"
    params: list = []

    if filters.incident_status:
        base_q += " AND incident_status = %s"
        params.append(filters.incident_status)
    if filters.incident_severity:
        base_q += " AND incident_severity = %s"
        params.append(filters.incident_severity)
    if filters.assigned_user_id:
        base_q += " AND assigned_user_id = %s"
        params.append(filters.assigned_user_id)
    if filters.min_resolution_time_hours is not None:
        base_q += " AND resolution_time_hours >= %s"
        params.append(filters.min_resolution_time_hours)
    if filters.max_resolution_time_hours is not None:
        base_q += " AND resolution_time_hours <= %s"
        params.append(filters.max_resolution_time_hours)

    # total count
    count_sql = f"SELECT COUNT(*) FROM ({base_q}) AS cnt"
    with connection.cursor() as cursor:
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]

    # apply ordering and pagination
    base_q += " ORDER BY reported_date DESC LIMIT %s OFFSET %s"
    params.extend([per_page, (page - 1) * per_page])
    print(base_q, params)
    with connection.cursor() as cursor:
        cursor.execute(base_q, params)
        cols = [c[0] for c in cursor.description]
        rows = [dict(zip(cols, r)) for r in cursor.fetchall()]

    return {"items": rows, "count": total}
