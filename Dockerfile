# CallQualityHub Dockerfile
# Multi-stage build için production-ready image

# Base image
FROM python:3.11-slim as base

# Metadata
LABEL maintainer="faikerkangursen@icloud.com"
LABEL description="CallQualityHub - Premium Call Quality Management System"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gettext \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-deps -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p /app/media/call_records \
    && mkdir -p /app/logs \
    && mkdir -p /app/staticfiles

# Set permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Collect static files
RUN python manage.py collectstatic --noinput --settings=call_quality_hub.settings

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Expose port
EXPOSE 8000

# Production stage
FROM base as production

# Copy application code
COPY --from=base --chown=appuser:appuser /app /app

# Switch to app user
USER appuser

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "call_quality_hub.wsgi:application"]

# Development stage
FROM base as development

# Install development dependencies
USER root
RUN pip install pytest pytest-django black flake8 coverage

# Switch back to app user
USER appuser

# Default command for development
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 