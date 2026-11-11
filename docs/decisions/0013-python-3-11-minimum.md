# 0013. Raise the minimum Python version to 3.11

- **Status:** Accepted
- **Date:** 2026-11-02
- **Supersedes:** the Python version in [0001](0001-python-uv-monorepo.md)

## Context
ADR 0001 set Python 3.10 as the minimum. Python 3.10 reached end of life in
October 2026: it no longer receives security fixes, and libraries are starting to
drop support for it.

## Decision
- The minimum supported Python version is 3.11.
- CI tests every supported version that the project's dependencies support:
  currently 3.11, 3.12, 3.13 and 3.14.
- Python 3.15 is added to CI once the dependencies publish support for it.
- When a Python version reaches end of life, the minimum is raised in a new ADR.

## Consequences
- Users on Python 3.10 must upgrade to use pharmakon.
- The code can use 3.11 features, such as `tomllib` and `ExceptionGroup`.
