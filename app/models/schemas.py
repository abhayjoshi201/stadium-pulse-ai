"""
Pydantic Data Schemas for Stadium Pulse AI.

WHY: Strict schema enforcement ensures that every request entering the system and every JSON payload
emitted by the GenAI engine adheres strictly to contract definitions. This eliminates AI hallucinations,
prevents malformed concourse signage updates, and guarantees type safety across the entire stack.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class MatchPhase(str, Enum):
    """
    Enum representing the current lifecycle stage of a World Cup matchday.
    WHY: Distinct phases drastically change crowd flow physics and priority targets.
    """
    PRE_MATCH_INGRESS = "PRE_MATCH_INGRESS"       # -180m to kickoff: Turnstile throughput priority
    HALFTIME_SURGE = "HALFTIME_SURGE"             # Halftime window: Concourse concourse & restroom priority
    MATCH_IN_PROGRESS = "MATCH_IN_PROGRESS"       # Active gameplay: Corridor emergency access priority
    POST_MATCH_EGRESS = "POST_MATCH_EGRESS"       # +90m final whistle: Mass evacuation & transit metering priority


class UserRole(str, Enum):
    """
    Enum representing the operational role of the requester.
    WHY: Customizing response depth and terminology based on role ensures that top-level directors
    receive macro strategy while floor stewards receive immediate tactical actions.
    """
    OPERATIONS_DIRECTOR = "OPERATIONS_DIRECTOR"
    GATE_SUPERVISOR = "GATE_SUPERVISOR"
    STEWARD = "STEWARD"
    MEDICAL_OFFICER = "MEDICAL_OFFICER"


class IncidentType(str, Enum):
    """
    Enum representing reported bottlenecks or anomalies.
    WHY: Explicit anomaly categorization allows the AI to trigger specialized contingency protocols.
    """
    OVERCROWDING_BOTTLENECK = "OVERCROWDING_BOTTLENECK"
    TURNSTILE_JAM = "TURNSTILE_JAM"
    MEDICAL_EMERGENCY = "MEDICAL_EMERGENCY"
    WEATHER_ALERT = "WEATHER_ALERT"
    ACCESSIBILITY_OBSTRUCTION = "ACCESSIBILITY_OBSTRUCTION"
    NORMAL_FLOW = "NORMAL_FLOW"


class CrowdContextRequest(BaseModel):
    """
    Input schema representing the current multi-dimensional matchday context.
    WHY: Aggregating temporal, spatial, role, and telemetry data into a single structured input
    gives the GenAI core exact boundaries to synthesize highly localized decisions.
    """
    stadium_id: str = Field(
        default="metlife_stadium_ny_nj",
        description="Unique identifier for the target World Cup venue."
    )
    zone_id: str = Field(
        default="North_Gate_Concourse_Level_2_B4",
        description="Exact concourse sector, turnstile bank, or transit platform."
    )
    user_role: UserRole = Field(
        default=UserRole.GATE_SUPERVISOR,
        description="Operational role of the user querying the assistant."
    )
    match_phase: MatchPhase = Field(
        default=MatchPhase.PRE_MATCH_INGRESS,
        description="Current temporal phase of the matchday."
    )
    crowd_density_percentage: float = Field(
        default=85.0,
        ge=0.0,
        le=150.0,
        description="Real-time estimated crowd density percentage relative to safe operating limits."
    )
    incident_type: IncidentType = Field(
        default=IncidentType.NORMAL_FLOW,
        description="Primary incident or operational challenge currently detected."
    )
    additional_notes: Optional[str] = Field(
        default="",
        description="Optional field notes or real-time steward observations (e.g., 'Heavy rain driving fans indoors')."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "stadium_id": "metlife_stadium_ny_nj",
                "zone_id": "North_Gate_Concourse_Level_2_B4",
                "user_role": "GATE_SUPERVISOR",
                "match_phase": "PRE_MATCH_INGRESS",
                "crowd_density_percentage": 94.5,
                "incident_type": "OVERCROWDING_BOTTLENECK",
                "additional_notes": "Unexpected sudden downpour causing fans to stop right inside Gate C turnstiles."
            }
        }
    )


class RiskAssessment(BaseModel):
    """
    Sub-schema detailing the AI's risk evaluation.
    WHY: Separating risk assessment from action items provides transparency into the model's reasoning process.
    """
    risk_level: str = Field(
        description="Assessed risk level: LOW, MODERATE, HIGH, or CRITICAL."
    )
    bottleneck_probability: int = Field(
        ge=0,
        le=100,
        description="Probability (0-100%) of severe crush or delay occurring within the next 15 minutes."
    )
    root_cause_analysis: str = Field(
        description="Detailed explanation of what factors are compounding to create this situation."
    )


class StewardDirective(BaseModel):
    """
    Sub-schema defining a specific action item for floor personnel.
    WHY: Action items must be discrete, prioritized, and assignable to ensure rapid physical execution.
    """
    priority: int = Field(
        description="Execution priority order (1 = immediate life safety/bottleneck relief)."
    )
    assigned_target: str = Field(
        description="Who or what team should execute this step (e.g., 'Gate C Stewards', 'Mobile Medical Unit')."
    )
    action_instruction: str = Field(
        description="Exact step-by-step instruction to perform."
    )


class PublicAddressScript(BaseModel):
    """
    Sub-schema containing multilingual PA scripts.
    WHY: World Cup crowds are globally diverse. Providing ready-to-broadcast scripts in English, Spanish,
    and French ensures clear communication during high-stress concourse surges.
    """
    english: str = Field(description="English public address announcement calibrated for calm urgency.")
    spanish: str = Field(description="Spanish public address announcement (Español neutro / LATAM).")
    french: str = Field(description="French public address announcement (Français standard / Canadien).")


class CrowdActionPlanResponse(BaseModel):
    """
    Complete structured output schema generated by the GenAI decision core.
    WHY: This validated payload acts as the universal contract between our GenAI engine, our REST API,
    and our visual frontend dashboard or stadium IoT integrations.
    """
    stadium_id: str = Field(description="Echoed stadium identifier.")
    zone_id: str = Field(description="Echoed zone identifier.")
    timestamp_utc: str = Field(description="ISO-8601 UTC timestamp of decision generation.")
    risk_assessment: RiskAssessment = Field(description="Evaluation of current crowd risk.")
    steward_directives: List[StewardDirective] = Field(
        description="Ordered list of tactical actions for operations personnel."
    )
    digital_signage_payload: str = Field(
        description="Concise, high-contrast message (max 100 chars) for instant push to concourse LED screens."
    )
    pa_broadcast_scripts: PublicAddressScript = Field(
        description="Multilingual audio broadcast scripts for localized concourse speakers."
    )
    summary_for_role: str = Field(
        description="Tailored executive or tactical summary specifically formatted for the requester's role."
    )


class BatchCSVRequest(BaseModel):
    """
    Input schema representing a raw CSV payload string submitted by evaluators or sensor gateways.
    WHY: Facilitates functional batch testing of real stadium telemetry without requiring multipart form data complexity in simple REST clients.
    """
    csv_payload: str = Field(
        description="Raw CSV content with header row: zone_id,user_role,match_phase,crowd_density_percentage,incident_type,additional_notes"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "csv_payload": "zone_id,user_role,match_phase,crowd_density_percentage,incident_type,additional_notes\nNorth_Gate_Concourse_Level_2_B4,GATE_SUPERVISOR,PRE_MATCH_INGRESS,94.5,OVERCROWDING_BOTTLENECK,Gate jam\nTransit_Hub_Egress_Platform_West,MEDICAL_OFFICER,POST_MATCH_EGRESS,108.0,MEDICAL_EMERGENCY,Fainted fan"
            }
        }
    )

