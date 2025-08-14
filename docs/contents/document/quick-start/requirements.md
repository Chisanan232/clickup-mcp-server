---
id: requirements
title: Requirements
sidebar_position: 1
---

# Requirements

Before installing and running ClickUp MCP Server, ensure your environment meets the following requirements:

## System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 256MB RAM
- **Disk Space**: Minimum 100MB for installation

## Software Prerequisites

- **Python**: Python 3.13 or higher
- **Package Manager**:
  - pip (included with Python, is a native tool in Python)
  - [poetry] (Python package manager, recommended)
  - [uv] (Python package manager in Rust, recommended)
- **ClickUp Account**: A ClickUp account with API access
- **API Token**: A valid ClickUp API token with appropriate permissions

[poetry]: https://python-poetry.org/
[uv]: https://docs.astral.sh/uv/

## Optional Requirements

- **Docker**: For containerized deployment (Docker 20.10.0 or later)

## API Access

To use the ClickUp MCP Server, you'll need to [obtain an API token from ClickUp]. This token should be stored securely and provided to the server during initialization.

[obtain an API token from ClickUp]: https://clickup.com/api
