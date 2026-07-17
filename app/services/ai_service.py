"""
Stadium Pulse AI GenAI Crowd Intelligence Service Layer.

WHY: Abstracting GenAI interaction into a dedicated async service class decouples prompt engineering
and API call retry logic from the REST controllers. It also provides multi-layer fallback resilience,
combining Google GenAI structured outputs with spatial context enrichment and deterministic algorithms
for high-availability World Cup stadium operations while enforcing strict cyclomatic complexity boundaries.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple

from app.core.config import get_settings
from app.core.prompts import SYSTEM_INSTRUCTION_STADIUM_PULSE, build_crowd_intelligence_prompt
from app.services.context_engine import SpatialContextEngine
from app.models.schemas import (
    CrowdContextRequest,
    CrowdActionPlanResponse,
    RiskAssessment,
    StewardDirective,
    PublicAddressScript,
    IncidentType,
)
from app.utils.constants import (
    DEFAULT_CRUSH_INDEX,
    ACTION_MODE_STANDARD,
    DEFAULT_OVERFLOW_TARGET,
    RISK_LEVEL_CRITICAL,
    RISK_LEVEL_HIGH,
    RISK_LEVEL_MODERATE,
    RISK_LEVEL_LOW,
    CRUSH_INDEX_THRESHOLDS,
)
from app.utils.helpers import extract_clean_json_from_markdown

logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types
    GENAI_SDK_AVAILABLE = True
except ImportError:
    GENAI_SDK_AVAILABLE = False


class CrowdIntelligenceService:
    """
    Service class responsible for ingesting crowd context vectors, enriching spatial data,
    interacting with Google Gemini GenAI models, and guaranteeing type-safe structured responses.
    """

    def __init__(self) -> None:
        """
        Initializes the service with validated application settings and instantiates the Gemini SDK client if available.

        WHY: Fails open to fallback reasoning if credentials are unconfigured or SDK missing.
        """
        self.settings = get_settings()
        self.client: Optional[genai.Client] = None

        if GENAI_SDK_AVAILABLE and self.settings.gemini_api_key:
            try:
                self.client = genai.Client(api_key=self.settings.gemini_api_key)
            except Exception as exc:
                logger.warning(f"Failed to initialize Google GenAI Client: {exc}")

    async def generate_crowd_action_plan(
        self, context: CrowdContextRequest
    ) -> CrowdActionPlanResponse:
        """
        Main entry point for generating a structured crowd action plan from user & stadium context.

        Args:
            context (CrowdContextRequest): The multi-dimensional temporal, spatial, role, and sensor input vector.

        Returns:
            CrowdActionPlanResponse: Validated tactical directives, LED signage payload, and multilingual PA scripts.

        WHY: Enriches raw telemetry with spatial index metrics before calling external LLMs or fallback logic.
        """
        enriched_telemetry: Dict[str, Any] = SpatialContextEngine.enrich_context(context)

        if not self.client or not self.settings.gemini_api_key:
            return self._fallback_deterministic_reasoning(
                context,
                enriched_telemetry,
                reason="API_KEY_MISSING_OR_CLIENT_UNAVAILABLE",
            )

        prompt_payload: str = build_crowd_intelligence_prompt(context, enriched_telemetry)

        try:
            response = self.client.models.generate_content(
                model=self.settings.ai_model_name,
                contents=[
                    types.Part.from_text(text=SYSTEM_INSTRUCTION_STADIUM_PULSE),
                    types.Part.from_text(text=prompt_payload),
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=CrowdActionPlanResponse,
                    temperature=0.2,
                ),
            )
            response_json: Dict[str, Any] = json.loads(response.text)
            return CrowdActionPlanResponse.model_validate(response_json)
        except Exception as primary_error:
            logger.warning(
                f"Primary structured GenAI generation failed ({primary_error}). Attempting secondary JSON parsing..."
            )
            return self._execute_secondary_genai_parsing(prompt_payload, context, enriched_telemetry, primary_error)

    def _execute_secondary_genai_parsing(
        self,
        prompt_payload: str,
        context: CrowdContextRequest,
        enriched: Dict[str, Any],
        primary_error: Exception,
    ) -> CrowdActionPlanResponse:
        """
        Executes secondary fallback GenAI text generation with markdown stripping if structured schema fails.

        Args:
            prompt_payload (str): Formatted user prompt.
            context (CrowdContextRequest): Original request payload.
            enriched (Dict[str, Any]): Enriched spatial calculations.
            primary_error (Exception): The error encountered during primary generation.

        Returns:
            CrowdActionPlanResponse: Parsed or fallback response.

        WHY: Isolating fallback retry logic guarantees early return boundaries and keeps cyclomatic complexity low.
        """
        if not self.client:
            return self._fallback_deterministic_reasoning(context, enriched, reason=f"LLM_EXECUTION_FALLBACK ({primary_error})")
        try:
            raw_response = self.client.models.generate_content(
                model=self.settings.ai_model_name,
                contents=prompt_payload,
                config=types.GenerateContentConfig(temperature=0.2),
            )
            cleaned_json_text: str = extract_clean_json_from_markdown(raw_response.text)
            return CrowdActionPlanResponse.model_validate_json(cleaned_json_text)
        except Exception as secondary_error:
            logger.error(f"Secondary GenAI parsing failure: {secondary_error}")
            return self._fallback_deterministic_reasoning(
                context,
                enriched,
                reason=f"LLM_EXECUTION_FALLBACK ({primary_error})",
            )

    def _extract_clean_json(self, raw_text: str) -> str:
        """
        Wrapper method delegating to `extract_clean_json_from_markdown` helper for backward compatibility.

        Args:
            raw_text (str): Raw string output from LLM response.

        Returns:
            str: Stripped JSON string.

        WHY: Preserves public API compatibility for existing unit tests while consolidating utility logic.
        """
        return extract_clean_json_from_markdown(raw_text)

    def _derive_fallback_risk_level(
        self,
        crush_index: float,
        incident_type: IncidentType,
        density: float,
        match_phase: Any,
        profile: str,
        overflow_target: str,
        zone_id: str,
    ) -> Tuple[str, int, str, str]:
        """
        Derives qualitative risk level, probability score, root cause, and signage from spatial index metrics.

        Args:
            crush_index (float): Computed quantitative crush risk index.
            incident_type (IncidentType): Reported anomaly.
            density (float): Crowd capacity percentage.
            match_phase (Any): Temporal phase.
            profile (str): Architectural profile string.
            overflow_target (str): Target relief concourse.
            zone_id (str): Primary sector identifier.

        Returns:
            Tuple[str, int, str, str]: Risk classification, probability percentage, root cause analysis, and LED signage.

        WHY: Single-responsibility helper isolates qualitative assessment from directive generation.
        """
        if crush_index >= CRUSH_INDEX_THRESHOLDS[2] or incident_type in [
            IncidentType.OVERCROWDING_BOTTLENECK,
            IncidentType.TURNSTILE_JAM,
        ]:
            risk_level: str = RISK_LEVEL_CRITICAL
            prob: int = min(int(crush_index * 0.95), 98)
            root_cause: str = (
                f"Severe crowd bottleneck detected (Crush Index: {crush_index}). {density}% density "
                f"compounded by {incident_type.value} during {match_phase.value}. "
                f"Architectural zone profile ({profile}) requires immediate pulse-metering."
            )
            signage: str = f"⚠️ GATE CONGESTED. USE EXPRESS ENTRY AT {overflow_target.upper()} FOR INSTANT ACCESS."
            return risk_level, prob, root_cause, signage

        if crush_index >= CRUSH_INDEX_THRESHOLDS[1]:
            risk_level = RISK_LEVEL_HIGH
            prob = min(int(crush_index * 0.8), 85)
            root_cause = (
                f"Elevated concourse density ({density}%) approaching threshold limits. "
                f"Crush Index ({crush_index}) indicates surge risk in {zone_id} without queue soothing."
            )
            signage = "PLEASE HAVE MOBILE TICKETS READY. KEEP CORRIDORS CLEAR FOR FLOW."
            return risk_level, prob, root_cause, signage

        risk_level = RISK_LEVEL_MODERATE if crush_index >= CRUSH_INDEX_THRESHOLDS[0] else RISK_LEVEL_LOW
        prob = int(crush_index * 0.5)
        root_cause = (
            f"Stable crowd flow ({density}% density) during {match_phase.value}. "
            f"Crush Index ({crush_index}) remains within safe operational boundaries."
        )
        signage = "WELCOME TO FIFA WORLD CUP 2026. FOLLOW SIGNAGE TO YOUR SECTOR."
        return risk_level, prob, root_cause, signage

    def _synthesize_fallback_directives(
        self,
        incident_type: IncidentType,
        zone_id: str,
        overflow_target: str,
        action_mode: str,
        signage: str,
        risk_level: str,
        adjacent_zones: List[str],
    ) -> List[StewardDirective]:
        """
        Synthesizes prioritized steward and operations directives based on incident and risk criteria.

        Args:
            incident_type (IncidentType): Active anomaly type.
            zone_id (str): Sector ID.
            overflow_target (str): Primary relief target.
            action_mode (str): Recommended operational mode.
            signage (str): LED payload string.
            risk_level (str): Assessed qualitative risk level.
            adjacent_zones (List[str]): All available relief sectors.

        Returns:
            List[StewardDirective]: List of prioritized tactical actions.

        WHY: Modularizing directive building prevents deeply nested if/else statements.
        """
        directives: List[StewardDirective] = []

        if incident_type == IncidentType.MEDICAL_EMERGENCY:
            directives.append(
                StewardDirective(
                    priority=1,
                    assigned_target="Rapid Response Medical Triage & Security Unit",
                    action_instruction=f"Enforce 3-meter emergency corridor through {zone_id}. Escort medical cart directly from closest service elevator.",
                )
            )
            directives.append(
                StewardDirective(
                    priority=2,
                    assigned_target=f"{zone_id} Gate Stewards",
                    action_instruction="Temporarily hold incoming turnstile scan velocity by 50% to prevent crowd crush around medical scene.",
                )
            )
        elif incident_type == IncidentType.TURNSTILE_JAM:
            directives.append(
                StewardDirective(
                    priority=1,
                    assigned_target="Mobile Ticketing Technical Team",
                    action_instruction=f"Deploy 4 handheld mobile scanning units to {zone_id} to clear stalled turnstile queue.",
                )
            )
            directives.append(
                StewardDirective(
                    priority=2,
                    assigned_target="Concourse Digital Signage Controller",
                    action_instruction=f"Redirect 40% of approaching general admission queue to {overflow_target} using LED displays.",
                )
            )
        else:
            directives.append(
                StewardDirective(
                    priority=1,
                    assigned_target=f"{zone_id} Floor Stewards",
                    action_instruction=f"Enforce active queue buffering ({action_mode}). Maintain 5-meter safety spacing around turnstiles and stairwells.",
                )
            )
            directives.append(
                StewardDirective(
                    priority=2,
                    assigned_target="Concourse Digital Signage Controller",
                    action_instruction=f"Push high-contrast signage update across {zone_id}: '{signage}'.",
                )
            )

        if risk_level in [RISK_LEVEL_CRITICAL, RISK_LEVEL_HIGH] and len(directives) < 4:
            sec_target: str = adjacent_zones[-1] if len(adjacent_zones) > 1 else overflow_target
            directives.append(
                StewardDirective(
                    priority=3,
                    assigned_target="Adjacent Concourse Coordinators",
                    action_instruction=f"Prepare {overflow_target} and {sec_target} to receive redirected fan influx.",
                )
            )

        return directives

    def _synthesize_fallback_pa_scripts(self, zone_id: str, overflow_target: str) -> PublicAddressScript:
        """
        Generates localized multilingual PA scripts for concourse acoustic broadcasts.

        Args:
            zone_id (str): Concourse identifier.
            overflow_target (str): Target relief gate.

        Returns:
            PublicAddressScript: Pydantic model containing English, Spanish, and French scripts.

        WHY: Single-responsibility helper keeps speech generation cleanly separated from risk logic.
        """
        return PublicAddressScript(
            english=(
                f"Attention fans in {zone_id}: To ensure your safety and express entry into the stadium, "
                f"please keep corridors clear, continue moving forward, and follow steward directions toward {overflow_target}."
            ),
            spanish=(
                f"Atención aficionados en {zone_id}: Para garantizar su seguridad y un acceso rápido al estadio, "
                f"por favor mantengan los pasillos despejados, continúen avanzando y sigan las instrucciones del personal hacia {overflow_target}."
            ),
            french=(
                f"Attention aux supporters dans {zone_id}: Pour assurer votre sécurité et une entrée rapide dans le stade, "
                f"veuillez garder les couloirs dégagés, continuer à avancer et suivre les indications des stadiers vers {overflow_target}."
            ),
        )

    def _fallback_deterministic_reasoning(
        self,
        context: CrowdContextRequest,
        enriched: Dict[str, Any],
        reason: str = "",
    ) -> CrowdActionPlanResponse:
        """
        High-availability deterministic decision matrix.

        Args:
            context (CrowdContextRequest): Input context vector.
            enriched (Dict[str, Any]): Pre-computed spatial calculations.
            reason (str): Diagnostic trace explaining why fallback reasoning triggered.

        Returns:
            CrowdActionPlanResponse: Synthesized action plan.

        WHY: Guaranteed zero-downtime resilience orchestrating modular helpers without cyclomatic bloat.
        """
        now_utc: str = datetime.now(timezone.utc).isoformat()
        crush_index: float = float(enriched.get("crush_risk_index", DEFAULT_CRUSH_INDEX))
        action_mode: str = str(enriched.get("recommended_action_mode", ACTION_MODE_STANDARD))
        adjacent_zones: List[str] = list(enriched.get("adjacent_overflow_zones", ["Gate B", "Sector C"]))
        overflow_target: str = adjacent_zones[0] if adjacent_zones else DEFAULT_OVERFLOW_TARGET
        profile: str = str(enriched.get("zone_architectural_profile", ""))

        risk_level, prob, root_cause, signage = self._derive_fallback_risk_level(
            crush_index,
            context.incident_type,
            context.crowd_density_percentage,
            context.match_phase,
            profile,
            overflow_target,
            context.zone_id,
        )

        directives: List[StewardDirective] = self._synthesize_fallback_directives(
            context.incident_type,
            context.zone_id,
            overflow_target,
            action_mode,
            signage,
            risk_level,
            adjacent_zones,
        )

        pa_scripts: PublicAddressScript = self._synthesize_fallback_pa_scripts(context.zone_id, overflow_target)

        role_summary: str = (
            f"[{context.user_role.value} BRIEFING] {context.zone_id} operating at {context.crowd_density_percentage}% density "
            f"(Crush Index: {crush_index} | Mode: {action_mode}). Risk assessed as {risk_level} with {prob}% bottleneck probability. "
            f"Immediate priority: Enforce queue buffering and redirect overflow to {overflow_target}. "
            f"(Executed via High-Resilience Spatial Engine: {reason})"
        )

        return CrowdActionPlanResponse(
            stadium_id=context.stadium_id,
            zone_id=context.zone_id,
            timestamp_utc=now_utc,
            risk_assessment=RiskAssessment(
                risk_level=risk_level,
                bottleneck_probability=prob,
                root_cause_analysis=root_cause,
            ),
            steward_directives=directives,
            digital_signage_payload=signage,
            pa_broadcast_scripts=pa_scripts,
            summary_for_role=role_summary,
        )


_intelligence_service: Optional[CrowdIntelligenceService] = None


def get_intelligence_service() -> CrowdIntelligenceService:
    """
    Retrieves the singleton instance of CrowdIntelligenceService.

    Returns:
        CrowdIntelligenceService: Cached service singleton.

    WHY: Preserves cached GenAI client across async route invocations.
    """
    global _intelligence_service
    if _intelligence_service is None:
        _intelligence_service = CrowdIntelligenceService()
    return _intelligence_service
