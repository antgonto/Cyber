import json
from typing import List, Optional

from django.db import connection, transaction
from django.http import HttpResponse

from ninja import Router

from app.api.schemas import ErrorSchema, SuccessSchema
from app.api.incidents.schemas import ThreatIncidentAssociationSchema
from app.api.threat_intelligence.schemas import (
    ThreatIntelligenceSchema,
    ThreatIntelligenceListSchema,
    ThreatIntelligenceCreateResponseSchema,
    ThreatIntelligenceUpdateResponseSchema,
    ThreatIntelligenceDeleteResponseSchema,
    ThreatAssetAssociationSchema,
    ThreatVulnerabilityAssociationSchema, ThreatIntelligenceListResponseSchema, ThreatAssetAssociationResponseSchema
)

router = Router(tags=["threat_intelligence"])


def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dictionaries"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


@router.get("/", response=ThreatIntelligenceListResponseSchema)
def list_threats(
        request,
        threat_actor_name: str = None,
        indicator_type: str = None,
        confidence_level: str = None,
        related_cve: str = None
):
    with connection.cursor() as cursor:
        query = """
            SELECT
                t.threat_id, t.threat_actor_name, t.indicator_type, t.indicator_value,
                t.confidence_level, t.description, t.related_cve, t.date_identified, t.last_updated,
                ARRAY_AGG(DISTINCT a.asset_id) FILTER (WHERE a.asset_id IS NOT NULL) as asset_ids,
                ARRAY_AGG(DISTINCT v.vulnerability_id) FILTER (WHERE v.vulnerability_id IS NOT NULL) as vulnerability_ids,
                ARRAY_AGG(DISTINCT i.incident_id) FILTER (WHERE i.incident_id IS NOT NULL) as incident_ids
            FROM api_threatintelligence t
            LEFT JOIN threat_asset_association taa ON t.threat_id = taa.threat_id
            LEFT JOIN asset a ON taa.asset_id = a.asset_id
            LEFT JOIN threat_vulnerability_association tva ON t.threat_id = tva.threat_id
            LEFT JOIN vulnerability v ON tva.vulnerability_id = v.vulnerability_id
            LEFT JOIN incident_threat_association ita ON t.threat_id = ita.threat_id
            LEFT JOIN incident i ON ita.incident_id = i.incident_id
        """

        where_clauses = []
        params = []

        if threat_actor_name:
            where_clauses.append("t.threat_actor_name LIKE %s")
            params.append(f"%{threat_actor_name}%")
        if indicator_type:
            where_clauses.append("t.indicator_type = %s")
            params.append(indicator_type)
        if confidence_level:
            where_clauses.append("t.confidence_level = %s")
            params.append(confidence_level)
        if related_cve:
            where_clauses.append("t.related_cve LIKE %s")
            params.append(f"%{related_cve}%")

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += """
            GROUP BY t.threat_id
            ORDER BY t.threat_id
        """

        cursor.execute(query, params)
        threats_raw = dictfetchall(cursor)

        # Process the results to handle array data
        threats = []
        for threat in threats_raw:
            # Convert None to empty lists and ensure arrays are properly processed
            assets = threat.get('asset_ids', []) or []
            vulnerabilities = threat.get('vulnerability_ids', []) or []
            incidents = threat.get('incident_ids', []) or []

            # Remove None from arrays if present
            assets = [a for a in assets if a is not None]
            vulnerabilities = [v for v in vulnerabilities if v is not None]
            incidents = [i for i in incidents if i is not None]

            # Create the processed threat object
            processed_threat = {
                "threat_id": threat['threat_id'],
                "threat_actor_name": threat['threat_actor_name'],
                "indicator_type": threat['indicator_type'],
                "indicator_value": threat['indicator_value'],
                "confidence_level": threat['confidence_level'],
                "description": threat['description'],
                "related_cve": threat['related_cve'],
                "date_identified": threat['date_identified'],
                "last_updated": threat['last_updated'],
                "assets": assets,
                "vulnerabilities": vulnerabilities,
                "incidents": incidents
            }
            threats.append(processed_threat)

    return {
        "threats": threats,
        "count": len(threats)
    }



