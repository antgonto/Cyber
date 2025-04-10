
from django.db import connection, transaction

from ninja import Router

from app.api.common.schemas import ErrorSchema, SuccessSchema
from app.api.incidents.schemas import ThreatIncidentAssociationSchema
from app.api.threat_intelligence.schemas import (
    ThreatIntelligenceSchema,
    ThreatIntelligenceListSchema,
    ThreatIntelligenceCreateResponseSchema,
    ThreatIntelligenceUpdateResponseSchema,
    ThreatIntelligenceDeleteResponseSchema,
    ThreatAssetAssociationSchema,
    ThreatVulnerabilityAssociationSchema
)

router = Router(tags=["Threat Intelligence"])


def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dictionaries"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


@router.get("/", response=ThreatIntelligenceListSchema)
def list_threats(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT threat_id, threat_actor_name, indicator_type, indicator_value, 
                   confidence_level, description, related_cve
            FROM threat_intelligence
            ORDER BY threat_id
        """)
        threats = dictfetchall(cursor)

    return {
        "threats": threats,
        "count": len(threats)
    }


@router.get("/{threat_id}", response={200: ThreatIntelligenceSchema, 404: ErrorSchema})
def get_threat(request, threat_id: int):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT threat_id, threat_actor_name, indicator_type, indicator_value, 
                   confidence_level, description, related_cve
            FROM threat_intelligence
            WHERE threat_id = %s
        """, [threat_id])
        threat = cursor.fetchone()

    if not threat:
        return 404, {"message": "Threat intelligence not found"}

    return 200, {
        "threat_id": threat[0],
        "threat_actor_name": threat[1],
        "indicator_type": threat[2],
        "indicator_value": threat[3],
        "confidence_level": threat[4],
        "description": threat[5],
        "related_cve": threat[6]
    }


@router.post("/", response={201: ThreatIntelligenceCreateResponseSchema, 400: ErrorSchema})
def create_threat(request, payload: ThreatIntelligenceSchema):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO threat_intelligence 
                (threat_actor_name, indicator_type, indicator_value, confidence_level, description, related_cve)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING threat_id
            """, [
                payload.threat_actor_name,
                payload.indicator_type,
                payload.indicator_value,
                payload.confidence_level,
                payload.description,
                payload.related_cve
            ])
            threat_id = cursor.fetchone()[0]

        return 201, {"threat_id": threat_id}
    except Exception as e:
        return 400, {"message": str(e)}


@router.put("/{threat_id}", response={200: ThreatIntelligenceUpdateResponseSchema, 404: ErrorSchema, 400: ErrorSchema})
def update_threat(request, threat_id: int, payload: ThreatIntelligenceSchema):
    try:
        with connection.cursor() as cursor:
            # Check if threat exists
            cursor.execute("SELECT 1 FROM threat_intelligence WHERE threat_id = %s", [threat_id])
            if not cursor.fetchone():
                return 404, {"message": "Threat intelligence not found"}

            cursor.execute("""
                UPDATE threat_intelligence
                SET threat_actor_name = %s,
                    indicator_type = %s,
                    indicator_value = %s,
                    confidence_level = %s,
                    description = %s,
                    related_cve = %s
                WHERE threat_id = %s
            """, [
                payload.threat_actor_name,
                payload.indicator_type,
                payload.indicator_value,
                payload.confidence_level,
                payload.description,
                payload.related_cve,
                threat_id
            ])

        return 200, {}
    except Exception as e:
        return 400, {"message": str(e)}


@router.delete("/{threat_id}", response={200: ThreatIntelligenceDeleteResponseSchema, 404: ErrorSchema})
def delete_threat(request, threat_id: int):
    with connection.cursor() as cursor:
        # Check if threat exists
        cursor.execute("SELECT 1 FROM threat_intelligence WHERE threat_id = %s", [threat_id])
        if not cursor.fetchone():
            return 404, {"message": "Threat intelligence not found"}

        cursor.execute("DELETE FROM threat_intelligence WHERE threat_id = %s", [threat_id])

    return 200, {}


@router.post("/asset-association", response={201: SuccessSchema, 400: ErrorSchema, 404: ErrorSchema})
def create_threat_asset_association(request, payload: ThreatAssetAssociationSchema):
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                # Check if threat exists
                cursor.execute("SELECT 1 FROM threat_intelligence WHERE threat_id = %s", [payload.threat_id])
                if not cursor.fetchone():
                    return 404, {"message": "Threat intelligence not found"}

                # Check if asset exists
                cursor.execute("SELECT 1 FROM asset WHERE asset_id = %s", [payload.asset_id])
                if not cursor.fetchone():
                    return 404, {"message": "Asset not found"}

                # Create association
                cursor.execute("""
                    INSERT INTO threat_asset_association (threat_id, asset_id)
                    VALUES (%s, %s)
                """, [payload.threat_id, payload.asset_id])

        return 201, {"message": "Association created successfully"}
    except Exception as e:
        return 400, {"message": str(e)}


@router.post("/vulnerability-association", response={201: SuccessSchema, 400: ErrorSchema, 404: ErrorSchema})
def create_threat_vulnerability_association(request, payload: ThreatVulnerabilityAssociationSchema):
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                # Check if threat exists
                cursor.execute("SELECT 1 FROM threat_intelligence WHERE threat_id = %s", [payload.threat_id])
                if not cursor.fetchone():
                    return 404, {"message": "Threat intelligence not found"}

                # Check if vulnerability exists
                cursor.execute("SELECT 1 FROM vulnerability WHERE vulnerability_id = %s", [payload.vulnerability_id])
                if not cursor.fetchone():
                    return 404, {"message": "Vulnerability not found"}

                # Create association
                cursor.execute("""
                    INSERT INTO threat_vulnerability_association (threat_id, vulnerability_id)
                    VALUES (%s, %s)
                """, [payload.threat_id, payload.vulnerability_id])

        return 201, {"message": "Association created successfully"}
    except Exception as e:
        return 400, {"message": str(e)}


@router.post("/incident-association", response={201: SuccessSchema, 400: ErrorSchema, 404: ErrorSchema})
def create_threat_incident_association(request, payload: ThreatIncidentAssociationSchema):
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                # Check if threat exists
                cursor.execute("SELECT 1 FROM threat_intelligence WHERE threat_id = %s", [payload.threat_id])
                if not cursor.fetchone():
                    return 404, {"message": "Threat intelligence not found"}

                # Check if incident exists
                cursor.execute("SELECT 1 FROM incident WHERE incident_id = %s", [payload.incident_id])
                if not cursor.fetchone():
                    return 404, {"message": "Incident not found"}

                # Create association
                cursor.execute("""
                    INSERT INTO threat_incident_association (threat_id, incident_id, notes)
                    VALUES (%s, %s, %s)
                """, [payload.threat_id, payload.incident_id, payload.notes])

        return 201, {"message": "Association created successfully"}
    except Exception as e:
        return 400, {"message": str(e)}