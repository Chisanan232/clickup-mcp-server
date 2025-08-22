<h1 align="center">
  ClickUp MCP Server
</h1>

<p align="center">
  <a href="https://pypi.org/project/clickup-mcp-server">
    <img src="https://img.shields.io/pypi/v/clickup-mcp-server?color=%23099cec&amp;label=PyPI&amp;logo=pypi&amp;logoColor=white" alt="PyPI package version">
  </a>
  <a href="https://github.com/Chisanan232/clickup-mcp-server/releases">
    <img src="https://img.shields.io/github/release/Chisanan232/clickup-mcp-server.svg?label=Release&logo=github" alt="GitHub release version">
  </a>
  <a href="https://github.com/Chisanan232/clickup-mcp-server/actions/workflows/ci.yaml">
    <img src="https://github.com/Chisanan232/clickup-mcp-server/actions/workflows/ci.yaml/badge.svg" alt="CI/CD status">
  </a>
  <a href="https://codecov.io/gh/Chisanan232/clickup-mcp-server" >
    <img src="https://codecov.io/gh/Chisanan232/clickup-mcp-server/graph/badge.svg?token=VVZ0cGPVvp"/>
  </a>
  <a href="https://results.pre-commit.ci/latest/github/Chisanan232/clickup-mcp-server/master">
    <img src="https://results.pre-commit.ci/badge/github/Chisanan232/clickup-mcp-server/master.svg" alt="Pre-Commit building state">
  </a>
  <a href="https://sonarcloud.io/summary/new_code?id=Chisanan232_clickup-mcp-server">
    <img src="https://sonarcloud.io/api/project_badges/measure?project=Chisanan232_clickup-mcp-server&metric=alert_status" alt="Code quality level">
  </a>
  <a href="https://chisanan232.github.io/clickup-mcp-server/">
    <img src="https://github.com/Chisanan232/clickup-mcp-server/actions/workflows/documentation.yaml/badge.svg" alt="documentation CI status">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="Software license">
  </a>

</p>

<img align="center" src="https://raw.githubusercontent.com/Chisanan232/clickup-mcp-server/refs/heads/master/docs/static/img/clickup_mcp_server_logo.png" alt="clickup-mcp-server logo" />

<p align="center">
  <em>clickup-mcp-server</em> is a Python tool to set up MCP server easily and humanly.
</p>

## Overview

🦾 A strong Model, Capability, Protocol (MCP) server for ClickUp API integration. This server provides a standardized
interface for interacting with ClickUp's API through the MCP protocol, making it easier to build AI-enabled applications
that leverage ClickUp's project management capabilities.


## Features

