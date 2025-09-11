"""
Application configuration settings.

This module provides environment-based configuration management with proper
validation and type hints for the Salah Tracker application.
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    url: str
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class JWTConfig:
    """JWT configuration settings."""
    secret_key: str
    access_token_expires: int = 3600  # 1 hour
    refresh_token_expires: int = 2592000  # 30 days
    algorithm: str = "HS256"


@dataclass
class MailConfig:
    """Email configuration settings."""
    server: str
    port: int
    username: str
    password: str
    use_tls: bool = True
    use_ssl: bool = False


@dataclass
class ExternalAPIConfig:
    """External API configuration settings."""
    prayer_times_api_key: str
    geocoding_api_key: str
    prayer_times_base_url: str = "http://api.aladhan.com/v1"
    geocoding_base_url: str = "https://api.bigdatacloud.net/data"


class Config:
    """Base configuration class."""

    # Flask configuration
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG: bool = False
    TESTING: bool = False

    # Database configuration
    DATABASE_CONFIG: DatabaseConfig = DatabaseConfig(
        url=os.getenv('DATABASE_URL', 'mysql://root:password@localhost/salah_tracker'),
        echo=os.getenv('DATABASE_ECHO', 'False').lower() == 'true'
    )

    # JWT configuration
    JWT_CONFIG: JWTConfig = JWTConfig(
        secret_key=os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    )

    # Mail configuration
    MAIL_CONFIG: Optional[MailConfig] = None

    # External API configuration
    EXTERNAL_API_CONFIG: ExternalAPIConfig = ExternalAPIConfig(
        prayer_times_api_key=os.getenv('PRAYER_TIMES_API_KEY', ''),
        geocoding_api_key=os.getenv('GEOCODING_API_KEY', ''),
        prayer_times_base_url=os.getenv('PRAYER_TIMES_BASE_URL', 'http://api.aladhan.com/v1'),
        geocoding_base_url=os.getenv('GEOCODING_BASE_URL', 'https://api.bigdatacloud.net/data')
    )

    # Application settings
    PRAYER_TIME_WINDOW_MINUTES: int = 30
    AUTO_UPDATE_INTERVAL_MINUTES: int = 5
    DEFAULT_TIMEZONE: str = 'Asia/Kolkata'
    DEFAULT_LOCATION: dict = {
        'lat': 12.9716,
        'lng': 77.5946,
        'city': 'Bangalore',
        'country': 'India'
    }

    def __post_init__(self):
        """Initialize mail configuration if credentials are provided."""
        if all([
            os.getenv('MAIL_SERVER'),
            os.getenv('MAIL_PORT'),
            os.getenv('MAIL_USERNAME'),
            os.getenv('MAIL_PASSWORD')
        ]):
            self.MAIL_CONFIG = MailConfig(
                server=os.getenv('MAIL_SERVER'),
                port=int(os.getenv('MAIL_PORT', 587)),
                username=os.getenv('MAIL_USERNAME'),
                password=os.getenv('MAIL_PASSWORD'),
                use_tls=os.getenv('MAIL_USE_TLS', 'True').lower() == 'true',
                use_ssl=os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
            )


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG: bool = True
    DATABASE_CONFIG: DatabaseConfig = DatabaseConfig(
        url=os.getenv('DATABASE_URL', 'mysql://root:password@localhost/salah_tracker'),
        echo=True
    )


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG: bool = False
    DATABASE_CONFIG: DatabaseConfig = DatabaseConfig(
        url=os.getenv('DATABASE_URL'),
        echo=False
    )


class TestingConfig(Config):
    """Testing configuration."""
    TESTING: bool = True
    DATABASE_CONFIG: DatabaseConfig = DatabaseConfig(
        url=os.getenv('TEST_DATABASE_URL', 'sqlite:///:memory:'),
        echo=False
    )


def get_config() -> Config:
    """
    Get configuration based on environment.

    Returns:
        Config: The appropriate configuration instance based on FLASK_ENV.
    """
    env = os.getenv('FLASK_ENV', 'development').lower()

    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }

    config_class = config_map.get(env, DevelopmentConfig)
    return config_class()