@router.post("/", response={201: ThreatIntelligenceCreateResponseSchema, 400: ErrorSchema})
def create_threat(request, payload: ThreatIntelligenceSchema):
    try:
        # Validate required fields
        if not payload.threat_actor_name:
            return 400, {"message": "Threat actor name is required"}
        if not payload.indicator_type:
            return 400, {"message": "Indicator type is required"}
        if not payload.indicator_value:
            return 400, {"message": "Indicator value is required"}
        if not payload.confidence_level:
            return 400, {"message": "Confidence level is required"}

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO api_threatintelligence
                    (threat_actor_name, indicator_type, indicator_value, confidence_level,
                     description, related_cve, date_identified, last_updated)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
                    RETURNING threat_id, date_identified, last_updated
                """, [
                    payload.threat_actor_name,
                    payload.indicator_type,
                    payload.indicator_value,
                    payload.confidence_level,
                    payload.description,
                    payload.related_cve
                ])
                result = cursor.fetchone()
                threat_id = result[0]
                date_identified = result[1]
                last_updated = result[2]

                # Process asset associations
                if payload.assets:
                    for asset_id in payload.assets:
                        cursor.execute("""
                            INSERT INTO threat_asset_association (threat_id, asset_id)
                            VALUES (%s, %s)
                        """, [threat_id, asset_id])

                # Process vulnerability associations
                if payload.vulnerabilities:
                    for vulnerability_id in payload.vulnerabilities:
                        cursor.execute("""
                            INSERT INTO threat_vulnerability_association (threat_id, vulnerability_id)
                            VALUES (%s, %s)
                        """, [threat_id, vulnerability_id])

                # Process incident associations
                if payload.incidents:
                    for incident_id in payload.incidents:
                        cursor.execute("""
                            INSERT INTO incident_threat_association (threat_id, incident_id)
                            VALUES (%s, %s)
                        """, [threat_id, incident_id])

        return 201, {
            "threat_id": threat_id,
            "date_identified": date_identified,
            "last_updated": last_updated
        }
    except Exception as e:
        return 400, {"message": str(e)}


@router.get("/{threat_id}", response={200: ThreatIntelligenceSchema, 404: ErrorSchema})
def get_threat(request, threat_id: int):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                t.threat_id, t.threat_actor_name, t.indicator_type, t.indicator_value,
                t.confidence_level, t.description, t.related_cve, t.date_identified, t.last_updated,
                ARRAY_AGG(DISTINCT a.asset_id) FILTER (WHERE a.asset_id IS NOT NULL) as asset_ids,
                ARRAY_AGG(DISTINCT v.vulnerability_id) FILTER (WHERE v.vulnerability_id IS NOT NULL) as vulnerability_ids,
                ARRAY_AGG(DISTINCT i.incident_id) FILTER (WHERE i.incident_id IS NOT NULL) as incident_ids
            FROM api_threatintelligence t
            LEFT JOIN threat_asset_association taa ON t.threat_id = taa.threat_id
            LEFT JOIN asset a ON taa.asset_id = a.asset_id
            LEFT JOIN threat_vulnerability_association tva ON t.threat_id = tva.threat_id
            LEFT JOIN vulnerability v ON tva.vulnerability_id = v.vulnerability_id
            LEFT JOIN incident_threat_association ita ON t.threat_id = ita.threat_id
            LEFT JOIN incident i ON ita.incident_id = i.incident_id
            WHERE t.threat_id = %s
            GROUP BY t.threat_id
        """, [threat_id])
        threat = cursor.fetchone()

    if not threat:
        return 404, {"message": "Threat intelligence not found"}

    # Process the arrays to ensure proper handling
    assets = threat[9] or []
    vulnerabilities = threat[10] or []
    incidents = threat[11] or []

    # Remove None values if present
    assets = [a for a in assets if a is not None]
    vulnerabilities = [v for v in vulnerabilities if v is not None]
    incidents = [i for i in incidents if i is not None]

    return 200, {
        "threat_id": threat[0],
        "threat_actor_name": threat[1],
        "indicator_type": threat[2],
        "indicator_value": threat[3],
        "confidence_level": threat[4],
        "description": threat[5],
        "related_cve": threat[6],
        "date_identified": threat[7],
        "last_updated": threat[8],
        "assets": assets,
        "vulnerabilities": vulnerabilities,
        "incidents": incidents
    }


