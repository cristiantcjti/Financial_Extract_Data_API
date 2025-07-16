# Financial Data API

A Django-based API for extracting financial data from the OFDA Financial Data API. This API provides resilient, cached, and secure access to financial accounts, balances, and transactions.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
  - [Core Components](#core-components)
  - [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Quick Setup (Recommended)](#quick-setup-recommended)
  - [Testing the API](#testing-the-api)
- [API Endpoints](#api-endpoints)
  - [Core Endpoints](#core-endpoints)
  - [Authentication](#authentication)
- [Request/Response Examples](#requestresponse-examples)
- [Development Setup](#development-setup)
  - [Local Development with Virtual Environment](#local-development-with-virtual-environment)
  - [UV Commands Reference](#uv-commands-reference)
  - [Traditional Local Development Setup](#traditional-local-development-setup)
  - [Running Tests](#running-tests)
  - [Code Quality](#code-quality)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [API Resilience](#api-resilience)
- [Monitoring and Logging](#monitoring-and-logging)
  - [Health Checks](#health-checks)
  - [Logging](#logging)
- [Security](#security)
  - [Data Protection](#data-protection)
  - [Authentication](#authentication-1)
- [Troubleshooting](#troubleshooting)
  - [Docker Setup Issues](#docker-setup-issues)
  - [Application Issues](#application-issues)
  - [Virtual Environment Issues](#virtual-environment-issues)
  - [Port Conflicts](#port-conflicts)
  - [Common Error Messages](#common-error-messages)
  - [Docker Commands Reference](#docker-commands-reference)
  - [Debugging](#debugging)
- [License](#license)

## Features

- **Resilient API Integration**: Handles OFDA API instability with retry mechanisms and circuit breakers
- **Intelligent Caching**: Redis-based caching for tokens and financial data
- **Security**: Encryption for sensitive PII data
- **Token Management**: Automatic dynamic client and consent management
- **Field Mapping**: Removes internal system identifiers from responses
- **Comprehensive Logging**: Detailed logging for monitoring and debugging
- **Health Checks**: Built-in health monitoring for all services
- **Docker Support**: Fully containerized setup

## Architecture

### Core Components

- **Django Ninja API**: RESTful API with automatic documentation
- **OFDA Client**: Handles communication with external OFDA API
- **Caching Layer**: Redis-based caching with encryption
- **Retry Service**: Exponential backoff for handling API instability
- **Field Mapping**: Transforms internal API responses to clean external format
- **Background Tasks**: Celery for asynchronous processing

### Technology Stack

- **Python 3.12+**
- **Django 5.1+ with Django Ninja**
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage
- **Celery**: Background task processing
- **Docker**: Containerization

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed on your system:

#### Required Software

1. **Docker and Docker Desktop**
   - **Windows/Mac**: Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - **Linux**: Install Docker Engine and Docker Compose:
     ```bash
     # Ubuntu/Debian
     curl -fsSL https://get.docker.com -o get-docker.sh
     sudo sh get-docker.sh
     sudo apt-get install docker-compose-plugin
     
     # Or use your distribution's package manager
     ```
   - Verify installation: `docker --version` and `docker-compose --version`

2. **UV (Fast Python Package Manager)**
   - **Windows**: 
     ```powershell
     powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
     ```
   - **macOS/Linux**:
     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```
   - Verify installation: `uv --version`

3. **Git** (for cloning the repository)
   - Download from [git-scm.com](https://git-scm.com/) or use your system's package manager

### Quick Setup (Recommended)

Follow these steps to get the application running quickly using Docker:

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd financial-api
   ```

2. **Set up environment configuration**
   ```bash
   cp .env.example .env
   # Optional: Edit .env file with your specific configuration
   # The default values work for local development
   ```

3. **Start the OFDA API service** (External dependency)
   ```bash
   # Pull and run the OFDA API that our service depends on
   docker pull gniparcs/ofda-engineer-test
   docker run -d -p 8000:8000 --name ofda-api gniparcs/ofda-engineer-test
   
   # Verify OFDA API is running
   curl http://localhost:8000/health
   ```

4. **Start all application services**
   ```bash
   # Start all services in detached mode (runs in background)
   docker-compose up -d
   
   # Check that all containers are running healthy
   docker-compose ps
   ```

5. **Verify the application is running**
   ```bash
   # Check API health endpoint
   curl http://localhost:8001/api/v1/health
   
   # View API documentation in browser
   # Visit: http://localhost:8001/api/v1/docs
   ```

### Testing the API

1. **Health Check**
   ```bash
   curl http://localhost:8001/api/v1/health
   ```

2. **Extract Financial Data**
   ```bash
   curl -X POST http://localhost:8001/api/v1/extract-financial-data \
     -H "Content-Type: application/json" \
     -d '{"user_document": "12345678901"}'
   ```

3. **API Documentation**
   Visit: http://localhost:8001/api/v1/docs

## API Endpoints

### Core Endpoints

- `POST /api/v1/extract-financial-data` - Extract financial data for a user
- `GET /api/v1/health` - Health check endpoint
- `GET /api/v1/extraction-history/{user_document}` - Get extraction history
- `GET /api/v1/stats` - Get extraction statistics

### Authentication

The API uses JWT authentication. Obtain tokens using:
- `POST /api/v1/auth/token/obtain/` - Get access token
- `POST /api/v1/auth/token/refresh/` - Refresh access token

## Request/Response Examples

### Extract Financial Data

**Request:**
```json
{
  "user_document": "12345678901"
}
```

**Response:**
```json
{
  "user_document": "12345678901",
  "extraction_date": "2024-01-15T10:30:00Z",
  "accounts": [
    {
      "account_id": "ACC001",
      "account_type": "CHECKING",
      "account_status": "ACTIVE",
      "balance": {
        "amount": 1500.75,
        "currency": "BRL"
      },
      "transactions": [
        {
          "transaction_id": "TXN001",
          "transaction_type": "TRANSFER",
          "transaction_status": "COMPLETED",
          "amount": 100.00,
          "currency": "BRL",
          "direction": "IN",
          "description": "Salary deposit",
          "date": "2024-01-10T09:00:00Z"
        }
      ]
    }
  ],
  "summary": {
    "total_accounts": 1,
    "total_transactions": 1,
    "processing_time_ms": 1250,
    "errors": []
  }
}
```

## Development Setup

### Local Development with Virtual Environment

For development work, you may want to run the application locally with a Python virtual environment instead of Docker. This approach gives you more control and faster iteration cycles.

#### Setting Up Python Virtual Environment with UV

1. **Create and activate virtual environment**
   ```bash
   # Create a new virtual environment using UV
   uv venv
   
   # Activate the virtual environment
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

2. **Install project dependencies**
   ```bash
   # Install all dependencies from pyproject.toml
   uv sync
   
   # Or install with development dependencies
   uv sync --dev
   ```

3. **Set up environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env file for local development
   # Make sure to update database and Redis URLs for local services
   ```

4. **Start required services (API and Redis)**
   ```bash
   # Start only the database and cache services
   docker-compose up redis -d
   
   # Verify services are running
   docker-compose ps
   ```
5. **Start the development server**
   ```bash
   # Run the Django development server
   python manage.py runserver
   
   # The API will be available at http://localhost:8000
   ```

#### UV Commands Reference

```bash
# Create virtual environment
uv venv [path]

# Install dependencies
uv sync                    # Install all dependencies
uv sync --dev             # Include development dependencies
uv sync --frozen          # Install from lockfile without updates

# Add new dependencies
uv add package-name       # Add to main dependencies
uv add package-name --dev # Add to development dependencies

# Remove dependencies
uv remove package-name

# Update dependencies
uv sync --upgrade         # Update all dependencies
uv sync --upgrade-package package-name  # Update specific package

# Run commands in virtual environment
uv run python manage.py runserver
uv run pytest
uv run black src/
```

### Traditional Local Development Setup

If you prefer not to use UV, you can also set up the project with traditional Python tools:

1. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Follow steps 3-6 from the UV setup above**

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest src/financial/tests/test_extraction.py
```

### Code Quality

```bash
# install pre-commit in the local termial
pre-commit install
* Whe run git commit it will automatically apply code quality convention.

## Configuration

### Environment Variables

Key environment variables:

- `SECRET_KEY`: Django secret key
- `DEBUG`: Enable debug mode
- `REDIS_URL`: Redis connection URL
- `OFDA_API_BASE_URL`: OFDA API base URL

### API Resilience

- `OFDA_API_RETRY_ATTEMPTS`: Maximum retry attempts (5)
- `OFDA_API_RETRY_DELAY`: Base delay between retries (1 second)
- `OFDA_API_TIMEOUT`: Request timeout (30 seconds)

## Monitoring and Logging

### Health Checks

The API includes comprehensive health checks:

- **Application Health**: `/api/v1/health`

### Logging

Logs are structured and include:

- **Request/Response Logging**: All API calls to OFDA
- **Error Tracking**: Detailed error information
- **Performance Metrics**: Processing times and statistics
- **Security Events**: Authentication and authorization events

### Monitoring

- **Extraction Statistics**: Track success/failure rates
- **Performance Metrics**: Response times and throughput
- **Error Rates**: Monitor API reliability
- **Cache Hit Rates**: Cache effectiveness

## Security

### Data Protection

- **Encryption**: All sensitive PII data encrypted at rest
- **Token Security**: Secure token storage and management
- **Input Validation**: Comprehensive request validation
- **Rate Limiting**: Protection against abuse

### Authentication

- JWT-based authentication
- Token expiration and refresh
- Role-based access control

## Troubleshooting

### Docker Setup Issues

1. **Docker Compose Fails to Start**
   ```bash
   # Check Docker is running
   docker --version
   docker-compose --version
   
   # Check if ports are already in use
   netstat -an | grep :8001  # Check if port 8001 is taken
   netstat -an | grep :6379  # Check if Redis port is taken
   
   # Stop conflicting services
   docker-compose down
   docker stop $(docker ps -q)  # Stop all running containers
   
   # Restart with clean state
   docker-compose up -d --force-recreate
   ```

2. **Container Health Check Failures**
   ```bash
   # Check container logs
   docker-compose logs financial-api
   docker-compose logs redis
   
   # Check container status
   docker-compose ps
   
   # Restart specific service
   docker-compose restart financial-api
   ```

3. **Permission Issues (Linux/WSL)**
   ```bash
   # Fix Docker socket permissions
   sudo usermod -aG docker $USER
   # Log out and back in for changes to take effect
   
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

### Application Issues

1. **OFDA API Connection Failures**
   ```bash
   # Check OFDA API is running
   curl http://localhost:8000/health
   
   # If not running, start it
   docker run -d -p 8000:8000 --name ofda-api gniparcs/ofda-engineer-test
   
   # Check Docker network connectivity
   docker network ls
   docker inspect bridge
   ```

2. **Redis Cache Issues**
   ```bash
   # Verify Redis is running
   docker-compose ps redis
   
   # Test Redis connectivity
   docker-compose exec redis redis-cli ping
   
   # Clear cache if needed
   docker-compose exec financial-api python manage.py shell -c "from django.core.cache import cache; cache.clear()"
   
   # Check Redis logs
   docker-compose logs redis
   ```

### Virtual Environment Issues

1. **UV Not Found or Installation Issues**
   ```bash
   # Reinstall UV
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Add to PATH (if needed)
   export PATH="$HOME/.cargo/bin:$PATH"
   
   # Restart terminal and verify
   uv --version
   ```

2. **Virtual Environment Activation Issues**
   ```bash
   # Recreate virtual environment
   rm -rf .venv
   uv venv
   
   # Activate (ensure you're in project directory)
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   
   # Verify activation
   which python  # Should point to .venv/bin/python
   ```

3. **Dependency Installation Problems**
   ```bash
   # Clear UV cache
   uv cache clean
   
   # Reinstall dependencies
   uv sync --reinstall
   
   # Install with verbose output for debugging
   uv sync --verbose
   ```

### Port Conflicts

```bash
# Check what's using your ports
lsof -i :8001  # Financial API port
lsof -i :8000  # OFDA API port
lsof -i :6379  # Redis port

# Kill processes using ports (if needed)
sudo kill -9 $(lsof -t -i:8001)
```

### Common Error Messages

1. **"Port already in use"**
   - Stop conflicting services or change ports in docker-compose.yml

2. **"Connection refused"**
   - Ensure all required services are running
   - Check firewall settings
   - Verify container networking

3. **"Permission denied"**
   - Check file permissions
   - Ensure Docker has proper permissions
   - On Windows, ensure Docker Desktop is running

### Docker Commands Reference

```bash
# Basic operations
docker-compose up -d              # Start all services in background
docker-compose down               # Stop and remove all containers
docker-compose ps                 # Show running containers
docker-compose logs               # Show logs from all services
docker-compose logs financial-api # Show logs from specific service

# Container management
docker-compose restart financial-api  # Restart specific service
docker-compose exec financial-api bash # Open shell in container
docker-compose pull                   # Update images to latest versions

# Database operations (if using PostgreSQL)
docker-compose exec financial-api python manage.py migrate
docker-compose exec financial-api python manage.py createsuperuser
docker-compose exec financial-api python manage.py shell

# Cleanup
docker-compose down -v            # Remove containers and volumes
docker system prune               # Clean up unused Docker objects
docker volume prune               # Remove unused volumes
```

### Debugging

1. **Enable Debug Mode**
   ```bash
   # Set in .env
   DEBUG=True
   ```

2. **Check Logs**
   ```bash
   # Application logs
   docker-compose logs financial-api
   
   # OFDA API logs
   docker logs ofda-api
   ```

3. **Test with Different Instability Levels**
   ```bash
   # Stable testing
   docker run -d -p 8000:8000 -e INSTABILITY_PROBABILITY=0.0 --name ofda-api-stable gniparcs/ofda-engineer-test
   
   # High instability testing
   docker run -d -p 8000:8000 -e INSTABILITY_PROBABILITY=0.5 --name ofda-api-unstable gniparcs/ofda-engineer-test
   ```

## License

MIT License - see LICENSE file for details.