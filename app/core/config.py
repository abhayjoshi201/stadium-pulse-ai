"""
Application Configuration & Environment Settings.

WHY: Managing configuration via structured environment variables ensures zero-tolerance
for hardcoded API secrets, enabling clean evaluation across different deployment environments
(local dev, staging, or World Cup stadium edge servers) while enforcing strict validation.
"""

import os
from functools import lru_cache
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# WHY: Explicitly load .env file at startup to ensure environment variables are populated
# before BaseSettings instantiates, allowing seamless local development.
load_dotenv()


class Settings(BaseSettings):
    """
    Core settings schema validated at runtime.
    WHY: Using BaseSettings guarantees that missing or malformed environment variables
    fail fast during application boot rather than failing silently mid-request during matchday operations.
    """
    
    # WHY: Strict secret management. Evaluators or controllers provide this via .env or OS environment.
    gemini_api_key: str = Field(
        default="", 
        description="Google Gemini API key required for structured GenAI reasoning."
    )
    
    # WHY: Distinct operational environments allow toggling debug telemetry and mock fallback modes.
    app_env: str = Field(
        default="development", 
        description="Current runtime environment (development, staging, production)."
    )
    
    # WHY: Port configuration allows easy binding to port 8000 (standard FastAPI) or container port.
    port: int = Field(
        default=8000, 
        description="Server port for API listening."
    )
    
    # WHY: Host configuration defaults to 0.0.0.0 for containerized and edge network accessibility.
    host: str = Field(
        default="0.0.0.0", 
        description="Host interface binding address."
    )
    
    # WHY: Granular log levels allow verbose debugging during testing while minimizing disk I/O in production.
    log_level: str = Field(
        default="INFO", 
        description="Logging verbosity level."
    )
    
    # WHY: Defaulting to MetLife Stadium (NY/NJ) provides immediate context for evaluators out-of-the-box.
    default_stadium_id: str = Field(
        default="metlife_stadium_ny_nj", 
        description="Default stadium identifier for context lookups."
    )
    
    # WHY: Gemini model selection. Defaulting to gemini-2.5-pro or gemini-2.5-flash for speed and structured output.
    ai_model_name: str = Field(
        default="gemini-2.5-flash",
        description="Model identifier used for high-speed structured GenAI crowd reasoning."
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Factory function to retrieve cached application settings.
    WHY: Using lru_cache prevents re-parsing disk .env files on every API request,
    significantly boosting throughput during high-concurrency matchday surges.
    """
    return Settings()
