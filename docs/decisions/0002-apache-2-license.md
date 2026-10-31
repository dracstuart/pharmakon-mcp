# 0002. Apache-2.0 license

- **Status:** Accepted
- **Date:** 2026-10-31

## Context
The project is public and meant for adoption in pharmaceutical and research
organizations, whose legal teams favor permissive licenses with clear patent terms.
Copyleft licenses (GPL, AGPL) are often banned internally at such organizations.

## Decision
- All code in this repository is licensed under Apache-2.0.
- Copyright is held by Andrew Stuart and recorded in `NOTICE`.
- Contributions are accepted under Apache-2.0 section 5; no separate contributor
  agreement is required.
- Dependencies must be compatible with permissive and proprietary use (for example
  Apache, MIT, BSD). GPL and AGPL dependencies are not allowed.

## Consequences
- Anyone may use, modify and build on pharmakon, including commercially, and it can be
  embedded in other products.
- Data retrieved by pharmakon stays under each source's own license (see the README).
