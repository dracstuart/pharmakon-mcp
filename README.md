# pharmakon-mcp

MCP servers and a Python library for looking up drug and molecule data — identifiers,
measured and computed properties, and drug information — across public databases,
with the source recorded on every value.

> **Status: early development.** Nothing is released yet. See the roadmap below.

## What it covers
- **Small molecules**, **peptides** (including modified and cyclic peptides via HELM),
  and **conjugates** such as antibody–drug conjugates (ADCs). Oligonucleotides are planned.
- Identifiers: InChIKey, SMILES, InChI, CAS, PubChem CID, ChEMBL ID, UNII, Wikidata QID,
  sequence, HELM.

## Roadmap
| Package | Status | What it does |
|---|---|---|
| `pharmakon-core` | In progress | Shared identifiers, data models, units, HTTP client |
| `pharmakon-pubchem` | Planned | Identifier resolution; computed and experimental properties |
| `pharmakon-chembl` | Planned | Drugs, mechanisms, targets, bioactivity, ADC components |
| `pharmakon-wikidata` | Planned | Identifier cross-references; Wikipedia pharmacokinetics |

Also planned: configurable unit and source-preference profiles, custom data sources
(CSV, Excel, SQLite), a REST API, and a combined server.

## Design
Architecture decisions are recorded in [docs/decisions](docs/decisions/), and
requirements in [docs/requirements](docs/requirements/).

## Data sources and licenses
pharmakon's code is Apache-2.0. Data it retrieves remains under each source's terms:
- **PubChem** (NCBI) — public domain data; see the [PubChem usage policy](https://www.ncbi.nlm.nih.gov/home/about/policies/).
- **ChEMBL** (EMBL-EBI) — [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/); attribution required.
- **Wikidata** — CC0. **Wikipedia** text — CC BY-SA 4.0.

Please respect each service's rate limits; pharmakon enforces them by default.

## Disclaimer
For research use only. Not for clinical or diagnostic decisions. Values come from
third-party sources and may be incomplete or wrong; always check the cited source.

## License
[Apache-2.0](LICENSE). Copyright 2026 Andrew Stuart.
