import os
from typing import List

# Load environment variables from .env file
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use system env vars


class Settings:
    """Application settings and configuration"""
    
    # Application settings
    APP_NAME: str = os.getenv("APP_NAME", "AI Agent Monitoring Dashboard Backend")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./test.db"
    )
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        origin.strip() 
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    ]

    # Telemetry settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_JSON: bool = os.getenv("LOG_JSON", "True").lower() == "true"
    ENABLE_TRACING: bool = os.getenv("ENABLE_TRACING", "True").lower() == "true"
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "True").lower() == "true"
    ENABLE_LOGGING: bool = os.getenv("ENABLE_LOGGING", "True").lower() == "true"
    TELEMETRY_EXPORTER: str = os.getenv("TELEMETRY_EXPORTER", "otlp")
    OTEL_SERVICE_NAME: str = os.getenv("OTEL_SERVICE_NAME", APP_NAME)
    OTEL_EXPORTER_OTLP_ENDPOINT: str = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    OTEL_EXPORTER_OTLP_PROTOCOL: str = os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf")
    METRICS_PATH: str = os.getenv("METRICS_PATH", "/metrics")


settings = Settings()
