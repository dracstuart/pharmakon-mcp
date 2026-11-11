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
### Changed
- Minimum Python version is now 3.11 (ADR 0013).
- Dependabot updates only `uv.lock` for Python dependencies and no longer raises version floors in `pyproject.toml`.
