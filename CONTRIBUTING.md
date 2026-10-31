# Contributing

Thanks for your interest! pharmakon is in early development; issues and ideas are welcome.

## Setup
1. Install [uv](https://docs.astral.sh/uv/).
2. `uv sync` — installs all packages and dev tools.
3. `uv run pre-commit install` — runs lint and format checks before each commit.

## Before opening a pull request
- `uv run pytest` passes (offline tests).
- `uv run ruff check` and `uv run pyright` are clean.
- New behavior has tests; tests for a requirement are marked `@pytest.mark.req("REQ-…")`.
- CHANGELOG.md has an entry under "Unreleased".
- Significant design changes come with an ADR in docs/decisions/.

## Testing a server by hand
`npx @modelcontextprotocol/inspector uv run pharmakon-pubchem` opens the MCP Inspector,
where you can call each tool and see the raw results.

## License of contributions
By submitting a contribution, you agree it is licensed under Apache-2.0, as described
in section 5 of the [LICENSE](LICENSE).
