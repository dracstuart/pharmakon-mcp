# 0009. Profiles are files; user interfaces edit them

- **Status:** Proposed
- **Date:** 2026-10-31

## Context
The people who most care about unit and source settings are often not programmers.
They need a simple way to define and change profiles, without editing configuration
files by hand.

## Decision
- A profile is always a file. It is the single source of truth and can be shared,
  backed up and versioned.
- User interfaces are editors over that file, delivered in tiers:
  1. **Chat setup:** MCP tools for viewing and changing a profile, using MCP
     elicitation for structured choices, with a plain-language summary confirmed
     before saving.
  2. **Local visual editor:** a page served on the user's own machine for reordering
     sources, choosing units, adding a source with column mapping, and previewing the
     result on an example molecule.
- Validation and preview logic live in `pharmakon-core`, so every interface behaves
  the same way.

## Consequences
- Non-programmers can manage their own settings.
- Every editor must round-trip the file without losing anything.
- Interactive UI inside chat clients (MCP Apps) can be added later as another editor.