@router.put("/{threat_id}", response={200: ThreatIntelligenceUpdateResponseSchema, 404: ErrorSchema, 400: ErrorSchema})
def update_threat(request, threat_id: int, payload: ThreatIntelligenceSchema):
    try:
        # Validate required fields
        if not payload.threat_actor_name:
            return 400, {"message": "Threat actor name is required"}
        if not payload.indicator_type:
            return 400, {"message": "Indicator type is required"}
        if not payload.indicator_value:
            return 400, {"message": "Indicator value is required"}
        if not payload.confidence_level:
            return 400, {"message": "Confidence level is required"}

        with transaction.atomic():
            with connection.cursor() as cursor:
                # Check if threat exists
                cursor.execute("SELECT 1 FROM api_threatintelligence WHERE threat_id = %s", [threat_id])
                if not cursor.fetchone():
                    return 404, {"message": "Threat intelligence not found"}

                cursor.execute("""
                    UPDATE api_threatintelligence
                    SET threat_actor_name = %s,
                        indicator_type = %s,
                        indicator_value = %s,
                        confidence_level = %s,
                        description = %s,
                        related_cve = %s,
                        last_updated = NOW()
                    WHERE threat_id = %s
                    RETURNING last_updated
                """, [
                    payload.threat_actor_name,
                    payload.indicator_type,
                    payload.indicator_value,
                    payload.confidence_level,
                    payload.description,
                    payload.related_cve,
                    threat_id
                ])
                last_updated = cursor.fetchone()[0]

                # Update asset associations
                cursor.execute("DELETE FROM threat_asset_association WHERE threat_id = %s", [threat_id])
                if payload.assets:
                    for asset_id in payload.assets:
                        cursor.execute("""
                            INSERT INTO threat_asset_association (threat_id, asset_id)
                            VALUES (%s, %s)
                        """, [threat_id, asset_id])

                # Update vulnerability associations
                cursor.execute("DELETE FROM threat_vulnerability_association WHERE threat_id = %s", [threat_id])
                if payload.vulnerabilities:
                    for vulnerability_id in payload.vulnerabilities:
                        cursor.execute("""
                            INSERT INTO threat_vulnerability_association (threat_id, vulnerability_id)
                            VALUES (%s, %s)
                        """, [threat_id, vulnerability_id])

                # Update incident associations
                cursor.execute("DELETE FROM incident_threat_association WHERE threat_id = %s", [threat_id])
                if payload.incidents:
                    for incident_id in payload.incidents:
                        cursor.execute("""
                            INSERT INTO incident_threat_association (threat_id, incident_id)
                            VALUES (%s, %s)
                        """, [threat_id, incident_id])

        return 200, {"threat_id": threat_id, "last_updated": last_updated}
    except Exception as e:
        return 400, {"message": str(e)}


@router.delete("/{threat_id}", response={200: ThreatIntelligenceDeleteResponseSchema, 404: ErrorSchema})
def delete_threat(request, threat_id: int):
    with transaction.atomic():
        with connection.cursor() as cursor:
            # Check if threat exists
            cursor.execute("SELECT 1 FROM api_threatintelligence WHERE threat_id = %s", [threat_id])
            if not cursor.fetchone():
                return 404, {"message": "Threat intelligence not found"}

            # Delete associations first to avoid foreign key constraint violations
            cursor.execute("DELETE FROM threat_asset_association WHERE threat_id = %s", [threat_id])
            cursor.execute("DELETE FROM threat_vulnerability_association WHERE threat_id = %s", [threat_id])
            cursor.execute("DELETE FROM incident_threat_association WHERE threat_id = %s", [threat_id])

            # Then delete the threat itself
            cursor.execute("DELETE FROM api_threatintelligence WHERE threat_id = %s", [threat_id])

    return 200, {"message": "Threat intelligence deleted successfully"}



