# SQL View Explanation: Incident Management Dashboard
# This SQL file creates a comprehensive database view called incident_management_dashboard that aggregates data from multiple tables related to security incidents. This view is likely used for reporting and visualization in a security incident management system.
# Key Components:
# Line 8. Core Incident Information
# Line 17. Assignment Information
# Line 25. Related Assets, Vulnerabilities and Threats. The view aggregates counts and details using functions like COUNT, STRING_AGG, and MAX:
# Line 48. Time and Resolution Metrics
# Line 58. Table Joins. The view joins multiple tables to gather all necessary information.

view = """
CREATE OR REPLACE VIEW incident_management_dashboard AS
SELECT 
    i.incident_id,
    i.incident_type,
    i.description AS incident_description,
    i.severity AS incident_severity,
    i.status AS incident_status,
    i.reported_date,
    i.resolved_date,
    u.user_id AS assigned_user_id,
    u.username AS assigned_username,
    u.email AS assigned_email,
    u.role AS assigned_user_role,
    
    -- Asset information
    COUNT(DISTINCT ia.asset_id) AS affected_assets_count,
    STRING_AGG(DISTINCT a.asset_name, ', ') AS affected_asset_names,
    MAX(a.criticality_level) AS highest_asset_criticality,
    
    -- Vulnerability information
    COUNT(DISTINCT av.vulnerability_id) AS related_vulnerabilities_count,
    STRING_AGG(DISTINCT v.title, ', ') AS vulnerability_titles,
    STRING_AGG(DISTINCT v.cve_reference, ', ') AS related_cves,
    
    -- Threat intelligence
    COUNT(DISTINCT tia.threat_id) AS related_threats_count,
    STRING_AGG(DISTINCT ti.threat_actor_name, ', ') AS threat_actors,
    MAX(ti.confidence_level) AS highest_threat_confidence,
    
    -- Alert information
    COUNT(DISTINCT al.alert_id) AS related_alerts_count,
    MAX(al.severity) AS highest_alert_severity,
    COUNT(DISTINCT CASE WHEN al.status = 'new' THEN al.alert_id END) AS unacknowledged_alerts_count,
    
    -- Activity metrics
    MAX(ual.timestamp) AS last_activity_time,
    COUNT(DISTINCT ual.log_id) AS activity_count,
    
    -- Time metrics
    CASE 
        WHEN i.status = 'resolved' OR i.status = 'closed' THEN 
            EXTRACT(EPOCH FROM (i.resolved_date - i.reported_date))/3600
        ELSE 
            EXTRACT(EPOCH FROM (NOW() - i.reported_date))/3600
    END AS resolution_time_hours
    
FROM api_incident i
LEFT JOIN api_user u ON i.assigned_to_id = u.user_id
LEFT JOIN incident_assets ia ON ia.incident_id = i.incident_id
LEFT JOIN api_asset a ON a.asset_id = ia.asset_id
LEFT JOIN asset_vulnerabilities av ON av.asset_id = a.asset_id
LEFT JOIN api_vulnerability v ON v.vulnerability_id = av.vulnerability_id
LEFT JOIN threat_incident_association tia ON tia.incident_id = i.incident_id
LEFT JOIN api_threatintelligence ti ON ti.threat_id = tia.threat_id
LEFT JOIN api_alert al ON al.incident_id = i.incident_id
LEFT JOIN user_activity_logs ual ON ual.resource_type = 'incident' AND ual.resource_id = i.incident_id

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
    CASE 
        WHEN i.status = 'open' THEN 1
        WHEN i.status = 'investigating' THEN 2
        WHEN i.status = 'resolved' THEN 3
        WHEN i.status = 'closed' THEN 4
    END,
    CASE 
        WHEN i.severity = 'critical' THEN 1
        WHEN i.severity = 'high' THEN 2
        WHEN i.severity = 'medium' THEN 3
        WHEN i.severity = 'low' THEN 4
    END,
    i.reported_date DESC;
"""





