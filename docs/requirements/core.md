# Core library requirements (`pharmakon-core`)

## Identifiers
| ID | Requirement | ADR | Phase | Verify |
|---|---|---|---|---|
| REQ-CORE-001 | Must recognize the identifier type of InChIKey, InChI, SMILES, CAS number, PubChem CID, ChEMBL ID, UNII, Wikidata QID, amino acid sequence, HELM and name. Ambiguous input returns the plausible types ranked, never a silent guess. | 0003 | P1 | T |
| REQ-CORE-002 | Must validate CAS number check digits and reject invalid CAS numbers with an explanation. | 0003 | P1 | T |
| REQ-CORE-003 | Must validate the format of InChIKey, ChEMBL ID, UNII and Wikidata QID. | 0003 | P1 | T |
| REQ-CORE-004 | Must allow custom identifier types (name and pattern) defined in configuration. | 0003 | P1 | T |
| REQ-CORE-005 | Matches made by name alone must be flagged as low-confidence. | 0003 | P1 | T |
| REQ-CORE-006 | All core functions must work without RDKit. Structure conversions then go to a source, or fail with a clear message that RDKit or network access is needed. | 0003 | P1 | T |
| REQ-CORE-007 | With the `rdkit` extra installed: SMILES validation, canonical SMILES, and local InChI/InChIKey computation. | 0003 | P1 | T |

## Data models
| ID | Requirement | ADR | Phase | Verify |
|---|---|---|---|---|
| REQ-CORE-010 | `Molecule` holds identifiers, names and synonyms, structure (SMILES, InChI, InChIKey) or sequence/HELM, and cross-references. | 0003, 0011 | P1 | T |
| REQ-CORE-011 | A `PropertyValue` cannot be created without a source (database, record ID, URL), a kind (measured, computed or predicted) and a retrieval time. | 0004 | P1 | T |
| REQ-CORE-012 | `PropertyValue` supports an optional original citation and measurement conditions. | 0004 | P1 | T |
| REQ-CORE-013 | Models export JSON Schema, and a saved copy of the schema is checked in tests so any change to the public format is deliberate. | 0010 | P1 | T |
| REQ-CORE-014 | `BiologicReference` model: name, INN, identifiers, optional sequence. | 0011 | P1 | T |
| REQ-CORE-015 | `Conjugate` model as described in ADR 0011. | 0011 | P2 | T |

## Units
| ID | Requirement | ADR | Phase | Verify |
|---|---|---|---|---|
| REQ-CORE-020 | The original value and unit must always be preserved. | 0006 | P1 | T |
| REQ-CORE-021 | Must convert to the profile's primary and optional secondary units when dimensions are compatible. | 0006 | P1 | T |
| REQ-CORE-022 | Conversions between mass and molar concentration use the molecular weight and record which value was used and its source. | 0006 | P1 | T |
| REQ-CORE-023 | Must never convert between different properties (for example logP and logD). Values that cannot be converted are returned as the original plus a note explaining why. | 0006 | P1 | T |
| REQ-CORE-024 | Measurement conditions must never be altered. | 0006 | P1 | T |

## Profiles, source priority and access policy
| ID | Requirement | ADR | Phase | Verify |
|---|---|---|---|---|
| REQ-CORE-030 | Profiles are TOML files with a schema version field. | 0009 | P1 | T |
| REQ-CORE-031 | Settings layer in this order, most specific winning: built-in defaults, group profile, personal profile, per-request override. | 0006 | P1 | T |
| REQ-CORE-032 | Validation errors are in plain language and name the field at fault. | 0009 | P1 | T |
| REQ-CORE-033 | Loading and saving a profile loses nothing, including comments (uses `tomlkit`). | 0009 | P1 | T |
| REQ-CORE-034 | A preview function shows what a profile produces for an example molecule. | 0009 | P1 | T |
| REQ-CORE-035 | Per-property source order with the modes `first-available`, `only` and `all`. | 0008 | P1 | T |
| REQ-CORE-036 | Each result states which profile and rule produced it. | 0008 | P1 | T |
| REQ-CORE-037 | MCP tools to view and change a profile, confirming a plain-language summary before saving. | 0009 | P1 | T |
| REQ-CORE-038 | Source access policies support `deny` lists (block these sources) and `allow` lists (only these sources). | 0012 | P1 | T |
| REQ-CORE-039 | A lower settings layer can only make an access policy stricter, never looser. | 0012 | P1 | T |

## Sources
| ID | Requirement | ADR | Phase | Verify |
|---|---|---|---|---|
| REQ-CORE-040 | One `Source` interface returns `PropertyValue`s with full provenance. | 0007 | P1 | T |
| REQ-CORE-041 | Built-in CSV, Excel and SQLite sources with column mapping and an identifier column. | 0007 | P1 | T |
| REQ-CORE-042 | Plugin sources are discovered through the Python entry-point group `pharmakon.sources`. | 0007 | P1 | T |
| REQ-CORE-043 | Credentials come only from environment variables. Configuration files may reference them (for example `${DB_PASSWORD}`) but never contain them. | 0007 | P1 | T |
| REQ-CORE-044 | Provenance for user sources includes the file or source name, its version or date, and a status such as "accepted value". | 0007 | P1 | T |
| REQ-CORE-045 | A source blocked by access policy receives no network request at all. | 0012 | P1 | T |
| REQ-CORE-046 | Results report sources that were skipped because of access policy. | 0012 | P1 | T |

## Network
| ID | Requirement | ADR | Phase | Verify |
|---|---|---|---|---|
| REQ-CORE-050 | Honors `HTTPS_PROXY` and `NO_PROXY`. | 0005 | P1 | T |
| REQ-CORE-051 | Supports custom certificate files via `SSL_CERT_FILE` or `PHARMAKON_CA_BUNDLE`, and optional use of the operating system's trusted certificates. | 0005 | P1 | T |
| REQ-CORE-052 | Enforces per-source rate limits (PubChem: at most 5 requests per second). | 0005 | P1 | T |
| REQ-CORE-053 | Uses timeouts, and retries with backoff on HTTP 429 and 5xx responses, respecting `Retry-After`. | 0005 | P1 | T |
| REQ-CORE-054 | The User-Agent identifies pharmakon, its version and a project URL. | 0005 | P1 | T |
| REQ-CORE-055 | Provides an on-disk response cache with a configurable expiry that can be turned off. | 0005 | P1 | T |
| REQ-CORE-056 | Certificate errors explain the likely proxy cause and how to set the certificate settings. | 0005 | P1 | T |
| REQ-CORE-057 | Servers make no direct HTTP calls; all network access goes through `pharmakon_core.http`. | 0005 | P1 | I |

## Architecture
| ID | Requirement | ADR | Phase | Verify |
|---|---|---|---|---|
| REQ-CORE-060 | `pharmakon-core` must not depend on the `mcp` package. | 0010 | P1 | T |
| REQ-CORE-061 | A `pharmakon` command-line tool for lookups and profile management. | 0010 | P1 | T |