[//]: # (- Full support for ClickUp API resources &#40;Teams, Spaces, Folders, Lists, Tasks&#41;)
- Multiple transport protocols (HTTP streaming and SSE)
- Environment variable configuration via `.env` files
- Consolidated data models for seamless API interaction


## Python versions support

[![Supported Versions](https://img.shields.io/pypi/pyversions/clickup-mcp-server.svg?logo=python&logoColor=FBE072)](https://pypi.org/project/clickup-mcp-server)

Requires Python 3.13 or higher.


## Quick Start

### Installation

```bash
pip install clickup-mcp-server
```

### Running the server

The simplest way to start the server:

```bash
clickup-mcp-server --token YOUR_CLICKUP_API_TOKEN
```

### Using environment files

You can store your API token in a `.env` file:

```
# .env file
CLICKUP_API_TOKEN=your_api_token_here
```

And start the server with:

```bash
clickup-mcp-server --env /path/to/.env
```

### Client connection

Connect to the server using any MCP client implementation. Example:

* Using SSE transport

```python
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def get_authorized_teams():
    url = "http://localhost:3005/sse"

    async with sse_client(url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Available tools:", [tools])

            res = await session.call_tool(
                name="get_authorized_teams",
            )
            print("get_authorized_teams →", res.model_dump())

if __name__ == "__main__":
    asyncio.run(get_authorized_teams())
```

* Using streaming HTTP transport

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def get_authorized_teams():
    url = "http://localhost:3005/mcp/mcp"

    async with streamablehttp_client(url) as (
        read_stream,
        write_stream,
        _close_fn,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools_resp = await session.list_tools()
            print("Available tools:", [t.name for t in tools_resp.tools])

            res = await session.call_tool(
                name="get_authorized_teams",
            )
            print("get_authorized_teams →", res.model_dump())

if __name__ == "__main__":
    asyncio.run(get_authorized_teams())
```


## API Resources

The server provides access to the following ClickUp resources:

- Teams
- Spaces

[//]: # (- Folders)

[//]: # (- Lists)

[//]: # (- Tasks)

[//]: # (- Users)

[//]: # (- Custom fields)

## Configuration Options

The server supports various configuration options:

| Option    | Environment Variable | Description                                     |
|-----------|----------------------|-------------------------------------------------|
| `--token` | `CLICKUP_API_TOKEN`  | Your ClickUp API token                          |
| `--env`   | -                    | Path to `.env` file containing configuration    |
| `--port`  | -                    | Port to run the server on (default: 8000)       |
| `--host`  | -                    | Host to bind the server to (default: 127.0.0.1) |


## Documentation

[![documentation](https://github.com/Chisanan232/clickup-mcp-server/actions/workflows/documentation.yaml/badge.svg)](https://chisanan232.github.io/clickup-mcp-server/)

The [documentation](https://chisanan232.github.io/clickup-mcp-server/) contains more details,
demonstrations and anything you need about **_clickup-mcp-server_**.

* [Getting start](https://chisanan232.github.io/clickup-mcp-server/docs/next/quick-start) helps you start to prepare the
environment, install dependencies and configure the detail settings with explanation in detail.
    * What [requirement](https://chisanan232.github.io/clickup-mcp-server/docs/next/quick-start/requirements) I need to prepare?
    * How can I [install](https://chisanan232.github.io/clickup-mcp-server/docs/next/quick-start/installation) it?
    * How to [configure the details for this MCP server](https://chisanan232.github.io/clickup-mcp-server/docs/next/quick-start/how-to-run#configuration)?
    * I have a configuration right now. How can I [run this MCP server](https://chisanan232.github.io/clickup-mcp-server/docs/next/quick-start/how-to-run#running-the-server)?
* Want to learn more how to use it?
    * What exact [features or APIs it has](https://chisanan232.github.io/clickup-mcp-server/docs/next/api-references)?
        * About the [web APIs](https://chisanan232.github.io/clickup-mcp-server/docs/next/api-references/web-apis)
        * About the [MCP APIs](https://chisanan232.github.io/clickup-mcp-server/docs/next/api-references/mcp-apis)
* Want to [contribute](https://chisanan232.github.io/clickup-mcp-server/docs/next/contribute) to this project?
    * I face something [issue](https://chisanan232.github.io/clickup-mcp-server/docs/next/contribute/report-bug) it cannot work finely!
    * I want to [wish a feature or something change](https://chisanan232.github.io/clickup-mcp-server/docs/next/contribute/request-changes).
    * If you're interested in **_clickup-mcp-server_** and have any ideas want to design it, even implement it, it's very welcome to [contribute](https://chisanan232.github.io/clickup-mcp-server/docs/next/contribute) **_clickup-mcp-server_**!
* About the [release notes](https://chisanan232.github.io/clickup-mcp-server/docs/next/changelog/).


## Coding style and following rules

**_<your lib name>_** follows coding styles **_black_** and **_PyLint_** to control code quality.

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)


## Downloading state

**_clickup-mcp-server_** still a young open source which keeps growing. Here's its download state:

[![Downloads](https://pepy.tech/badge/clickup-mcp-server)](https://pepy.tech/project/clickup-mcp-server)
[![Downloads](https://pepy.tech/badge/clickup-mcp-server/month)](https://pepy.tech/project/clickup-mcp-server)


## License

[MIT License](./LICENSE)
