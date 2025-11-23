---
slug: golden-user-journey-first-minor-release
title: Shipping the first minor release — Golden user journey for ClickUp MCP Server
authors: [chisanan232]
tags: [clickup, mcp, python]
---

We’ve reached an exciting milestone: the first minor release of ClickUp MCP Server. This release delivers the “golden user journey” for both end users and developers, supported by a carefully planned architecture and cohesive tooling.

<!-- truncate -->

## Why this release matters

- Establishes a complete, reliable baseline for integrating ClickUp with MCP clients.
- Provides well-defined extension points for developers to build custom logic safely and predictably.
- Documents clear operational paths (CLI, transports, webhooks, and examples) to accelerate adoption.

## Golden user journeys

- **For end users (MCP tools)**
  - Discover and call tools for ClickUp resources (team/workspace info; space, folder, list, task operations).
  - Connect via SSE (default) or HTTP streaming transports.
  - Quick health checks for operational readiness.

- **For developers**
  - Extend webhook processing with either Pythonic functions or OOP-style handlers.
  - Plug in message queue backends (default `local`) via an abstracted backend design.
  - Follow layered models and typed DTOs to keep integrations maintainable.

## Architecture highlights

- **API client**
  - Typed async HTTP client for ClickUp.
  - Clear error types and retry-aware behavior for robustness.

- **Model layering**
  - I/O models (request/response shapes),
  - Domain models (core behaviors and invariants),
  - DTO models (transport-friendly mapping between layers).

- **MCP tools**
  - Tools exposed for teams/workspaces (info) and CRUD flows for spaces/folders/lists/tasks.
  - Designed for discoverability and safe inputs/outputs.

- **Webhook features**
  - Inbound endpoint compatible with ClickUp webhook payloads.
  - Two handler styles:
    - Pythonic: lightweight function handlers for rapid iteration.
    - OOP: class-based handlers for structure, reuse, and testing.

- **Message queue backend**
  - Abstract backend interface with a `local` backend for development out of the box.
  - Decouples producers (web server) and consumers for scalable processing.

## Operational experience

- **CLI and transports**
  - `clickup-mcp-server` with `.env` discovery (or `--env`) and `--token` override.
  - SSE (default) mounted at `/sse`, HTTP streaming at `/mcp`.
  - Health endpoint at `/health`.

- **Webhook consumer**
  - `clickup-webhook-consumer` to dispatch events to registered handlers.
  - Configurable via `QUEUE_BACKEND` and `CLICKUP_WEBHOOK_HANDLER_MODULES`.

## Get started

- Quick start and how-to-run: see the docs
  - CLI usages and scenarios: /docs/next/quick-start/cli-usage
  - How to run: /docs/next/quick-start/how-to-run
  - Introduction: /docs/next/introduction

## What’s next

- More backends for messaging and production-ready deployments.
- Additional MCP tools and higher-level workflows.
- Deeper guides for testing, observability, and scaling.

Thanks to everyone who contributed ideas, testing, and feedback during planning and architecture design. This release sets a strong foundation for the community to build on.
