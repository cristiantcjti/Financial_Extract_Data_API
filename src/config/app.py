import logging

from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

from src.financial.controllers.extract_financial_data import financial_router

logger = logging.getLogger(__name__)


class FinancialNinjaAPI(NinjaExtraAPI):
    pass


api_v1 = FinancialNinjaAPI(
    version="1.0.0",
    title="Financial Data API",
    description="API for extracting financial data from OFDA service with resilience and caching",
    auth=None,
    docs_url="/docs",
    openapi_url="/openapi.json",
)

api_v1.register_controllers(NinjaJWTDefaultController)

api_v1.add_router("", financial_router, tags=["financial"])
