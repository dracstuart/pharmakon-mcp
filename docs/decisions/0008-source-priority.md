# 0008. Per-property source priority in group profiles

- **Status:** Proposed
- **Date:** 2026-10-31

## Context
Groups that care which source a value comes from want to set that per property: for
example density from an internal accepted-values list first, then PubChem.

## Decision
- The group profile (the same file as the unit profile, ADR 0006) lists, per property,
  an ordered list of sources and a mode:
  - `first-available`: use the first source that has a value;
  - `only`: use only the listed sources, never fall back;
  - `all`: return every source's value side by side.
- A combining layer queries sources in order, applies the mode, converts units, and
  returns values with provenance.

## Consequences
- Strict groups can guarantee that only approved values appear.
- The combining layer is the heart of the planned combined server.
- Results depend on configuration, so responses must make clear which profile and
  rule produced them.
