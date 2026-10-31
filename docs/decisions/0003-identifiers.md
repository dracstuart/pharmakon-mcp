# 0003. Identifiers: InChIKey for small molecules, sequence/HELM for peptides, cross-references for everything

- **Status:** Accepted
- **Date:** 2026-10-31

## Context
Databases identify molecules differently (PubChem CID, ChEMBL ID, CAS number, names).
Combining sources needs a common key. InChIKey works well for small molecules but
poorly for peptides and larger molecules.

## Decision
- `pharmakon-core` recognizes and normalizes: InChIKey, SMILES, InChI, CAS number
  (with checksum validation), PubChem CID, ChEMBL ID, UNII, Wikidata QID, amino acid
  sequence, HELM, and drug names (including INNs).
- InChIKey is the common key for small molecules; HELM, or the sequence, for peptides.
- Every record carries cross-references to the identifiers it has in other databases.
- Custom identifier types (for example internal compound numbers) can be defined in
  configuration.
- RDKit is an optional extra (`pharmakon-core[rdkit]`). Without it, structure
  conversions are delegated to PubChem.

## Consequences
- Results from different sources can be combined reliably.
- Matches made by name alone are treated as low-confidence.
- Installs without RDKit stay lightweight but need network access for conversions.
