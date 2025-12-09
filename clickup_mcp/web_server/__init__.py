"""
FastAPI-based web server for the ClickUp MCP service.

Provides:
- Application factory and server singleton
- MCP transport mounting (SSE / HTTP streaming)
- Webhook ingress and event handling (sinks, handlers, MQ)
"""
