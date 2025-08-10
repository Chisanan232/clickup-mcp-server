"""
Common logic for end-to-end tests that need to set up and run a server to verify
features truly.

This subpackage contains modules that are used by the end-to-end tests that need
to set up and run a server to verify features truly. These tests are typically
run in a CI environment and are used to catch regressions before they reach the
production environment.

The modules in this subpackage are responsible for:

* Setting up the server and preparing the environment for the tests
* Running the tests using the specific transport type (e.g. HTTP streaming,
  SSE, etc.)
* Cleaning up the environment after the tests have completed

"""

# Re-export client classes for easier imports
from .client import EndpointClient, SSEClient, StreamingHTTPClient
from .suite import (
    BaseMCPServerFunctionTest,
    BaseE2ETestWithRunningServer,
    OPERATION_TIMEOUT,
    SERVER_START_TIMEOUT,
    ROUTES_REGISTRATION_TIME,
)
