"""
Configuration management for the Salah Reminders application.

This module provides centralized configuration management with environment-based
settings and proper validation.
"""

from .settings import Config, DevelopmentConfig, ProductionConfig, TestingConfig

__all__ = ['Config', 'DevelopmentConfig', 'ProductionConfig', 'TestingConfig']
