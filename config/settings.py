"""Application configuration management."""

import os
from pathlib import Path
from typing import Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application configuration."""

    # Gmail API
    gmail_credentials_path: str = Field(default="config/credentials.json")
    gmail_token_path: str = Field(default="config/token.json")
    gmail_account: str = Field(default="kobylev@gmail.com")

    # Gemini API
    gemini_api_key: str = Field(default="")

    # Application
    log_level: str = Field(default="INFO")
    max_clone_workers: int = Field(default=5, ge=1, le=10)
    clone_timeout: int = Field(default=60, ge=10, le=300)
    gemini_request_delay: int = Field(default=60, ge=0, le=300)

    # File Paths
    data_dir: str = Field(default="./data")
    output_dir: str = Field(default="./data/output")
    temp_dir: str = Field(default="./tmp")
    log_dir: str = Field(default="./logs")
    students_mapping_file: str = Field(default="./data/students_mapping.xlsx")

    # Processing Limits
    max_batch_size: int = Field(default=100, ge=1, le=1000)
    default_batch_size: int = Field(default=10, ge=1, le=100)

    # Excel File Names
    file_1_2_name: str = Field(default="file_1_2.xlsx")
    file_2_3_name: str = Field(default="file_2_3.xlsx")
    file_3_4_name: str = Field(default="file_3_4.xlsx")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"

    def get_output_path(self, filename: str) -> Path:
        """Get full path for output file."""
        return Path(self.output_dir) / filename

    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()
