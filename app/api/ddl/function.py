# app/api/views.py or appropriate file location
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_http_methods
import json


@require_http_methods(["GET"])
def get_risk_scores(request):
    """
    Endpoint to get risk scores for all open incidents, ordered by priority.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT row_to_json(r)
                FROM api_incident i
                CROSS JOIN LATERAL calculate_incident_risk_score(i.incident_id) r
                WHERE i.status IN ('open', 'investigating')
                ORDER BY r.risk_score DESC
            """)
            results = [json.loads(row[0]) for row in cursor.fetchall()]

        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)