# Get all associations
@router.get("/assets/{threat_id}", response={200: List[ThreatAssetAssociationResponseSchema], 400: ErrorSchema})
def get_threat_assets(request, threat_id: int):
    assets = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT threat_id FROM api_threatintelligence WHERE threat_id = %s", [threat_id])
        if not cursor.fetchone():
            return HttpResponse(
                status=404,
                content=json.dumps({"detail": "Threat not found"})
            )

        # Get all assets for the incident
        cursor.execute(
            """
            SELECT threat_id, asset_id, notes 
            FROM threat_asset_association 
            WHERE threat_id = %s
            """,
            [threat_id]
        )


        for row in cursor.fetchall():
            assets.append({
                "threat_id": row[0],
                "asset_id": row[1],
                "notes": row[2]
            })

        return assets


# Create a new association
@router.post("/assets/", response={201: ThreatAssetAssociationResponseSchema, 400: ErrorSchema})
def add_asset_to_threat(request, threat_asset_data: ThreatAssetAssociationSchema):
    with transaction.atomic():
        with connection.cursor() as cursor:
            # Check if association already exists
            cursor.execute(
                    "SELECT threat_id FROM threat_asset_association WHERE threat_id = %s AND asset_id = %s",
                    [threat_asset_data.threat_id, threat_asset_data.asset_id])

            if cursor.fetchone():
                return HttpResponse(
                    status=400,
                    content=json.dumps({"detail": "Asset already associated with this incident"})
                )

            # Validate that the threat and asset exist
            cursor.execute("SELECT threat_id FROM api_threatintelligence WHERE threat_id = %s",
                           [threat_asset_data.threat_id])
            if not cursor.fetchone():
                return HttpResponse(
                    status=400,
                    content=json.dumps({"detail": "Referenced threat not found"})
                )
            # Verify asset exists
            cursor.execute("SELECT asset_id FROM asset WHERE asset_id = %s",
                           [threat_asset_data.asset_id])
            if not cursor.fetchone():
                return HttpResponse(
                    status=400,
                    content=json.dumps({"detail": "Referenced asset not found"})
                )

            # Create the association
            cursor.execute("""
                    INSERT INTO threat_asset_association (threat_id, asset_id, notes) VALUES (%s, %s, %s)
                    RETURNING id, threat_id, asset_id, notes    
                """,
                [threat_asset_data.threat_id, threat_asset_data.asset_id, threat_asset_data.notes])

        return threat_asset_data

# Update association
@router.put("/assets", response={200: ThreatAssetAssociationResponseSchema, 404: ErrorSchema, 400: ErrorSchema})
def update_threat_asset(request, threat_asset_data: ThreatAssetAssociationSchema,
                        original_threat_id: Optional[int] = None,
                        original_asset_id: Optional[int] = None):

    with connection.cursor() as cursor:
        # Check if association exists
        cursor.execute("SELECT threat_id FROM threat_asset_association WHERE threat_id = %s AND asset_id = %s",
                       [original_threat_id, original_asset_id]
        )

        if not cursor.fetchone():
            return HttpResponse(
                status=404,
                content=json.dumps({"detail": "Original asset association not found"})
            )

        # Validate that the threat and asset exist
        cursor.execute("SELECT threat_id FROM api_threatintelligence WHERE threat_id = %s",
                       [threat_asset_data.threat_id])

        if not cursor.fetchone():
            return HttpResponse(
                status=400,
                content=json.dumps({"detail": "Referenced threat not found"})
            )

        cursor.execute("SELECT asset_id FROM api_asset WHERE asset_id = %s",
                       [threat_asset_data.asset_id])
        if not cursor.fetchone():
            return HttpResponse(
                status=400,
                content=json.dumps({"detail": "Referenced asset not found"})
            )

        if ((original_threat_id != threat_asset_data.threat_id) or (original_asset_id != threat_asset_data.asset_id)):
            # Update the association (either same pair with new impact_level or completely new pair)
            cursor.execute(
                "DELETE FROM threat_asset_association WHERE threat_id = %s AND asset_id = %s",
                [original_threat_id, original_asset_id]
            )
            # Update the association (either same pair with new data or a completely new pair)
            cursor.execute(
                """INSERT INTO threat_asset_association (threat_id, asset_id, notes) 
                   VALUES (%s, %s, %s)""",
                [threat_asset_data.threat_id, threat_asset_data.asset_id, threat_asset_data.notes]
            )
        else:
            # Just update impact_level for existing association
            cursor.execute(
                "SELECT threat_id FROM threat_asset_association WHERE threat_id = %s AND asset_id = %s",
                [threat_asset_data.threat_id, threat_asset_data.asset_id]
            )
            if not cursor.fetchone():
                return HttpResponse(
                    status=404,
                    content=json.dumps({"detail": "Asset association not found"})
                )

            # Update just the impact level
            cursor.execute(
                "UPDATE threat_asset_association SET notes = %s WHERE threat_id = %s AND asset_id = %s",
                [threat_asset_data.notes, threat_asset_data.threat_id, threat_asset_data.asset_id]
            )

        return threat_asset_data


