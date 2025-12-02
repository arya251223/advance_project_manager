import os
from typing import Dict
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Ollama configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Model configurations with extended timeouts
    MODEL_TIMEOUT: int = 1200  # 20 minutes default
    MODEL_MAX_TIMEOUT: int = 1800  # 30 minutes max
    
    # Model mappings
    MODELS: Dict[str, str] = {
        "mistral": "ollama/mistral:7b-instruct",
        "starcoder": "ollama/starcoder2:7b",
        "codellama": "ollama/codellama:7b"
    }
    
    # Agent model assignments
    AGENT_MODELS: Dict[str, str] = {
        "senior_manager": "mistral",
        "project_manager": "mistral",
        "senior_developer": "starcoder",
        "junior_developer": "codellama",
        "integrator": "mistral",
        "integrator_tester": "starcoder",
        "final_tester": "starcoder",
        "delivery": "mistral"
    }
    
    # Project settings
    GENERATED_DIR: str = "generated"
    MAX_RETRIES: int = 3

    # 🔹 Server config (with alias to match .env uppercase keys)
    api_host: str = Field("0.0.0.0", alias="API_HOST")
    api_port: int = Field(8000, alias="API_PORT")
    debug: bool = Field(True, alias="DEBUG")

    # ✅ Add this line to support your .env
    crewai_tracing_enabled: bool = Field(False, alias="CREWAI_TRACING_ENABLED")

    class Config:
        env_file = ".env"
        populate_by_name = True  # allows using both alias + field name

settings = Settings()
