# pharmakon-mcp

Public, Apache-2.0 Python monorepo of MCP servers and a shared library for drug and
molecule data (small molecules, peptides, conjugates such as ADCs). Owner: Andrew Stuart.

## Ground rules
- **Ask before creating or changing files.** Propose changes, wait for approval.
- **This repo is public.** Never add customer names, customer data, business strategy,
  or anything about the private HyphaRXN product. Use made-up or public example data only.
- Never commit secrets. API keys and credentials come from environment variables.

## Architecture (see docs/decisions/ for the reasoning)
- **Library first.** All logic lives in importable packages (`packages/core`, each
  server's `client.py`/`parse.py`). MCP, CLI and (later) REST are thin front doors.
  `server.py` files contain tool definitions only and must not hold business logic.
- **Provenance on every value.** Every `PropertyValue` records its source, record ID,
  and whether it is measured, computed or predicted. Never return a bare number.
- **Units:** keep the original value and unit; convert to profile units only when
  unambiguous; otherwise return the original with a note explaining why it was not converted.
- **HTTP:** all network calls go through `pharmakon_core.http` (proxy, custom CA,
  rate limits, retries, User-Agent). No direct `urllib`/`httpx` calls in servers.
- **Modalities:** synthesized parts get structure (SMILES/InChIKey/HELM); expressed
  parts (antibodies, large proteins) get a `BiologicReference`.
- Pydantic models are a public contract: changing or removing a field is a breaking change.

## Layout
- `packages/core/` — `pharmakon-core`: identifiers, models, units, profiles, sources, http, cache
- `servers/<db>/` — one MCP server per data source (`pharmakon-<db>`)
- `apps/` — later: REST API, profile editor
- `docs/requirements/` — requirements with stable IDs (`REQ-<AREA>-NNN`)
- `docs/decisions/` — ADRs (`NNNN-title.md`); never edit an accepted ADR, supersede it

## Commands
- Install everything: `uv sync`
- Tests (offline): `uv run pytest`
- Live API tests: `PHARMAKON_LIVE_TESTS=1 uv run pytest -m live`
- Lint/format: `uv run ruff check --fix && uv run ruff format`
- Type check: `uv run pyright`
- Try a server interactively: `npx @modelcontextprotocol/inspector uv run pharmakon-<db>`

## Testing conventions
- Default tests are offline and use saved API responses in `tests/fixtures/`.
- Tests that hit real APIs are marked `@pytest.mark.live` and skipped by default.
- Tests that verify a requirement reference its ID: `@pytest.mark.req("REQ-CORE-003")`.

## Workflow
- Branch from `main`, open a PR, CI must pass before merge. No direct pushes to `main`.
- Commit messages: plain imperative sentences ("Add PubChem client"), no prefixes.
- All packages share one version number (lockstep). Update CHANGELOG.md in each PR.