# Delete association
@router.delete("/threats/{threat_id}/{asset_id}", response={200: dict, 404: ErrorSchema})
def remove_asset_from_threat(request, threat_id: int, asset_id: int):
    with connection.cursor() as cursor:
        # Check if association exists
        cursor.execute("SELECT threat_id FROM threat_asset_association WHERE threat_id = %s AND asset_id = %s",
                       [threat_id, asset_id]
        )
        if not cursor.fetchone():
            return HttpResponse(
                status=404,
                content=json.dumps({"detail": "Asset association not found"})
            )


        # Delete the association
        cursor.execute(
            "DELETE FROM threat_asset_association WHERE threat_id = %s AND asset_id = %s",
            [threat_id, asset_id]
        )

        return {"success": True}


@router.get("/vulnerabilities/{threat_id}", response=list[ThreatVulnerabilityAssociationSchema])
def get_vulnerabilities_from_threat(request, threat_id: int):
    vulnerabilities = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT threat_id FROM api_threatintelligence WHERE threat_id = %s", [threat_id])
        if not cursor.fetchone():
            return HttpResponse(
                status=404,
                content=json.dumps({"detail": "Threat not found"})
            )

        # Get associations
        cursor.execute("SELECT threat_id, vulnerability_id, notes FROM threat_incident_association WHERE vulnerability_id = %s",
            [threat_id]
        )

        for row in  cursor.fetchall():
            vulnerabilities.append({
                "threat_id": row[0],
                "vulnerability_id": row[1],
                "notes": row[2]
            })

    return vulnerabilities

@router.post("/vulnerabilities/", response=ThreatVulnerabilityAssociationSchema)
def add_vulnerability_to_threat(request, threat_vuln_data: ThreatVulnerabilityAssociationSchema):
    with connection.cursor() as cursor:
        # Verify that both threat and vulnerability exist
        cursor.execute("SELECT threat_id FROM api_threatintelligence WHERE threat_id = %s",
                       [threat_vuln_data.threat_id])
        if not cursor.fetchone():
            return HttpResponse(
                status=400,
                content=json.dumps({"detail": "Referenced threat not found"})
            )

        cursor.execute("SELECT vulnerability_id FROM api_vulnerability WHERE vulnerability_id = %s",
                       [threat_vuln_data.vulnerability_id])

        if not cursor.fetchone():
            return HttpResponse(
                status=400,
                content=json.dumps({"detail": "Referenced vulnerability not found"})
            )

        # Check if association already exists
        cursor.execute(
            "SELECT threat_id FROM threat_vulnerability_association WHERE threat_id = %s AND vulnerability_id = %s",
            [threat_vuln_data.threat_id, threat_vuln_data.vulnerability_id]
        )

        if cursor.fetchone():
            return HttpResponse(
                status=400,
                content=json.dumps({"detail": "Threat already associated with this vulnerability"})
            )

        # Create new association
        notes = threat_vuln_data.notes or ""
        cursor.execute(
            "INSERT INTO threat_vulnerability_association (threat_id, vulnerability_id, notes) VALUES (%s, %s, %s)",
            [threat_vuln_data.threat_id, threat_vuln_data.vulnerability_id, notes]
        )

    return threat_vuln_data

