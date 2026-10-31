# 0006. User-configurable unit profiles

- **Status:** Proposed
- **Date:** 2026-10-31

## Context
Different groups in a pharmaceutical organization report the same property in
different units. Within a group the convention is usually consistent, often set by
the instrument software they use; between groups it differs. Sources also report in
mixed units (solubility as mg/mL, g/L or µM; temperatures in °C or °F).

It is not yet known whether groups also use the same property *name* for different
measurements (for example kinetic vs thermodynamic solubility). The design must leave
room for that.

## Decision
- Every `PropertyValue` keeps the **original** value and unit exactly as the source
  reported them.
- A **unit profile** sets, per property, a **primary** unit and an optional
  **secondary** unit. Values are converted to these in addition to the original.
- Settings are layered, most specific wins: built-in defaults → group profile file →
  personal overrides → a per-request choice (for example "show this in µM").
- Conversions that need chemistry (for example mg/mL ↔ µM) use the molecular weight
  and record which value was used.
- Conversions are made only when unambiguous. Different properties are never treated
  as unit changes (logP vs logD; pH-dependent solubility). Measurement conditions are
  never altered. When a conversion is not valid, the original is returned with a note
  explaining why.
- Unit handling uses the `pint` library (BSD).
- Profile structure is versioned and extensible, so property-name or definition
  mapping can be added later without breaking existing profiles.

## Consequences
- Each group sees values in the units it expects, while the original stays traceable.
- Profiles become a shared artifact that groups distribute among their members.
- More fields per value; conversion rules need careful tests.
