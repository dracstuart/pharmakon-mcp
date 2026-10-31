# 0004. Every value records where it came from

- **Status:** Accepted
- **Date:** 2026-10-31

## Context
Scientists need to know where a number came from, and whether it was measured or
calculated, before they trust it. Many groups must report values from specific
approved sources.

## Decision
No bare values. Every `PropertyValue` includes:
- the source database, record ID and URL;
- `kind`: measured, computed or predicted;
- the original citation, when the source provides one;
- measurement conditions (for example temperature, pH, solvent), when known;
- when the value was retrieved.

## Consequences
- Results are traceable and auditable, and conflicting values can be shown side by side.
- Responses are larger.
- Parsers must extract source details, not just values, which makes them more work to write.
