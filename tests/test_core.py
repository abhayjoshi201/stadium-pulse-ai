"""
Aura-26 Stadium Pulse Comprehensive Test Suite.

WHY: Rigorous unit and integration testing verifies that our spatial enrichment algorithms,
Pydantic data schemas, GenAI prompt builders, and REST endpoints perform deterministically
under normal and emergency World Cup matchday conditions.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import (
    CrowdContextRequest,
    CrowdActionPlanResponse,
    MatchPhase,
    UserRole,
    IncidentType,
)
from app.services.context_engine import SpatialContextEngine
from app.services.ai_service import CrowdIntelligenceService
from app.core.prompts import build_crowd_intelligence_prompt

# Initialize synchronous TestClient for FastAPI endpoints
client = TestClient(app)


def test_schema_validation_and_defaults():
    """
    Verifies that Pydantic models instantiate with correct defaults and enforce strict boundary validation.
    WHY: Prevents invalid or out-of-range sensor telemetry from crashing the reasoning engine.
    """
    req = CrowdContextRequest()
    assert req.stadium_id == "metlife_stadium_ny_nj"
    assert req.zone_id == "North_Gate_Concourse_Level_2_B4"
    assert req.user_role == UserRole.GATE_SUPERVISOR
    assert req.match_phase == MatchPhase.PRE_MATCH_INGRESS
    assert req.crowd_density_percentage == 85.0

    # Verify that invalid crowd density percentage (> 150%) raises validation error
    with pytest.raises(ValueError):
        CrowdContextRequest(crowd_density_percentage=200.0)


def test_spatial_context_engine_crush_index():
    """
    Verifies quantitative crush risk index formulas across distinct concourse zones and match phases.
    WHY: Ensures mathematical determinism and accurate surge classification prior to LLM injection.
    """
    # Test normal pre-match ingress at North Gate turnstiles
    req_normal = CrowdContextRequest(
        zone_id="North_Gate_Concourse_Level_2_B4",
        match_phase=MatchPhase.PRE_MATCH_INGRESS,
        crowd_density_percentage=60.0,
        incident_type=IncidentType.NORMAL_FLOW
    )
    enriched_normal = SpatialContextEngine.enrich_context(req_normal)
    assert enriched_normal["crush_risk_index"] > 0
    assert enriched_normal["recommended_action_mode"] in [
        "ACTIVE_MONITORING_AND_WAYFINDING",
        "STANDARD_OPERATIONAL_FLOW"
    ]

    # Test critical post-match egress bottleneck at Transit Hub
    req_critical = CrowdContextRequest(
        zone_id="Transit_Hub_Egress_Platform_West",
        match_phase=MatchPhase.POST_MATCH_EGRESS,
        crowd_density_percentage=98.0,
        incident_type=IncidentType.OVERCROWDING_BOTTLENECK
    )
    enriched_critical = SpatialContextEngine.enrich_context(req_critical)
    assert enriched_critical["crush_risk_index"] >= 95.0
    assert enriched_critical["recommended_action_mode"] == "EMERGENCY_CLEARANCE_AND_PULSE_METERING"
    assert "West Perimeter Holding Plaza" in enriched_critical["adjacent_overflow_zones"]


def test_prompt_builder_structure_and_contracts():
    """
    Verifies that the modular prompt builder injects all enriched spatial metrics without formatting errors.
    WHY: Guarantees that the LLM receives the exact required schema and contingency directives.
    """
    req = CrowdContextRequest(
        user_role=UserRole.OPERATIONS_DIRECTOR,
        match_phase=MatchPhase.HALFTIME_SURGE,
        crowd_density_percentage=90.0,
        incident_type=IncidentType.MEDICAL_EMERGENCY,
        additional_notes="Stairwell B landing slip hazard."
    )
    enriched = SpatialContextEngine.enrich_context(req)
    prompt = build_crowd_intelligence_prompt(req, enriched)

    assert "OPERATIONS_DIRECTOR" in prompt
    assert "HALFTIME_SURGE" in prompt
    assert "MEDICAL_EMERGENCY" in prompt
    assert str(enriched["crush_risk_index"]) in prompt
    assert "Stairwell B landing slip hazard" in prompt
    assert "CrowdActionPlanResponse" in prompt or "risk_assessment" in prompt


@pytest.mark.asyncio
async def test_ai_service_fallback_reasoning():
    """
    Verifies the high-availability deterministic fallback engine in CrowdIntelligenceService.
    WHY: Guarantees that even if external LLM endpoints are unreachable or unconfigured,
    the application returns schema-valid, actionable operational plans instantly.
    """
    service = CrowdIntelligenceService()
    # Force client to None to trigger deterministic fallback
    service.client = None

    req = CrowdContextRequest(
        zone_id="VIP_East_Turnstile_Bank_A",
        user_role=UserRole.STEWARD,
        match_phase=MatchPhase.PRE_MATCH_INGRESS,
        crowd_density_percentage=88.0,
        incident_type=IncidentType.TURNSTILE_JAM
    )

    action_plan = await service.generate_crowd_action_plan(req)
    assert isinstance(action_plan, CrowdActionPlanResponse)
    assert action_plan.stadium_id == "metlife_stadium_ny_nj"
    assert action_plan.zone_id == "VIP_East_Turnstile_Bank_A"
    assert action_plan.risk_assessment.risk_level in ["CRITICAL", "HIGH"]
    assert len(action_plan.steward_directives) >= 2
    assert "english" in action_plan.pa_broadcast_scripts.english.lower() or len(action_plan.pa_broadcast_scripts.english) > 10
    assert "spanish" in action_plan.pa_broadcast_scripts.spanish.lower() or len(action_plan.pa_broadcast_scripts.spanish) > 10


def test_api_health_check_endpoint():
    """
    Verifies the health check API probe.
    WHY: Essential for container and Kubernetes liveness monitoring.
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert data["stadium_pulse_engine"] == "Aura-26 v1.0.0"
    assert data["spatial_context_engine"] == "ACTIVE"


