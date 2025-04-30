# app/api/risk/services.py
from django.db import connection
from typing import Dict, List, Optional


def get_incident_risk_score(incident_id: int) -> Optional[Dict]:
    """
    Call the calculate_incident_risk_score PostgreSQL function to get a detailed
    risk assessment for a specific incident.

    Args:
        incident_id: The ID of the incident to analyze

    Returns:
        A dictionary containing the risk score details or None if not found
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM calculate_incident_risk_score(%s)", [incident_id])
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()

        if not row:
            return None

        return dict(zip(columns, row))


def get_all_open_incident_risk_scores() -> List[Dict]:
    """
    Get risk scores for all open and investigating incidents, ordered by
    risk priority (highest risk first).

    Returns:
        A list of dictionaries containing risk score details for each incident
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT r.*
            FROM api_incident i
            CROSS JOIN LATERAL calculate_incident_risk_score(i.incident_id) r
            WHERE i.status IN ('open', 'investigating')
            ORDER BY r.risk_score DESC
        """)

        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]