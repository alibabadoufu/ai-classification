"""
Configuration management for CAIS platform.
Handles environment variables and application settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Configuration class for CAIS platform."""
    
    # LLM API Configuration
    LLM_API_URL: str = os.getenv("LLM_API_URL", "http://localhost:8000/v1")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "your-api-key-here")
    
    # S3 Configuration
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "cais-documents")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Application Configuration
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "7860"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Prompt Configuration
    DEFAULT_JURISDICTION_PROMPT: str = "prompts/jurisdiction/v1_base.txt"
    DEFAULT_COUNTERPARTY_PROMPT: str = "prompts/counterparty/v1_base.txt"
    ACTIVE_PROMPT_VERSION: str = os.getenv("ACTIVE_PROMPT_VERSION", "v1_base")
    
    # Data Storage Paths
    S3_DOCUMENTS_PREFIX: str = "documents/"
    S3_TRAINING_DATA_PREFIX: str = "training_data/"
    S3_FEEDBACK_PREFIX: str = "feedback/"
    S3_ANALYSIS_RESULTS_PREFIX: str = "analysis_results/"
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present."""
        required_vars = [
            "LLM_API_URL",
            "LLM_API_KEY",
            "S3_BUCKET_NAME"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var) or getattr(cls, var) == "your-api-key-here":
                missing_vars.append(var)
        
        if missing_vars:
            print(f"Warning: Missing required configuration: {', '.join(missing_vars)}")
            return False
        
        return True

# Global config instance
config = Config()