@router.put("/vulnerabilities/", response=ThreatVulnerabilityAssociationSchema)
def update_vulnerability_in_threat(request, threat_vuln_data: ThreatVulnerabilityAssociationSchema,
                                            original_threat_id: Optional[int] = None,
                                            original_vulnerability_id: Optional[int] = None):
    with connection.cursor() as cursor:
        # Check if we're updating an existing association
        if original_threat_id and original_vulnerability_id:
            # Verify that the new threat and vulnerability exist
            cursor.execute("SELECT threat_id FROM api_threatintelligence WHERE threat_id = %s",
                           [threat_vuln_data.threat_id])
            if not cursor.fetchone():
                return HttpResponse(
                    status=400,
                    content=json.dumps({"detail": "Referenced threat not found"})
                )

            cursor.execute("SELECT vulnerability_id FROM api_vulnerability WHERE vulnerability_id = %s",
                           [threat_vuln_data.vulnerability_id])
            if not cursor.fetchone():
                return HttpResponse(
                    status=400,
                    content=json.dumps({"detail": "Referenced vulnerability not found"})
                )

            # Verify the original association exists
            cursor.execute(
                "SELECT threat_id FROM threat_vulnerability_association WHERE threat_id = %s AND vulnerability_id = %s",
                [original_threat_id, original_vulnerability_id]
            )
            if not cursor.fetchone():
                return HttpResponse(
                    status=404,
                    content=json.dumps({"detail": "Original threat-vulnerability association not found"})
                )

            # Check if the new association would create a duplicate
            if (original_threat_id != threat_vuln_data.threat_id or
                    original_vulnerability_id != threat_vuln_data.vulnerability_id):
                cursor.execute(
                    "SELECT threat_id FROM threat_vulnerability_association WHERE threat_id = %s AND vulnerability_id = %s",
                    [threat_vuln_data.threat_id, threat_vuln_data.vulnerability_id]
                )
                if cursor.fetchone():
                    return HttpResponse(
                        status=400,
                        content=json.dumps({"detail": "This threat is already associated with this vulnerability"})
                    )

                # Update the association with new threat/vulnerability pair
                cursor.execute(
                    """DELETE FROM threat_vulnerability_association 
                       WHERE threat_id = %s AND vulnerability_id = %s""",
                    [original_threat_id, original_vulnerability_id]
                )

                notes = threat_vuln_data.notes if hasattr(threat_vuln_data, 'notes') else ""
                cursor.execute(
                    """INSERT INTO threat_vulnerability_association (threat_id, vulnerability_id, notes)
                       VALUES (%s, %s, %s)""",
                    [threat_vuln_data.threat_id, threat_vuln_data.vulnerability_id, notes]
                )
            else:
                # Just update notes for the same threat/vulnerability pair
                notes = threat_vuln_data.notes if hasattr(threat_vuln_data, 'notes') else ""
                cursor.execute(
                    "UPDATE threat_vulnerability_association SET notes = %s WHERE threat_id = %s AND vulnerability_id = %s",
                    [notes, original_threat_id, original_vulnerability_id]
                )
        else:
            # Just update notes for existing association
            cursor.execute(
                "SELECT threat_id FROM threat_vulnerability_association WHERE threat_id = %s AND vulnerability_id = %s",
                [threat_vuln_data.threat_id, threat_vuln_data.vulnerability_id]
            )
            if not cursor.fetchone():
                return HttpResponse(
                    status=404,
                    content=json.dumps({"detail": "Threat-vulnerability association not found"})
                )

            # Update just the notes
            notes = threat_vuln_data.notes if hasattr(threat_vuln_data, 'notes') else ""
            cursor.execute(
                "UPDATE threat_vulnerability_association SET notes = %s WHERE threat_id = %s AND vulnerability_id = %s",
                [notes, threat_vuln_data.threat_id, threat_vuln_data.vulnerability_id]
            )

    return threat_vuln_data

@router.delete("/vulnerabilities/{threat_id}/{vulnerability_id}")
def remove_vulnerability_from_threat(request, threat_id: int, vulnerability_id: int):
    # Check if association exists
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT threat_id FROM threat_vulnerability_association WHERE threat_id = %s AND vulnerability_id = %s",
            [threat_id, vulnerability_id]
        )
        if not cursor.fetchone():
            return HttpResponse(
                status=404,
                content=json.dumps({"detail": "Threat-vulnerability association not found"})
            )

        # Delete association
        cursor.execute(
            "DELETE FROM threat_vulnerability_association WHERE threat_id = %s AND vulnerability_id = %s",
            [threat_id, vulnerability_id]
        )

    return {"message": "Vulnerability removed from threat successfully"}