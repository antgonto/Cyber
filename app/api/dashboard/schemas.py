from typing import Optional, List

from ninja import Schema
from datetime import datetime

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