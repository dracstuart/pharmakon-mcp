# 0010. Library-first architecture with several front doors

- **Status:** Proposed
- **Date:** 2026-10-31

## Context
Users should be able to reach pharmakon from wherever they work: chat assistants,
electronic lab notebooks, LIMS, project boards, low-code tools, notebooks and scripts.
Building a separate connector for every platform does not scale.

## Decision
- All logic lives in a plain Python library with no MCP dependency.
- Thin front doors expose it:
  - **MCP server** for chat assistants and agents;
  - **CLI** for scripts and batch jobs;
  - **REST API** with an OpenAPI description, for any platform that can call a URL;
  - the **Python library** itself, for notebooks and pipelines.
- Phase 1 ships the MCP server (stdio, run locally) and the CLI. Entry points are
  structured so that HTTP transport and the REST API can be added without a rewrite.
- The Pydantic models are the shared response format for every front door and are
  treated as a public contract (changes follow semantic versioning).

## Consequences
- One implementation serves every channel, and results look the same everywhere.
- Platform-specific integrations become small wrappers over the REST API.
- Discipline is needed to keep logic out of `server.py` and other front doors.
