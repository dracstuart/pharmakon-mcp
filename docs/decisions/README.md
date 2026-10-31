# Architecture decision records

Each file records one significant decision: its **context**, the **decision**, and its
**consequences**. Files are numbered in order (`NNNN-short-title.md`).

- **Status** is one of: Proposed, Accepted, Superseded by NNNN.
- Accepted records are not edited. To change a decision, write a new record that
  supersedes the old one, and update the old record's status line only.

| ADR | Title | Status |
|---|---|---|
| [0001](0001-python-uv-monorepo.md) | Python and a uv workspace monorepo | Accepted |
| [0002](0002-apache-2-license.md) | Apache-2.0 license | Accepted |
| [0003](0003-identifiers.md) | Identifiers: InChIKey, sequence/HELM, cross-references | Accepted |
| [0004](0004-provenance-on-every-value.md) | Every value records where it came from | Accepted |
| [0005](0005-proxy-and-custom-ca.md) | Works behind corporate proxies and inspecting web filters | Accepted |
