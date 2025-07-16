# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Django-based Financial Data API** that integrates with the OFDA Financial Data API to extract, process, and serve financial data with resilience, caching, and security features.

## Common Development Commands

### Setup and Installation
```bash
# Install dependencies using UV
uv sync

# Copy environment configuration
cp .env.example .env

# Start services with Docker
docker-compose up -d

# Run database migrations
python manage.py migrate
# or with Docker:
docker-compose exec financial-api python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Development Server
```bash
# Start development server
python manage.py runserver

# Or with Docker
docker-compose up financial-api
```

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest src/financial/tests/test_extraction.py

# Run Django tests
python manage.py test
```

### Code Quality
```bash
# Format code
uv run black src/

# Lint code
uv run ruff src/

# Type checking (if mypy is added)
uv run mypy src/
```

### Database Operations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Database shell
python manage.py dbshell

# Django shell
python manage.py shell
```

### Background Tasks
```bash
# Start Celery worker
celery -A src.config.celery worker --loglevel=info

# Start Celery beat
celery -A src.config.celery beat --loglevel=info

# Or with Docker
docker-compose up celery-worker celery-beat
```

## Architecture

### High-Level Structure
```
src/
├── config/           # Django configuration and API setup
├── core/            # Shared utilities (retry, caching, encryption)
├── financial/       # Main business logic for financial data
├── ofda/           # OFDA API integration and models
```

### Key Components

1. **Django Ninja API** (`src/config/app.py`):
   - Custom `FinancialNinjaAPI` class with error handling
   - JWT authentication
   - Automatic API documentation

2. **OFDA Client** (`src/ofda/client.py`):
   - Handles all communication with OFDA API
   - Implements retry logic and circuit breaker
   - Manages dynamic clients and consents

3. **Financial Data Service** (`src/financial/services/extraction.py`):
   - Main business logic for data extraction
   - Orchestrates the entire extraction process
   - Handles caching and error recovery

4. **Field Mapping Service** (`src/financial/services/field_mapping.py`):
   - Removes system identifiers from API responses
   - Maps internal fields to clean external format
   - Provides data transformation and validation

5. **Retry Service** (`src/core/utils/retry.py`):
   - Exponential backoff with jitter
   - Circuit breaker pattern
   - Configurable retry attempts and delays

6. **Cache Service** (`src/core/utils/cache.py`):
   - Redis-based caching with encryption
   - Different TTL for different data types
   - Automatic cache invalidation

7. **Encryption Service** (`src/core/utils/encryption.py`):
   - PII data encryption at rest
   - Secure key management
   - Field-level encryption support

### Data Flow

1. **Request** → Controller validates input
2. **Service** → Checks cache for existing data
3. **OFDA Client** → Creates/reuses dynamic client
4. **OFDA Client** → Creates/reuses consent for user
5. **OFDA Client** → Extracts accounts, balances, transactions
6. **Field Mapping** → Cleans and maps response data
7. **Cache** → Stores processed data
8. **Response** → Returns structured JSON

### Database Models

- **DynamicClient**: Stores OFDA dynamic client tokens
- **UserConsent**: Manages user consent tokens
- **CachedFinancialData**: Cached financial data
- **FinancialDataExtraction**: Extraction audit logs
- **APICallLog**: OFDA API call logs

## Environment Configuration

### Required Environment Variables
```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_NAME=financial_api
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/1

# OFDA API
OFDA_API_BASE_URL=http://localhost:8000
OFDA_API_TIMEOUT=30
OFDA_API_RETRY_ATTEMPTS=5

# Security
ENCRYPTION_KEY=your-encryption-key
```

## API Endpoints

### Main Endpoints
- `POST /api/v1/extract-financial-data` - Extract financial data
- `GET /api/v1/health` - Health check
- `GET /api/v1/extraction-history/{user_document}` - Get history
- `GET /api/v1/stats` - Get statistics

### Authentication
- `POST /api/v1/auth/token/obtain/` - Get JWT token
- `POST /api/v1/auth/token/refresh/` - Refresh JWT token

## Testing Strategy

### Test Structure
- Unit tests for services and utilities
- Integration tests for API endpoints
- Mock external API calls
- Test different error scenarios

### Running OFDA API for Testing
```bash
# Stable testing
docker run -d -p 8000:8000 -e INSTABILITY_PROBABILITY=0.0 --name ofda-api-stable gniparcs/ofda-engineer-test

# Unstable testing
docker run -d -p 8000:8000 -e INSTABILITY_PROBABILITY=0.3 --name ofda-api-unstable gniparcs/ofda-engineer-test
```

## Key Design Patterns

1. **Service Layer Pattern**: Business logic separated from controllers
2. **Repository Pattern**: Data access abstraction
3. **DTO Pattern**: Data transfer objects for type safety
4. **Circuit Breaker**: Fault tolerance for external services
5. **Retry with Exponential Backoff**: Resilience against temporary failures
6. **Caching Strategy**: Multiple cache layers with different TTLs
7. **Field Mapping**: Clean external API responses

## Security Considerations

- All PII data encrypted at rest
- JWT authentication for API access
- Input validation on all endpoints
- Rate limiting and circuit breakers
- Secure token management
- No sensitive data in logs

## Monitoring and Observability

- Comprehensive logging with structured format
- Health check endpoints for all services
- Extraction statistics and metrics
- Error tracking and alerting
- Performance monitoring

## Common Issues and Solutions

1. **OFDA API 504 errors**: Handled by retry mechanism
2. **Token expiration**: Automatic token refresh
3. **Cache misses**: Graceful degradation to fresh data
4. **Database connectivity**: Health checks and reconnection
5. **Memory issues**: Efficient data processing and cleanup

## Development Notes

- Use UV for dependency management
- Follow Django conventions for app structure
- All models use UUID primary keys
- Comprehensive error handling at all levels
- Async processing with Celery for heavy operations
- Docker for consistent development environment