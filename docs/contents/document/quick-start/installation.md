---
id: installation
title: Installation
sidebar_position: 2
---

# Installation

This guide provides step-by-step instructions for installing the ClickUp MCP Server on your system.

## Prerequisites

Before installation, make sure you've met all the [requirements](./requirements.md).

## Install Using pip

ClickUp MCP Server can be installed directly using pip, which is included with Python:

```bash
pip install clickup-mcp-server
```

## Install Using poetry

For better dependency management and project isolation, we recommend installing ClickUp MCP Server using poetry:

```bash
poetry add clickup-mcp-server
```

## Install Using uv

For faster installation with advanced dependency resolution, another recommended approach is using uv:

```bash
uv add clickup-mcp-server
```

## Install from Source

For the latest development version or to contribute to the project:

1. Clone the repository:
   ```bash
   git clone https://github.com/Chisanan232/clickup-mcp-server.git
   cd clickup-mcp-server
   ```

2. Install in development mode:

   Using pip (Python's native package installer):
   ```bash
   pip install -e .
   ```

   Using Poetry:
   ```bash
   poetry install
   ```

   Using uv:
   ```bash
   uv pip install .
   ```

## Docker Installation

You can also run ClickUp MCP Server using Docker:

1. Pull the Docker image:
   ```bash
   docker pull chisanan232/clickup-mcp-server:latest
   ```

2. Or build the image yourself:
   ```bash
   git clone https://github.com/Chisanan232/clickup-mcp-server.git
   cd clickup-mcp-server
   docker build -t clickup-mcp-server .
   ```

## Verify Installation

To verify that the installation was successful, run:

Install by using pip (Python's native package installer):
```bash
clickup-mcp-server --version
```

Install by using Poetry:
```bash
poetry run clickup-mcp-server --version
```

Install by using uv:
```bash
uv run clickup-mcp-server --version
```

You should see the current version of the ClickUp MCP Server displayed.
