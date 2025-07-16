"""
Django app configuration for financial data processing.
"""
from django.apps import AppConfig


class FinancialConfig(AppConfig):
    """Configuration for the financial app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.financial'
    verbose_name = 'Financial Data Processing'
