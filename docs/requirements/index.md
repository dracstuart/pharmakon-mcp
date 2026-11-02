# Requirements

Requirements are written as code: plain Markdown, reviewed in pull requests, and
linked to the tests that verify them.

## Conventions
- **IDs** look like `REQ-<AREA>-NNN` (for example `REQ-CORE-011`). IDs are never
  reused; a dropped requirement stays listed with the status "Withdrawn".
- **Must** means required. **Should** means expected unless there is a stated reason
  not to.
- **ADR** names the architecture decision record the requirement comes from
  (see [docs/decisions](../decisions/)).
- **Phase:** P1 (first release), P1.5 (follow-up), P2 (later).
- **Verify:** T = automated test, I = inspection (for example code review).
- Tests that verify a requirement are marked `@pytest.mark.req("REQ-…")`.

## Areas
| Area | File |
|---|---|
| Core library (`pharmakon-core`) | [core.md](core.md) |
