# Changelog

All notable changes are recorded here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/); all packages share one version.

## [Unreleased]
### Added
- Repository structure, license, contribution guidelines, and architecture decision records.
- Requirements for the core library (`docs/requirements/`).
- EPA CompTox Chemicals Dashboard API added to the roadmap as a planned toxicity data source.
- `pharmakon-core` package skeleton with a `pharmakon --version` command.
- CI (lint, type checks, tests on Python 3.11–3.14) and Dependabot.
- `pharmakon_core.identifiers`: recognize, validate and normalize InChIKey, InChI, SMILES, CAS, PubChem CID, ChEMBL ID, UNII, Wikidata QID, amino acid sequence, HELM, names and custom identifier types. Ambiguous input returns ranked candidates and no single guess.
- `pharmakon_core.structure`: canonical SMILES, InChI and InChIKey with the optional `rdkit` extra.
- Dependency on `pydantic` (v2); optional extra `pharmakon-core[rdkit]`.
- `pharmakon_core.models`: `Molecule`, `BiologicReference`, `PropertyValue` with required provenance (`Provenance`, `ValueKind`), optional `Citation` and `Conditions`, and `CrossReference`. Values keep their original form, including qualifiers ("> 100"), ranges and text.
- Saved JSON Schemas for the public models in `docs/schemas/`, checked by the tests.
### Changed
- Minimum Python version is now 3.11 (ADR 0013).
- Dependabot updates only `uv.lock` for Python dependencies and no longer raises version floors in `pyproject.toml`.
