# Use Python 3.13 as base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY . .

# Create a virtual environment and install dependencies using uv
RUN uv venv
RUN . .venv/bin/activate && uv sync --locked --all-extras

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"
ENV SERVER_PORT=8000

# Expose port from environment variable
EXPOSE ${SERVER_PORT}

# Set the entry point
CMD ["bash", "./scripts/docker/run-server.sh"]
