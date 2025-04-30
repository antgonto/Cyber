# app/api/risk/api.py
from ninja import Router, Schema
from typing import List, Dict, Optional
from .services import get_incident_risk_score, get_all_open_incident_risk_scores

router = Router()


class RiskFactors(Schema):
    asset_factor: float
    vulnerability_factor: float
    threat_factor: float
    alert_factor: float
    time_factor: float


class RiskScoreResponse(Schema):
    incident_id: int
    incident_type: str
    severity: str
    risk_score: float
    risk_factors: RiskFactors
    recommended_action: str


@router.get("/{incident_id}/", response={200: RiskScoreResponse, 404: Dict})
def get_risk_score(request, incident_id: int):
    """Get the risk score for a specific incident."""
    result = get_incident_risk_score(incident_id)

    if not result:
        return 404, {"error": f"Incident with ID {incident_id} not found"}

    return 200, result


@router.get("/", response=List[RiskScoreResponse])
def get_all_risk_scores(request):
    """Get risk scores for all open incidents, ordered by priority."""
    return get_all_open_incident_risk_scores()