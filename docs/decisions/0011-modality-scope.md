# 0011. Modality scope: structure for synthesized parts, references for expressed parts

- **Status:** Proposed — pending domain review
- **Date:** 2026-10-31

## Context
pharmakon covers therapeutics whose production involves significant chemical
synthesis: small molecules, peptides, and conjugates such as antibody–drug conjugates
(ADCs). Large biologics like antibodies are produced biologically and do not need
full structural detail here, but conjugates combine both kinds of parts.

In an ADC, drug-linkers attach at several sites on the antibody, so the antibody is
not simply the end of a chain.

## Decision
- The dividing line is how a part is made, not its size:
  - **synthesized parts** get full structure (SMILES, InChIKey, or HELM for peptides);
  - **expressed parts** get a `BiologicReference` (name, INN, identifiers, optional sequence).
- About 50 amino acids is the default boundary between peptide and protein; it is
  configurable.
- Models:
  - `Molecule` — small molecules and peptides (with sequence and HELM where relevant);
  - `Conjugate` — payload, linker, drug-linker, carrier, conjugation chemistry and
    average drug-to-antibody ratio (DAR), plus a generated display name such as
    "MMAE – mc-vc-PABC – brentuximab";
  - `BiologicReference` — antibodies and large proteins.
- HELM for a whole conjugate is stored when a source provides it.
- Scope order: small molecules and peptides, then ADCs, then oligonucleotides.

## Consequences
- Searches by payload, linker, drug-linker or antibody can all find a conjugate.
- Conjugation sites and DAR distribution are not modeled yet; they can be added as
  optional fields without a breaking change.
- To be reviewed with an ADC synthesis chemist before acceptance.
