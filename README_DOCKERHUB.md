# 🦾 ClickUp MCP Server

[![Docker Pulls](https://img.shields.io/docker/pulls/chisanan232/clickup-mcp-server)](https://hub.docker.com/r/chisanan232/clickup-mcp-server)
[![Docker Image Size](https://img.shields.io/docker/image-size/chisanan232/clickup-mcp-server/latest)](https://hub.docker.com/r/chisanan232/clickup-mcp-server)
[![Docker Stars](https://img.shields.io/docker/stars/chisanan232/clickup-mcp-server)](https://hub.docker.com/r/chisanan232/clickup-mcp-server)
[![Docker Automated build](https://img.shields.io/docker/automated/chisanan232/clickup-mcp-server)](https://hub.docker.com/r/chisanan232/clickup-mcp-server)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)

## 🔍 Overview

A powerful FastAPI web server that exposes ClickUp functionality through a REST API using the Model-Controller-Provider (MCP) pattern.

## 🐳 Docker Usage

### 🚀 Quick Start

Pull the Docker image:

```bash
docker pull chisanan232/clickup-mcp-server:latest
```

Run the container with minimal configuration:

```bash
docker run -d -p 8000:8000 -e CLICKUP_API_TOKEN=your_token_here chisanan232/clickup-mcp-server
```

Access the API documentation at `http://localhost:8000/docs`

### 🔧 Configuration Options

The Docker container can be configured using environment variables:

| Environment Variable | Description                                                     | Default   |
|----------------------|-----------------------------------------------------------------|-----------|
| `CLICKUP_API_TOKEN`  | Your ClickUp API token (required)                               | -         |
| `SERVER_HOST`        | Host to bind the server to                                      | `0.0.0.0` |
| `SERVER_PORT`        | Port to bind the server to                                      | `8000`    |
| `MCP_TRANSPORT`      | Transport mode (`sse`, `streamable-http`)                       | `sse`     |
| `LOG_LEVEL`          | Logging level (`debug`, `info`, `warning`, `error`, `critical`) | `info`    |
| `RELOAD`             | Enable auto-reload for development                              | -         |

### 📝 Using Environment Files

You can use a `.env` file for configuration instead of passing environment variables directly:

1. Create a `.env` file with your configuration:

```
CLICKUP_API_TOKEN=your_clickup_api_token_here
LOG_LEVEL=debug
```

2. Mount the file when running the container:

```bash
docker run -d -p 8000:8000 -v $(pwd)/.env:/app/.env chisanan232/clickup-mcp-server
```

### 🔄 Custom Port Configuration

To use a custom port:

```bash
docker run -d -p 9000:9000 -e SERVER_PORT=9000 -e CLICKUP_API_TOKEN=your_token_here chisanan232/clickup-mcp-server
```

### 🛡️ Securing Your API Token

For production environments, consider using Docker secrets or a secure environment management solution rather than passing the API token directly.

### 🔍 Health Check

The container includes a health check endpoint at `/health` that can be used to verify the server is running correctly.

## 📚 Python Usage

### Installation

```bash
pip install -e .
```

### Configuration

There are two ways to configure your ClickUp API token:

1. **Environment variable**: Set the `CLICKUP_API_TOKEN` environment variable
2. **Environment file**: Create a `.env` file with your ClickUp API token:

```
CLICKUP_API_TOKEN=your_clickup_api_token_here
```

See the `.env.example` file for an example configuration.

### Starting the server

```bash
python -m clickup_mcp
```

### Command Line Options

The server accepts the following command line options:

- `--host`: Host to bind the server to (default: 0.0.0.0)
- `--port`: Port to bind the server to (default: 8000)
- `--log-level`: Logging level (choices: debug, info, warning, error, critical; default: info)
- `--reload`: Enable auto-reload for development
- `--env`: Path to a custom .env file for environment variables (default: .env)
- `--token`: ClickUp API token (overrides token from .env file if provided)
- `--transport`: Transport protocol to use (sse or http-streaming)

Example:
```bash
python -m clickup_mcp --host 127.0.0.1 --port 8080 --log-level debug --env custom.env
```

## 📋 Requirements

- Python 3.13+
- Docker (for container deployment)

## 📖 Documentation

API documentation is available at `http://localhost:8000/docs` when the server is running.

## 🌟 Features

- 🔒 Secure API token handling via environment variables or files
- 🔄 Multiple transport protocols (SSE, HTTP streaming)
- 📊 Comprehensive ClickUp API coverage
- 🚀 Fast and efficient FastAPI implementation
- 📝 Interactive API documentation with Swagger UI

## 🔨 Development

Want to contribute? Great! Check out our [GitHub repository](https://github.com/Chisanan232/clickup-mcp-server) for contribution guidelines.

## 📜 License

[MIT License](./LICENSE)
