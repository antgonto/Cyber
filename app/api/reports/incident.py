from django.db import connection
from django.http import JsonResponse
from datetime import datetime, timedelta
import json


def generate_incident_report(incident_id):
    """
    Generate a comprehensive security incident report with detailed information
    from the incident_management_dashboard view and additional metrics.

    Args:
        incident_id (int): ID of the incident to generate report for

    Returns:
        dict: Complete incident report with detailed analysis and recommendations
    """
    try:
        # Get basic incident information from the dashboard view
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM incident_management_dashboard
                WHERE incident_id = %s
            """, [incident_id])

            columns = [col[0] for col in cursor.description]
            incident_data = dict(zip(columns, cursor.fetchone() or []))

            if not incident_data:
                return {"error": f"Incident with ID {incident_id} not found"}

            # Get historical incident metrics for comparison
            cursor.execute("""
                SELECT 
                    AVG(resolution_time_hours) as avg_resolution_time,
                    MAX(affected_assets_count) as max_affected_assets
                FROM incident_management_dashboard
                WHERE incident_severity = %s AND incident_id != %s
            """, [incident_data["incident_severity"], incident_id])

            columns = [col[0] for col in cursor.description]
            historical_metrics = dict(zip(columns, cursor.fetchone() or []))

            # Get recent similar incidents
            cursor.execute("""
                SELECT 
                    incident_id, 
                    incident_type, 
                    incident_severity, 
                    resolution_time_hours,
                    reported_date
                FROM incident_management_dashboard
                WHERE incident_severity = %s 
                AND incident_id != %s
                ORDER BY reported_date DESC
                LIMIT 5
            """, [incident_data["incident_severity"], incident_id])

            columns = [col[0] for col in cursor.description]
            similar_incidents = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # Get assigned personnel's workload
            if incident_data.get("assigned_user_id"):
                cursor.execute("""
                    SELECT COUNT(*) as open_incidents
                    FROM api_incident
                    WHERE assigned_to_id = %s
                    AND status IN ('open', 'investigating')
                """, [incident_data["assigned_user_id"]])

                assigned_workload = cursor.fetchone()[0]
            else:
                assigned_workload = 0

            # Get vulnerability patch status if applicable
            if incident_data.get("related_vulnerabilities_count", 0) > 0:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_vulnerabilities,
                        SUM(CASE WHEN v.patch_available THEN 1 ELSE 0 END) as patchable_count
                    FROM asset_vulnerabilities av
                    JOIN api_vulnerability v ON av.vulnerability_id = v.vulnerability_id
                    JOIN incident_assets ia ON ia.asset_id = av.asset_id
                    WHERE ia.incident_id = %s
                """, [incident_id])

                vulnerability_stats = dict(
                    zip(['total_vulnerabilities', 'patchable_count'], cursor.fetchone() or [0, 0]))
            else:
                vulnerability_stats = {"total_vulnerabilities": 0, "patchable_count": 0}

        # Calculate additional metrics
        metrics = {
            "time_since_reported": _format_time_difference(incident_data.get("reported_date")),
            "time_to_resolution": _format_time_difference(incident_data.get("reported_date"),
                                                          incident_data.get("resolved_date")),
            "performance_vs_average": _calculate_performance(incident_data.get("resolution_time_hours"),
                                                             historical_metrics.get("avg_resolution_time"))
        }

        # Generate recommendations based on the incident data
        recommendations = _generate_recommendations(
            incident_data,
            historical_metrics,
            vulnerability_stats
        )

        # Create the complete report
        report = {
            "incident_details": incident_data,
            "historical_comparison": historical_metrics,
            "similar_incidents": similar_incidents,
            "assigned_personnel_workload": assigned_workload,
            "vulnerability_metrics": vulnerability_stats,
            "additional_metrics": metrics,
            "recommendations": recommendations,
            "report_generated": datetime.now().isoformat(),
        }

        return report

    except Exception as e:
        return {"error": str(e)}


def _format_time_difference(start_time, end_time=None):
    """Format time difference between two timestamps"""
    if not start_time:
        return "Unknown"

    if isinstance(start_time, str):
        start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))

    if end_time and isinstance(end_time, str):
        end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))

    end = end_time or datetime.now()

    diff = end - start_time
    hours = diff.total_seconds() / 3600

    if hours < 1:
        return f"{int(diff.total_seconds() / 60)} minutes"
    elif hours < 24:
        return f"{int(hours)} hours"
    else:
        return f"{int(hours / 24)} days, {int(hours % 24)} hours"


def _calculate_performance(current_time, average_time):
    """Calculate performance compared to average resolution time"""
    if not current_time or not average_time:
        return "Insufficient data"

    diff_percent = ((average_time - current_time) / average_time) * 100

    if diff_percent > 20:
        return f"{abs(int(diff_percent))}% faster than average"
    elif diff_percent < -20:
        return f"{abs(int(diff_percent))}% slower than average"
    else:
        return "Within average resolution time"


def _generate_recommendations(incident_data, historical_metrics, vulnerability_stats):
    """Generate recommendations based on incident data"""
    recommendations = []

    # Check if incident is taking longer than average
    if (incident_data.get("incident_status") in ["open", "investigating"] and
            incident_data.get("resolution_time_hours") and
            historical_metrics.get("avg_resolution_time") and
            incident_data["resolution_time_hours"] > historical_metrics["avg_resolution_time"] * 1.2):
        recommendations.append({
            "priority": "high",
            "action": "Escalate incident",
            "reason": "Resolution time exceeding historical average by more than 20%"
        })

    # Check if critical incident is unassigned
    if incident_data.get("incident_severity") == "critical" and not incident_data.get("assigned_user_id"):
        recommendations.append({
            "priority": "urgent",
            "action": "Assign incident to security manager",
            "reason": "Critical incident remains unassigned"
        })

    # Recommendation for vulnerabilities with available patches
    if (vulnerability_stats.get("total_vulnerabilities", 0) > 0 and
            vulnerability_stats.get("patchable_count", 0) > 0):
        recommendations.append({
            "priority": "medium",
            "action": "Apply available patches",
            "reason": f"{vulnerability_stats['patchable_count']} of {vulnerability_stats['total_vulnerabilities']} vulnerabilities have patches available"
        })

    # Check for high number of assets affected
    if (incident_data.get("affected_assets_count", 0) > 3 and
            incident_data.get("highest_asset_criticality") in ["high", "critical"]):
        recommendations.append({
            "priority": "high",
            "action": "Implement containment strategy",
            "reason": f"Multiple high criticality assets affected ({incident_data['affected_assets_count']})"
        })

    # Check for threat intelligence with high confidence
    if incident_data.get("highest_threat_confidence") in ["high", "very_high"]:
        recommendations.append({
            "priority": "medium",
            "action": "Review threat intelligence",
            "reason": f"High confidence threat intelligence associated with this incident"
        })

    # Add generic recommendation if none were generated
    if not recommendations:
        recommendations.append({
            "priority": "low",
            "action": "Follow standard operating procedure",
            "reason": "No specific recommendations identified"
        })

    return recommendations