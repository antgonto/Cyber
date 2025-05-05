from typing import Optional, Dict, List

from django.http import JsonResponse

from ninja import Router, Schema

from psycopg import OperationalError

from app.api.common.utils import get_connection

router = Router(tags=["risk"])

# Response model for risk score data
class RiskScoreResponse(Schema):
    incident_id:  Optional[int] = None
    incident_type: Optional[str] = None
    severity: Optional[str] = None
    risk_score: Optional[float] = None
    risk_factors: Optional[Dict] = None
    recommended_action: Optional[str] = None

class SimpleMessage(Schema):
    success: bool
    detail: str


@router.get("/risk_scores/")
def get_risk_scores(request):
    """
    Endpoint to get risk scores for all open incidents, ordered by priority.
    """
    try:
        # First ensure the risk score function exists
        create_result = create_risk_score_function(request)
        if not create_result.get("success", False):
            return JsonResponse({"error": "Could not create risk score function"}, status=500)
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT i.incident_id, i.incident_type, i.severity, 
                       f.risk_score, f.risk_factors, f.recommended_action
                FROM api_incident i
                CROSS JOIN LATERAL (
                    SELECT * FROM public.calculate_incident_risk_score(i.incident_id)
                ) AS f
                WHERE i.status IN ('open', 'investigating')
                ORDER BY f.risk_score DESC            
            """)
            results = cursor.fetchall()
            results_list = []
            for r in results:
                results_list.append({
                    "incident_id": r[0],
                    "incident_type": r[1],
                    "severity": r[2],
                    "risk_score": float(r[3]),
                    "risk_factors": r[4],
                    "recommended_action": r[5]
                })
        return JsonResponse(results_list, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@router.post("/create_risk_score_function/", response=SimpleMessage)
def create_risk_score_function(request) -> Dict:
    """Creates the calculate_incident_risk_score function in PostgreSQL"""
    try:

        # First check if function already exists
        check_sql = """
        SELECT COUNT(*) FROM pg_proc 
        WHERE proname = 'calculate_incident_risk_score'
        """
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(check_sql)
            function_exists = cur.fetchone()[0] > 0

        create_sql = """
        CREATE OR REPLACE FUNCTION public.calculate_incident_risk_score(p_incident_id INTEGER)
        RETURNS TABLE (
            incident_id        INTEGER,
            incident_type      VARCHAR,
            severity           VARCHAR,
            risk_score         NUMERIC(5,2),
            risk_factors       JSONB,
            recommended_action VARCHAR
        )
        LANGUAGE plpgsql AS $$
        DECLARE
            -- rename the timestamp var so it doesn't clash
            v_now       TIMESTAMP   := NOW();
            v_severity  VARCHAR;
            asset_factor      NUMERIC(5,2) := 0;
            vuln_factor       NUMERIC(5,2) := 0;
            threat_factor     NUMERIC(5,2) := 0;
            alert_factor      NUMERIC(5,2) := 0;
            time_factor       NUMERIC(5,2) := 0;
            base_score        NUMERIC(5,2);
            risk_factors_json JSONB;
        BEGIN
            -- grab the incident's severity
            SELECT i.severity
              INTO v_severity
            FROM api_incident i
            WHERE i.incident_id = p_incident_id;            

            -- CASE expression to set base_score
            base_score := CASE v_severity
                WHEN 'critical' THEN 80
                WHEN 'high'     THEN 60
                WHEN 'medium'   THEN 40
                WHEN 'low'      THEN 20
                ELSE 10
            END;

            -- asset factor
            SELECT
              CASE WHEN COUNT(*) = 0 THEN 0
                   ELSE 5 * COUNT(*) *
                       CASE
                         WHEN MAX(a.criticality_level) = 'critical' THEN 2
                         WHEN MAX(a.criticality_level) = 'high'     THEN 1.5
                         WHEN MAX(a.criticality_level) = 'medium'   THEN 1
                         ELSE 0.5
                       END
              END
              INTO asset_factor
            FROM incident_assets ia
            JOIN api_asset a ON a.asset_id = ia.asset_id
            WHERE ia.incident_id = p_incident_id;
            asset_factor := LEAST(asset_factor, 50);

            -- vulnerability factor
            SELECT
              CASE WHEN COUNT(*) = 0 THEN 0
                   ELSE 3 * COUNT(*) *
                       CASE
                         WHEN bool_or(v.severity = 'critical') THEN 2
                         WHEN bool_or(v.severity = 'high')     THEN 1.5
                         ELSE 1
                       END
              END
              INTO vuln_factor
            FROM incident_assets ia
            JOIN asset_vulnerabilities av ON av.asset_id = ia.asset_id
            JOIN api_vulnerability v ON v.vulnerability_id = av.vulnerability_id
            WHERE ia.incident_id = p_incident_id;
            vuln_factor := LEAST(vuln_factor, 40);

            -- threat intelligence factor
            SELECT
              CASE WHEN COUNT(*) = 0 THEN 0
                   ELSE 10 * COUNT(*) *
                       CASE
                         WHEN MAX(ti.confidence_level) = 'very_high' THEN 1.5
                         WHEN MAX(ti.confidence_level) = 'high'      THEN 1.0
                         WHEN MAX(ti.confidence_level) = 'medium'    THEN 0.5
                         ELSE 0.25
                       END
              END
              INTO threat_factor
            FROM threat_incident_association tia
            JOIN api_threatintelligence ti ON ti.threat_id = tia.threat_id
            WHERE tia.incident_id = p_incident_id;
            threat_factor := LEAST(threat_factor, 30);

            -- alert factor
            SELECT
              CASE WHEN COUNT(*) = 0 THEN 0
                   ELSE 5 * COUNT(*) *
                       CASE
                         WHEN bool_or(a.severity = 'critical') THEN 2
                         WHEN bool_or(a.severity = 'high')     THEN 1.5
                         WHEN bool_or(a.severity = 'medium')   THEN 1
                         ELSE 0.5
                       END
              END
              INTO alert_factor
            FROM api_alert a
            WHERE a.incident_id = p_incident_id;
            alert_factor := LEAST(alert_factor, 30);

            -- time factor (days since reported, capped at 30)
            SELECT
              CASE WHEN status IN ('resolved','closed') THEN 0
                   ELSE LEAST(
                       EXTRACT(EPOCH FROM (v_now - reported_date)) / 86400,
                       30
                   )
              END
              INTO time_factor
            FROM api_incident i
            WHERE i.incident_id = p_incident_id;

            -- assemble JSON
            risk_factors_json := jsonb_build_object(
                'asset_factor',         asset_factor,
                'vulnerability_factor', vuln_factor,
                'threat_factor',        threat_factor,
                'alert_factor',         alert_factor,
                'time_factor',          time_factor
            );

            -- final RETURN QUERY
            RETURN QUERY
            SELECT
                i.incident_id,
                i.incident_type,
                i.severity,
                LEAST(
                    base_score + asset_factor + vuln_factor
                  + threat_factor + alert_factor + time_factor,
                    100
                )::NUMERIC(5,2) AS risk_score,
                risk_factors_json,
                CASE
                  WHEN base_score + asset_factor + vuln_factor
                     + threat_factor + alert_factor + time_factor >= 90
                    THEN 'Immediate executive response required'::VARCHAR
                  WHEN base_score + asset_factor + vuln_factor
                     + threat_factor + alert_factor + time_factor >= 75
                    THEN 'Escalate to security manager'::VARCHAR
                  WHEN base_score + asset_factor + vuln_factor
                     + threat_factor + alert_factor + time_factor >= 50
                    THEN 'Assign to dedicated analyst'::VARCHAR
                  ELSE 'Follow standard procedures'::VARCHAR
                END AS recommended_action                
            FROM api_incident i
            WHERE i.incident_id = p_incident_id;
        END;
        $$;
        """

        with conn.cursor() as cur:
            cur.execute(create_sql)
        conn.commit()

        # Verify function creation was successful
        with conn.cursor() as cur:
            cur.execute("SELECT proname FROM pg_proc WHERE proname = 'calculate_incident_risk_score'")
            if cur.fetchone() is None:
                conn.close()
                return {"success": False, "detail": "Function creation failed - not found after creation"}

        conn.close()
        status = "updated" if function_exists else "created"
        return {"success": True, "detail": f"Risk score function successfully {status}"}
    except OperationalError as e:
        return {"success": False, "detail": f"Database operation failed: {str(e)}"}
    except Exception as e:
        return {"success": False, "detail": f"Unexpected error: {str(e)}"}


@router.get("/risk_score/{incident_id}", response=RiskScoreResponse)
def calculate_risk_score(request, incident_id: int):
    """
    Calculates the risk score for a specific incident based on multiple factors.
    """
    try:
        # First ensure the risk score function exists
        create_result = create_risk_score_function(request)
        if not create_result.get("success", False):
            return JsonResponse({"error": "Could not create risk score function"}, status=500)

        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM public.calculate_incident_risk_score(%s)", (incident_id,))
            result = cursor.fetchone()

            if not result:
                return JsonResponse({"error": "Incident not found"}, status=404)

            # Map to response object
            response = {
                "incident_id": result[0],
                "incident_type": result[1],
                "severity": result[2],
                "risk_score": float(result[3]),
                "risk_factors": result[4],
                "recommended_action": result[5]
            }

        conn.close()
        return response
    except OperationalError as e:
        return JsonResponse({"error": f"Database operation failed: {str(e)}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)
    finally:
        if 'conn' in locals() and conn:
            conn.close()

@router.get("/risk_scores/open/", response=List[RiskScoreResponse])
def list_open_incident_risk_scores(request):
    """
    Lists risk scores for all open incidents, ordered by priority (highest risk first).
    """
    try:
        # First ensure the risk score function exists
        create_result = create_risk_score_function(request)
        if not create_result.get("success", False):
            return JsonResponse({"error": "Could not create risk score function"}, status=500)

        conn = get_connection()

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT r.*
                FROM api_incident i
                CROSS JOIN LATERAL (
                    SELECT * FROM public.calculate_incident_risk_score(i.incident_id)
                ) AS r                
                WHERE i.status IN ('open', 'investigating')
                ORDER BY r.risk_score DESC
            """)
            results = cursor.fetchall()

            # Map to response objects
            response = []
            for row in results:
                response.append({
                    "incident_id": row[0],
                    "incident_type": row[1],
                    "severity": row[2],
                    "risk_score": float(row[3]),
                    "risk_factors": row[4],
                    "recommended_action": row[5]
                })

        conn.close()
        return response
    except OperationalError as e:
        return JsonResponse({"error": f"Database operation failed: {str(e)}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)
    finally:
        if 'conn' in locals() and conn:
                conn.close()