"""
Aura-26 GenAI Crowd Intelligence Service Layer.

WHY: Abstracting GenAI interaction into a dedicated async service class decouples prompt engineering
and API call retry logic from the REST controllers. It also provides multi-layer fallback resilience,
combining Google GenAI structured outputs with spatial context enrichment and deterministic algorithms
for high-availability World Cup stadium operations.
"""

import json
import re
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from app.core.config import get_settings
from app.core.prompts import SYSTEM_INSTRUCTION_AURA26, build_crowd_intelligence_prompt
from app.services.context_engine import SpatialContextEngine
from app.models.schemas import (
    CrowdContextRequest,
    CrowdActionPlanResponse,
    RiskAssessment,
    StewardDirective,
    PublicAddressScript,
    IncidentType,
)

# WHY: Attempt to import Google GenAI SDK cleanly without breaking local dev if unconfigured.
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

    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[genai.Client] = None
        
        # WHY: Initialize Gemini client only when SDK is present and API key is configured.
        if GENAI_SDK_AVAILABLE and self.settings.gemini_api_key:
            try:
                self.client = genai.Client(api_key=self.settings.gemini_api_key)
            except Exception as e:
                # WHY: Log error during initialization without hard crashing server boot.
                print(f"[WARN] Failed to initialize Google GenAI Client: {e}")

    async def generate_crowd_action_plan(
        self, context: CrowdContextRequest
    ) -> CrowdActionPlanResponse:
        """
        Main entry point for generating a structured crowd action plan from user & stadium context.
        WHY: Enriches raw telemetry with spatial index metrics before calling external LLMs or fallback logic.
        """
        # Step 1: Pre-process and enrich context vector via Spatial Engine
        enriched_telemetry = SpatialContextEngine.enrich_context(context)

        # Step 2: Check GenAI client availability
        if not self.client or not self.settings.gemini_api_key:
            return self._fallback_deterministic_reasoning(
                context, 
                enriched_telemetry, 
                reason="API_KEY_MISSING_OR_CLIENT_UNAVAILABLE"
            )

        # Step 3: Build modular prompt using enriched context
        prompt_payload = build_crowd_intelligence_prompt(context, enriched_telemetry)

        try:
            # Primary Strategy: Structured JSON Schema enforcement via Google GenAI SDK
            response = self.client.models.generate_content(
                model=self.settings.ai_model_name,
                contents=[
                    types.Part.from_text(text=SYSTEM_INSTRUCTION_AURA26),
                    types.Part.from_text(text=prompt_payload)
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=CrowdActionPlanResponse,
                    temperature=0.2,  # WHY: Low temperature ensures high operational logic and determinism
                )
            )
            
            # Parse and validate the strict schema response
            response_json = json.loads(response.text)
            return CrowdActionPlanResponse.model_validate(response_json)

        except Exception as primary_error:
            # WHY: If structured generation fails (e.g. due to model tier differences), attempt clean text fallback.
            print(f"[WARN] Primary structured GenAI generation failed ({primary_error}). Attempting secondary JSON parsing...")
            try:
                raw_response = self.client.models.generate_content(
                    model=self.settings.ai_model_name,
                    contents=prompt_payload,
                    config=types.GenerateContentConfig(temperature=0.2)
                )
                cleaned_json_text = self._extract_clean_json(raw_response.text)
                return CrowdActionPlanResponse.model_validate_json(cleaned_json_text)
            except Exception as secondary_error:
                print(f"[ERROR] Secondary GenAI parsing failure: {secondary_error}")
                return self._fallback_deterministic_reasoning(
                    context, 
                    enriched_telemetry, 
                    reason=f"LLM_EXECUTION_FALLBACK ({str(primary_error)})"
                )

    def _extract_clean_json(self, raw_text: str) -> str:
        """
        Extracts JSON block from markdown code fences if present.
        WHY: Protects against LLMs wrapping valid JSON inside ```json ... ``` blocks.
        """
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
        if match:
            return match.group(1)
        return raw_text.strip()

    def _fallback_deterministic_reasoning(
        self, 
        context: CrowdContextRequest, 
        enriched: Dict[str, Any], 
        reason: str = ""
    ) -> CrowdActionPlanResponse:
        """
        High-availability deterministic decision matrix.
        WHY: Guaranteed zero-downtime resilience. Synthesizes exact spatial calculations (`crush_risk_index`),
        adjacent overflow zones, and incident protocols when GenAI APIs are offline during matchday.
        """
        now_utc = datetime.now(timezone.utc).isoformat()
        crush_index = enriched.get("crush_risk_index", 75.0)
        action_mode = enriched.get("recommended_action_mode", "STANDARD_OPERATIONAL_FLOW")
        adjacent_zones = enriched.get("adjacent_overflow_zones", ["Gate B", "Sector C"])
        overflow_target = adjacent_zones[0] if adjacent_zones else "Adjacent Concourse"

        # Determine risk classification and probability score from enriched spatial index
        if crush_index >= 95.0 or context.incident_type in [IncidentType.OVERCROWDING_BOTTLENECK, IncidentType.TURNSTILE_JAM]:
            risk_level = "CRITICAL"
            prob = min(int(crush_index * 0.95), 98)
            root_cause = (
                f"Severe crowd bottleneck detected (Crush Index: {crush_index}). {context.crowd_density_percentage}% density "
                f"compounded by {context.incident_type.value} during {context.match_phase.value}. "
                f"Architectural zone profile ({enriched.get('zone_architectural_profile')}) requires immediate pulse-metering."
            )
            signage = f"⚠️ GATE CONGESTED. USE EXPRESS ENTRY AT {overflow_target.upper()} FOR INSTANT ACCESS."
        elif crush_index >= 75.0:
            risk_level = "HIGH"
            prob = min(int(crush_index * 0.8), 85)
            root_cause = (
                f"Elevated concourse density ({context.crowd_density_percentage}%) approaching threshold limits. "
                f"Crush Index ({crush_index}) indicates surge risk in {context.zone_id} without queue soothing."
            )
            signage = f"PLEASE HAVE MOBILE TICKETS READY. KEEP CORRIDORS CLEAR FOR FLOW."
        else:
            risk_level = "MODERATE" if crush_index >= 50.0 else "LOW"
            prob = int(crush_index * 0.5)
            root_cause = (
                f"Stable crowd flow ({context.crowd_density_percentage}% density) during {context.match_phase.value}. "
                f"Crush Index ({crush_index}) remains within safe operational boundaries."
            )
            signage = f"WELCOME TO FIFA WORLD CUP 2026. FOLLOW SIGNAGE TO YOUR SECTOR."

        # Synthesize role-specific prioritized directives
        directives = []
        
        if context.incident_type == IncidentType.MEDICAL_EMERGENCY:
            directives.append(StewardDirective(
                priority=1,
                assigned_target="Rapid Response Medical Triage & Security Unit",
                action_instruction=f"Enforce 3-meter emergency corridor through {context.zone_id}. Escort medical cart directly from closest service elevator."
            ))
            directives.append(StewardDirective(
                priority=2,
                assigned_target=f"{context.zone_id} Gate Stewards",
                action_instruction=f"Temporarily hold incoming turnstile scan velocity by 50% to prevent crowd crush around medical scene."
            ))
        elif context.incident_type == IncidentType.TURNSTILE_JAM:
            directives.append(StewardDirective(
                priority=1,
                assigned_target="Mobile Ticketing Technical Team",
                action_instruction=f"Deploy 4 handheld mobile scanning units to {context.zone_id} to clear stalled turnstile queue."
            ))
            directives.append(StewardDirective(
                priority=2,
                assigned_target="Concourse Digital Signage Controller",
                action_instruction=f"Redirect 40% of approaching general admission queue to {overflow_target} using LED displays."
            ))
        else:
            directives.append(StewardDirective(
                priority=1,
                assigned_target=f"{context.zone_id} Floor Stewards",
                action_instruction=f"Enforce active queue buffering ({action_mode}). Maintain 5-meter safety spacing around turnstiles and stairwells."
            ))
            directives.append(StewardDirective(
                priority=2,
                assigned_target="Concourse Digital Signage Controller",
                action_instruction=f"Push high-contrast signage update across {context.zone_id}: '{signage}'."
            ))

        # Add overflow management directive for higher risk
        if risk_level in ["CRITICAL", "HIGH"] and len(directives) < 4:
            directives.append(StewardDirective(
                priority=3,
                assigned_target="Adjacent Concourse Coordinators",
                action_instruction=f"Prepare {overflow_target} and {adjacent_zones[-1] if len(adjacent_zones)>1 else overflow_target} to receive redirected fan influx."
            ))

        # Synthesize multilingual PA scripts
        pa_scripts = PublicAddressScript(
            english=(
                f"Attention fans in {context.zone_id}: To ensure your safety and express entry into the stadium, "
                f"please keep corridors clear, continue moving forward, and follow steward directions toward {overflow_target}."
            ),
            spanish=(
                f"Atención aficionados en {context.zone_id}: Para garantizar su seguridad y un acceso rápido al estadio, "
                f"por favor mantengan los pasillos despejados, continúen avanzando y sigan las instrucciones del personal hacia {overflow_target}."
            ),
            french=(
                f"Attention aux supporters dans {context.zone_id}: Pour assurer votre sécurité et une entrée rapide dans le stade, "
                f"veuillez garder les couloirs dégagés, continuer à avancer et suivre les indications des stadiers vers {overflow_target}."
            )
        )

        role_summary = (
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
                root_cause_analysis=root_cause
            ),
            steward_directives=directives,
            digital_signage_payload=signage,
            pa_broadcast_scripts=pa_scripts,
            summary_for_role=role_summary
        )


# Singleton factory for dependency injection
_intelligence_service: Optional[CrowdIntelligenceService] = None

def get_intelligence_service() -> CrowdIntelligenceService:
    """
    Retrieves the singleton instance of CrowdIntelligenceService.
    WHY: Preserves cached GenAI client across async route invocations.
    """
    global _intelligence_service
    if _intelligence_service is None:
        _intelligence_service = CrowdIntelligenceService()
    return _intelligence_service
