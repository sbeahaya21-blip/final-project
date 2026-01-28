"""Configuration management for the application."""
import os
from typing import Optional


class Config:
    """Application configuration."""
    
    # ERPNext Configuration
    ERPNEXT_BASE_URL: str = os.getenv(
        'ERPNEXT_BASE_URL',
        'https://your-instance.erpnext.com'
    )
    ERPNEXT_API_KEY: str = os.getenv('ERPNEXT_API_KEY', '')
    ERPNEXT_API_SECRET: str = os.getenv('ERPNEXT_API_SECRET', '')
    
    # Application Settings
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def validate_erpnext_config(cls) -> bool:
        """Validate that ERPNext configuration is set."""
        return bool(
            cls.ERPNEXT_BASE_URL and
            cls.ERPNEXT_API_KEY and
            cls.ERPNEXT_API_SECRET and
            cls.ERPNEXT_BASE_URL != 'https://your-instance.erpnext.com'
        )
