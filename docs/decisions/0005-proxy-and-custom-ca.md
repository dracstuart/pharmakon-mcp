# 0005. Works behind corporate proxies and certificate-inspecting web filters

- **Status:** Accepted
- **Date:** 2026-10-31

## Context
Enterprise networks often route traffic through web filters (for example Zscaler) that
inspect encrypted connections by substituting their own security certificate. Python
tools frequently fail in these environments with certificate errors.

## Decision
- All network access goes through one shared client in `pharmakon_core.http`.
- It respects `HTTPS_PROXY` and `NO_PROXY`, and custom certificate files
  (`SSL_CERT_FILE`, plus a pharmakon-specific setting), and can optionally use the
  operating system's trusted certificates.
- The same client handles per-source rate limits, retries, timeouts, caching and a
  descriptive User-Agent.

## Consequences
- pharmakon works out of the box in typical corporate setups.
- Network behavior is consistent and testable in one place.
- Servers must never make direct HTTP calls; code review enforces this.
