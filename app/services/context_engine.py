"""
Aura-26 Spatial & Contextual Enrichment Engine.

WHY: Pre-processing and enriching raw telemetry before LLM prompt injection ensures that
spatial rules, capacity thresholds, and crush-risk algorithms are computed deterministically.
This acts as a high-precision multiplier for GenAI accuracy, grounding AI reasoning in physical
World Cup stadium architecture.
"""

from typing import Dict, Any
from app.models.schemas import CrowdContextRequest, MatchPhase, IncidentType


class SpatialContextEngine:
    """
    Service class responsible for enriching spatial and architectural context,
    computing quantitative crush risk indexes, and deriving operational action modes.
    """

    # WHY: Pre-mapped stadium zone database grounds the AI in real-world 2026 venue layouts.
    ZONE_DATABASE: Dict[str, Dict[str, Any]] = {
        "North_Gate_Concourse_Level_2_B4": {
            "architectural_profile": "Turnstile Ingress Bank & Security Screening Concourse (Level 2)",
            "nominal_capacity": 4500,
            "bottleneck_sensitivity": 1.2,  # High sensitivity due to security checkpoint funnels
            "adjacent_overflow_zones": ["Gate C Express Lanes", "North-West Pedestrian Ramp"]
        },
        "VIP_East_Turnstile_Bank_A": {
            "architectural_profile": "Premium Hospitality & Express Entry Turnstile Bank",
            "nominal_capacity": 1200,
            "bottleneck_sensitivity": 0.8,
            "adjacent_overflow_zones": ["East Concourse Gate B", "Suite Access Elevator Bank 2"]
        },
        "South_Concourse_Restrooms_Sector_C2": {
            "architectural_profile": "Enclosed Interior Concourse, Restroom & Concession Hub",
            "nominal_capacity": 3800,
            "bottleneck_sensitivity": 1.5,  # Extreme sensitivity during halftime window
            "adjacent_overflow_zones": ["Upper Level 3 Concourse", "Stairwell Landing C-North"]
        },
        "Transit_Hub_Egress_Platform_West": {
            "architectural_profile": "Mass Transit Hub, Rail Platform & Accessible Shuttle Cart Bay",
            "nominal_capacity": 6500,
            "bottleneck_sensitivity": 1.8,  # Critical surge point during post-match egress
            "adjacent_overflow_zones": ["West Perimeter Holding Plaza", "Pedestrian Bridge 4"]
        }
    }

    @classmethod
    def enrich_context(cls, request: CrowdContextRequest) -> Dict[str, Any]:
        """
        Synthesizes raw request telemetry with quantitative risk calculations and spatial layouts.
        WHY: Provides explicit quantitative indexes (`crush_risk_index`) and architectural profiles
        so the GenAI model does not have to guess physical concourse characteristics.
        """
        zone_info = cls.ZONE_DATABASE.get(
            request.zone_id,
            {
                "architectural_profile": f"Standard Stadium Concourse Zone ({request.zone_id})",
                "nominal_capacity": 3000,
                "bottleneck_sensitivity": 1.0,
                "adjacent_overflow_zones": ["Adjacent Concourse Sector A", "Perimeter Gate B"]
            }
        )

        # Compute crush risk index based on density, sensitivity, phase, and incident
        density = request.crowd_density_percentage
        sensitivity = zone_info["bottleneck_sensitivity"]

        # Multipliers based on temporal match phase and reported incident
        phase_multiplier = 1.0
        if request.match_phase == MatchPhase.PRE_MATCH_INGRESS and "Turnstile" in zone_info["architectural_profile"]:
            phase_multiplier = 1.3
        elif request.match_phase == MatchPhase.HALFTIME_SURGE and "Restroom" in zone_info["architectural_profile"]:
            phase_multiplier = 1.5
        elif request.match_phase == MatchPhase.POST_MATCH_EGRESS and "Transit" in zone_info["architectural_profile"]:
            phase_multiplier = 1.6

        incident_multiplier = 1.0
        if request.incident_type in [IncidentType.OVERCROWDING_BOTTLENECK, IncidentType.TURNSTILE_JAM]:
            incident_multiplier = 1.4
        elif request.incident_type in [IncidentType.MEDICAL_EMERGENCY, IncidentType.ACCESSIBILITY_OBSTRUCTION]:
            incident_multiplier = 1.3
        elif request.incident_type == IncidentType.WEATHER_ALERT:
            incident_multiplier = 1.25

        # Compute composite numeric score (0 to 100+)
        raw_score = (density * sensitivity * phase_multiplier * incident_multiplier) / 1.5
        crush_risk_index = min(round(raw_score, 1), 150.0)

        # Determine qualitative action mode
        if crush_risk_index >= 95.0 or request.incident_type == IncidentType.MEDICAL_EMERGENCY:
            action_mode = "EMERGENCY_CLEARANCE_AND_PULSE_METERING"
        elif crush_risk_index >= 75.0 or request.incident_type == IncidentType.TURNSTILE_JAM:
            action_mode = "DYNAMIC_REROUTE_AND_QUEUE_BUFFERING"
        elif crush_risk_index >= 55.0:
            action_mode = "ACTIVE_MONITORING_AND_WAYFINDING"
        else:
            action_mode = "STANDARD_OPERATIONAL_FLOW"

        return {
            "crush_risk_index": crush_risk_index,
            "recommended_action_mode": action_mode,
            "zone_architectural_profile": zone_info["architectural_profile"],
            "nominal_capacity": zone_info["nominal_capacity"],
            "adjacent_overflow_zones": zone_info["adjacent_overflow_zones"],
            "phase_multiplier": phase_multiplier,
            "incident_multiplier": incident_multiplier
        }