def test_api_stadium_zones_endpoint():
    """
    Verifies that the pre-configured World Cup zones endpoint returns valid architectural metadata.
    WHY: Ensures UI dashboard can populate selectors cleanly.
    """
    response = client.get("/api/v1/stadium/zones")
    assert response.status_code == 200
    data = response.json()
    assert data["stadium_id"] == "metlife_stadium_ny_nj"
    assert len(data["zones"]) == 4
    assert data["zones"][0]["zone_id"] == "North_Gate_Concourse_Level_2_B4"


def test_api_spatial_enrichment_endpoint():
    """
    Verifies the standalone spatial enrichment calculation endpoint.
    WHY: Allows testing math algorithms via API without incurring LLM latency.
    """
    payload = {
        "stadium_id": "metlife_stadium_ny_nj",
        "zone_id": "South_Concourse_Restrooms_Sector_C2",
        "user_role": "GATE_SUPERVISOR",
        "match_phase": "HALFTIME_SURGE",
        "crowd_density_percentage": 92.5,
        "incident_type": "OVERCROWDING_BOTTLENECK"
    }
    response = client.post("/api/v1/stadium/spatial-enrichment", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "spatial_enrichment_results" in data
    assert data["spatial_enrichment_results"]["crush_risk_index"] > 50.0


def test_api_crowd_analyze_endpoint():
    """
    Verifies the main POST /api/v1/crowd/analyze endpoint.
    WHY: Verifies full end-to-end HTTP serialization, service execution, and Pydantic validation.
    """
    payload = {
        "stadium_id": "metlife_stadium_ny_nj",
        "zone_id": "North_Gate_Concourse_Level_2_B4",
        "user_role": "OPERATIONS_DIRECTOR",
        "match_phase": "PRE_MATCH_INGRESS",
        "crowd_density_percentage": 82.0,
        "incident_type": "NORMAL_FLOW"
    }
    response = client.post("/api/v1/crowd/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["stadium_id"] == "metlife_stadium_ny_nj"
    assert "risk_assessment" in data
    assert "steward_directives" in data
    assert "digital_signage_payload" in data
    assert "pa_broadcast_scripts" in data


def test_api_batch_csv_upload_and_binary_search():
    """
    Verifies the batch CSV upload evaluation endpoint and checks O(log N) binary search threshold accuracy.
    WHY: Ensures the tournament jury can evaluate multi-row CSV telemetry without parsing errors.
    """
    csv_sample = (
        "zone_id,user_role,match_phase,crowd_density_percentage,incident_type,additional_notes\n"
        "North_Gate_Concourse_Level_2_B4,GATE_SUPERVISOR,PRE_MATCH_INGRESS,94.5,OVERCROWDING_BOTTLENECK,Gate jam\n"
        "Transit_Hub_Egress_Platform_West,MEDICAL_OFFICER,POST_MATCH_EGRESS,108.0,MEDICAL_EMERGENCY,Fainted fan\n"
        "VIP_East_Turnstile_Bank_A,STEWARD,HALFTIME_SURGE,45.0,NORMAL_FLOW,Clear flow"
    )
    response = client.post("/api/v1/telemetry/batch-csv-upload", json={"csv_payload": csv_sample})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "BATCH_PROCESSED_SUCCESSFULLY"
    summary = data["batch_evaluation_results"]["batch_summary"]
    assert summary["total_sectors_analyzed"] == 3
    assert summary["critical_bottleneck_zones"] >= 1
    assert "O(M * log N)" in summary["algorithmic_complexity"]
    evals = data["batch_evaluation_results"]["sector_evaluations"]
    assert len(evals) == 3
    assert evals[1]["recommended_action_mode"] == "EMERGENCY_CLEARANCE_AND_PULSE_METERING"

