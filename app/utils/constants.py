"""
Stadium Pulse AI Centralized Constants (`constants.py`).

WHY: Eradicating hardcoded magic numbers, status strings, zone IDs, and density thresholds
from service algorithms and API routes ensures single-source-of-truth configuration and 100% type-safe refactoring.
"""

from typing import List, Dict, Any

# ==========================================
# SYSTEM & STADIUM IDENTIFIERS
# ==========================================
DEFAULT_STADIUM_ID: str = "metlife_stadium_ny_nj"
STADIUM_DISPLAY_NAME: str = "MetLife Stadium (New York / New Jersey) - 82,500 Capacity"
DEFAULT_ZONE_ID: str = "North_Gate_Concourse_Level_2_B4"
DEFAULT_OVERFLOW_TARGET: str = "Adjacent Concourse"
DEFAULT_ARCHITECTURAL_PROFILE: str = "Standard Stadium Concourse Zone"

# ==========================================
# RISK LEVELS & OPERATIONAL MODES
# ==========================================
RISK_LEVEL_CRITICAL: str = "CRITICAL"
RISK_LEVEL_HIGH: str = "HIGH"
RISK_LEVEL_MODERATE: str = "MODERATE"
RISK_LEVEL_LOW: str = "LOW"

ACTION_MODE_STANDARD: str = "STANDARD_OPERATIONAL_FLOW"
ACTION_MODE_MONITORING: str = "ACTIVE_MONITORING_AND_WAYFINDING"
ACTION_MODE_DYNAMIC_BUFFERING: str = "DYNAMIC_REROUTE_AND_QUEUE_BUFFERING"
ACTION_MODE_EMERGENCY_PULSE: str = "EMERGENCY_CLEARANCE_AND_PULSE_METERING"

ACTION_MODES_LIST: List[str] = [
    ACTION_MODE_STANDARD,
    ACTION_MODE_MONITORING,
    ACTION_MODE_DYNAMIC_BUFFERING,
    ACTION_MODE_EMERGENCY_PULSE,
]

# ==========================================
# SPATIAL ALGORITHM THRESHOLDS (O(log N))
# ==========================================
CRUSH_INDEX_THRESHOLDS: List[float] = [55.0, 75.0, 95.0]
SUPER_SATURATION_DENSITY_THRESHOLD: float = 120.0
SUPER_SATURATION_CRUSH_INDEX: float = 140.0
DEFAULT_CRUSH_INDEX: float = 75.0
DEFAULT_DENSITY_PERCENTAGE: float = 85.0

# ==========================================
# MULTIPLIERS FOR RISK SCORE SYNTHESIS
# ==========================================
MULTIPLIER_BASE: float = 1.0
MULTIPLIER_INGRESS_TURNSTILE: float = 1.3
MULTIPLIER_HALFTIME_RESTROOM: float = 1.5
MULTIPLIER_EGRESS_TRANSIT: float = 1.6

MULTIPLIER_BOTTLENECK_JAM: float = 1.4
MULTIPLIER_MEDICAL_OBSTRUCTION: float = 1.3
MULTIPLIER_WEATHER_ALERT: float = 1.25
SCORE_NORMALIZATION_DIVISOR: float = 1.5
MAX_CRUSH_RISK_INDEX: float = 150.0

# ==========================================
# PRE-MAPPED STADIUM ZONES DATABASE
# ==========================================
STADIUM_ZONE_DATABASE: Dict[str, Dict[str, Any]] = {
    "North_Gate_Concourse_Level_2_B4": {
        "architectural_profile": "Turnstile Ingress Bank & Security Screening Concourse (Level 2)",
        "nominal_capacity": 4500,
        "bottleneck_sensitivity": 1.2,
        "adjacent_overflow_zones": ["Gate C Express Lanes", "North-West Pedestrian Ramp"],
    },
    "VIP_East_Turnstile_Bank_A": {
        "architectural_profile": "Premium Hospitality & Express Entry Turnstile Bank",
        "nominal_capacity": 1200,
        "bottleneck_sensitivity": 0.8,
        "adjacent_overflow_zones": ["East Concourse Gate B", "Suite Access Elevator Bank 2"],
    },
    "South_Concourse_Restrooms_Sector_C2": {
        "architectural_profile": "Enclosed Interior Concourse, Restroom & Concession Hub",
        "nominal_capacity": 3800,
        "bottleneck_sensitivity": 1.5,
        "adjacent_overflow_zones": ["Upper Level 3 Concourse", "Stairwell Landing C-North"],
    },
    "Transit_Hub_Egress_Platform_West": {
        "architectural_profile": "Mass Transit Hub, Rail Platform & Accessible Shuttle Cart Bay",
        "nominal_capacity": 6500,
        "bottleneck_sensitivity": 1.8,
        "adjacent_overflow_zones": ["West Perimeter Holding Plaza", "Pedestrian Bridge 4"],
    },
}
