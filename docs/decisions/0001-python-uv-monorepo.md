# 0001. Python and a uv workspace monorepo

- **Status:** Accepted
- **Date:** 2026-10-31

## Context
The project needs several MCP servers that share one library. The scientific Python
ecosystem (RDKit, pint, pandas) is the strongest for chemistry, and the official MCP
Python SDK is mature. Likely contributors are scientists, who mostly know Python.

## Decision
- Python 3.10 or later, using the official MCP Python SDK 2.x.
- One repository and one uv workspace: shared code in `packages/`, one installable
  package per data source in `servers/`.
- All packages share one version number (lockstep).

## Consequences
- One lockfile, one CI pipeline, and easy changes that cross packages.
- Each server can still be installed on its own (`uvx pharmakon-pubchem`).
- MCP features that land first in the TypeScript SDK may reach Python later.
- A future component in another language would need its own tooling.
