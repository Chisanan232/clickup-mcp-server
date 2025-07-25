# Build stage
FROM python:3.13-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy only requirements files first to leverage Docker cache
COPY pyproject.toml uv.lock LICENSE README.md ./

# Create virtual environment and install dependencies
RUN uv venv /app/.venv && \
    . /app/.venv/bin/activate && \
    uv sync --locked --all-extras

# Final stage
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    SERVER_PORT=8000

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . .

# Create a non-root user to run the app and set permissions
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port from environment variable
EXPOSE ${SERVER_PORT}

# Set the entry point
CMD ["bash", "./scripts/docker/run-server.sh"]
