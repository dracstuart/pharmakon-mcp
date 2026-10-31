# 0007. Pluggable data sources

- **Status:** Proposed
- **Date:** 2026-10-31

## Context
Some groups require values from specific sources. Those may be public databases or
their own lists of accepted values, kept in spreadsheets, CSV files, databases or
internal web services. Users need to add such sources without changing pharmakon's code.

## Decision
- `pharmakon-core` defines one **Source** interface: given a molecule, return
  `PropertyValue`s with full provenance (ADR 0004).
- PubChem, ChEMBL and Wikidata are built-in sources.
- Users register additional sources in configuration. Built-in source types: **CSV**,
  **Excel** and **SQLite**, with column mapping and an identifier column for matching.
- Other source types are added as **plugins**: separate Python packages, discovered
  through Python entry points, that implement the Source interface.
- Rows are matched on InChIKey, SMILES or a configured custom identifier. Name-only
  matches are flagged as low-confidence.
- Credentials come from environment variables, never from configuration files.
- PDFs are not read as live sources. Values in PDFs should be imported once into a
  structured file, with a person reviewing them.
- Provenance for user sources includes the file or source name, its version or date,
  and a status such as "accepted value".

## Consequences
- Organizations can use their own approved data alongside public data.
- Internal data is read where pharmakon runs; nothing is sent elsewhere.
- The Source interface becomes a public contract that plugins depend on.
