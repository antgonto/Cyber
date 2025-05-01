from ninja import Router, Schema, Query
from typing import Optional, List
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


from ninja import Schema
from django.db import connection

class SimpleMessage(Schema):
    success: bool
    detail: str

@router.post("/create_view", response=SimpleMessage)
def create_view(request):
    """
    Creates or replaces the `refresh_incident_management_dashboard_view` stored procedure
    which in turn (re)creates the `incident_management_dashboard` view.
    """
    view = """
      CREATE OR REPLACE VIEW incident_management_dashboard AS
      SELECT 
          i.incident_id,
          i.incident_type,
          i.description AS incident_description,
          i.severity   AS incident_severity,
          i.status     AS incident_status,
          i.reported_date,
          i.resolved_date,
          u.user_id    AS assigned_user_id,
          u.username   AS assigned_username,
          u.email      AS assigned_email,
          u.role       AS assigned_user_role,
          COUNT(DISTINCT ia.asset_id)             AS affected_assets_count,
          STRING_AGG(DISTINCT a.asset_name, ', ') AS affected_asset_names,
          MAX(a.criticality_level)                AS highest_asset_criticality,
          COUNT(DISTINCT av.vulnerability_id)     AS related_vulnerabilities_count,
          STRING_AGG(DISTINCT v.title, ', ')      AS vulnerability_titles,
          STRING_AGG(DISTINCT v.cve_reference, ', ') AS related_cves,
          COUNT(DISTINCT tia.threat_id)           AS related_threats_count,
          STRING_AGG(DISTINCT ti.threat_actor_name, ', ') AS threat_actors,
          MAX(ti.confidence_level)               AS highest_threat_confidence,
          COUNT(DISTINCT al.alert_id)             AS related_alerts_count,
          MAX(al.severity)                        AS highest_alert_severity,
          COUNT(DISTINCT CASE WHEN al.status = 'new' THEN al.alert_id END)
                                                 AS unacknowledged_alerts_count,
          MAX(ual.timestamp)                     AS last_activity_time,
          COUNT(DISTINCT ual.log_id)             AS activity_count,
          CASE 
            WHEN i.status IN ('resolved','closed') THEN
              EXTRACT(EPOCH FROM (i.resolved_date - i.reported_date))/3600
            ELSE
              EXTRACT(EPOCH FROM (NOW() - i.reported_date))/3600
          END                                     AS resolution_time_hours
      FROM api_incident i
      LEFT JOIN api_user u    ON i.assigned_to_id = u.user_id
      LEFT JOIN incident_assets ia ON ia.incident_id = i.incident_id
      LEFT JOIN api_asset a   ON a.asset_id = ia.asset_id
      LEFT JOIN asset_vulnerabilities av
                             ON av.asset_id = a.asset_id
      LEFT JOIN api_vulnerability v
                             ON v.vulnerability_id = av.vulnerability_id
      LEFT JOIN threat_incident_association tia
                             ON tia.incident_id = i.incident_id
      LEFT JOIN api_threatintelligence ti
                             ON ti.threat_id = tia.threat_id
      LEFT JOIN api_alert al  ON al.incident_id = i.incident_id
      LEFT JOIN user_activity_logs ual
        ON ual.resource_type = 'incident'
       AND ual.resource_id   = i.incident_id
      GROUP BY 
          i.incident_id,
          i.incident_type,
          i.description,
          i.severity,
          i.status,
          i.reported_date,
          i.resolved_date,
          u.user_id,
          u.username,
          u.email,
          u.role
      ORDER BY 
        CASE i.status
          WHEN 'open'          THEN 1
          WHEN 'investigating' THEN 2
          WHEN 'resolved'      THEN 3
          WHEN 'closed'        THEN 4
          ELSE 5
        END,
        CASE i.severity
          WHEN 'critical' THEN 1
          WHEN 'high'     THEN 2
          WHEN 'medium'   THEN 3
          WHEN 'low'      THEN 4
          ELSE 5
        END,
        i.reported_date DESC;
    """
    with connection.cursor() as cursor:
        cursor.execute(view)
    return {"success": True, "detail": "View created or replaced successfully"}


@router.post("/refresh-view", response=SimpleMessage)
def refresh_dashboard_view(request):
    """
    Triggers the `create_stored_procedure_dashboard` stored procedure,
    which (re)creates the `incident_management_dashboard` view.
    """
    with connection.cursor() as cursor:
        cursor.execute("CALL create_stored_procedure_dashboard()")
    return {"success": True, "detail": "create_stored_procedure_dashboard created"}


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
