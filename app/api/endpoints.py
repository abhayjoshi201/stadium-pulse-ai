"""
Aura-26 Stadium Pulse API Routers & Endpoints.

WHY: Exposing our context-aware GenAI engine via clean REST endpoints allows modular integration
with stadium concourse displays, mobile steward tablet apps, and central command center dashboards.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import CrowdContextRequest, CrowdActionPlanResponse
from app.services.ai_service import CrowdIntelligenceService, get_intelligence_service

router = APIRouter(prefix="/api/v1", tags=["Crowd Operations Intelligence"])


@router.post(
    "/crowd/analyze",
    response_model=CrowdActionPlanResponse,
    summary="Analyze Real-Time Crowd Telemetry & Generate GenAI Action Plan",
    description=(
        "Ingests temporal, spatial, role-based, and telemetry context vectors. "
        "Returns structured, localized tactical action plans, LED signage payloads, and multilingual PA scripts."
    )
)
async def analyze_crowd_context(
    request: CrowdContextRequest,
    service: CrowdIntelligenceService = Depends(get_intelligence_service)
) -> CrowdActionPlanResponse:
    """
    Primary GenAI analysis endpoint.
    WHY: Using dependency injection (`Depends`) ensures clean unit testing by allowing easy service mocking.
    """
    try:
        action_plan = await service.generate_crowd_action_plan(request)
        return action_plan
    except Exception as exc:
        # WHY: Catch-all safe error response prevents sensitive stack trace exposure while informing the client.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to synthesize crowd intelligence: {str(exc)}"
        )


@router.get(
    "/health",
    summary="System Health & Readiness Check",
    description="Returns current health status of the API and GenAI backend connectivity."
)
async def health_check(
    service: CrowdIntelligenceService = Depends(get_intelligence_service)
):
    """
    Health check endpoint.
    WHY: Essential for automated Kubernetes/Docker liveness probes during World Cup matchday operations.
    """
    is_ai_live = service.client is not None and bool(service.settings.gemini_api_key)
    return {
        "status": "ONLINE",
        "stadium_pulse_engine": "Aura-26 v1.0.0",
        "genai_live_mode": is_ai_live,
        "default_stadium": service.settings.default_stadium_id,
        "environment": service.settings.app_env
    }


@router.get(
    "/stadium/zones",
    summary="List Available Stadium Zones for Telemetry Simulation",
    description="Provides pre-configured World Cup stadium concourses and gates for dashboard interaction."
)
async def get_stadium_zones():
    """
    Returns standard concourses and gates.
    WHY: Pre-populating zones enables immediate, frictionless evaluation and demo capabilities on the UI.
    """
    return {
        "stadium_id": "metlife_stadium_ny_nj",
        "stadium_name": "MetLife Stadium (New York / New Jersey) - 82,500 Capacity",
        "zones": [
            {
                "zone_id": "North_Gate_Concourse_Level_2_B4",
                "name": "North Gate Concourse - Level 2 (Sector B4)",
                "type": "Turnstile & Ingress Bank",
                "normal_capacity": 4500
            },
            {
                "zone_id": "VIP_East_Turnstile_Bank_A",
                "name": "VIP East Turnstile Bank A",
                "type": "Express & Hospitality Gate",
                "normal_capacity": 1200
            },
            {
                "zone_id": "South_Concourse_Restrooms_Sector_C2",
                "name": "South Concourse Restroom & Concession Hub (Sector C2)",
                "type": "Halftime High-Density Area",
                "normal_capacity": 3800
            },
            {
                "zone_id": "Transit_Hub_Egress_Platform_West",
                "name": "Transit Hub & Shuttle Egress Platform (West Gate)",
                "type": "Post-Match Egress Bottleneck",
                "normal_capacity": 6500
            }
        ]
    }
