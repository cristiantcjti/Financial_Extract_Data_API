from django.apps import AppConfig


class FinancialConfig(AppConfig):
    default_auto_field: str = "django.db.models.BigAutoField"
    name = "src.financial"
    verbose_name = "Financial Data Processing"
