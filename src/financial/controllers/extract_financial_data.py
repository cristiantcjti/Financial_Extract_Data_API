from datetime import datetime

from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from src.config.logging import logger
from src.financial.services.extraction_service import ExtractionService
from src.financial.services.client_service import DynamicClientService
from src.financial.schemas.schemas import (
    ExtractionRequestSchema,
    FinancialDataResponseSchema,
    HealthCheckSchema,
)

financial_router = Router()

@financial_router.post("/extract-financial-data", response=FinancialDataResponseSchema)
def extract_financial_data(request: HttpRequest, data: ExtractionRequestSchema):
    try:
        logger.info(f"Starting financial data extraction for user_document: {data.user_document}")

        dynamic_client_data = DynamicClientService().get_or_create_client(data.user_document)
        logger.info(f"Client obtained: {dynamic_client_data.name}")

        extraction_service = ExtractionService()

        result = extraction_service.extract_financial_data(
            user_document=data.user_document,
            dynamic_client_id=dynamic_client_data.id,
            dynamic_token=dynamic_client_data.token
        )

        logger.info(f"Financial data extraction completed successfully for user_document: {data.user_document}")
        return result

    except HttpError:
        raise

    except ValueError as e:
        logger.error(f"Validation error for user_document: {data.user_document}, Error: {str(e)}")
        raise HttpError(400, f"Validation error: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error during extraction for user_document: {data.user_document}, Error: {str(e)}")
        raise HttpError(500, "An unexpected error occurred during financial data extraction")


@financial_router.get("/health", response=HealthCheckSchema)
def health_check(request: HttpRequest):
    try:
        services_status = {
            "api": "healthy",
            "database": "healthy",
            "ofda_api": "unknown"
        }
        try:
            extraction_service = ExtractionService()
            services_status["ofda_api"] = "healthy"
        except Exception as e:
            logger.warning(f"OFDA API health check failed: {str(e)}")
            services_status["ofda_api"] = "unhealthy"

        overall_status = "healthy" if all(status == "healthy" for status in services_status.values()) else "degraded"

        return HealthCheckSchema(
            status=overall_status,
            timestamp=datetime.now(),
            services=services_status
        )

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthCheckSchema(
            status="unhealthy",
            timestamp=datetime.now(),
            services={"api": "unhealthy", "error": str(e)}
        )