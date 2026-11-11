# pharmakon-core

The shared library behind the pharmakon servers: identifier recognition, data models
with provenance, unit conversion, profiles and source policies, data sources, and a
network client that works behind corporate proxies.

It has no dependency on MCP, so it can be used directly from Python, the `pharmakon`
command line, or any other front end. See the
[requirements](../../docs/requirements/core.md) and
[architecture decisions](../../docs/decisions/).

## Identifiers

```python
>>> from pharmakon_core.identifiers import recognize, validate, IdentifierType
>>> recognize("CHEMBL25").best.type
'chembl_id'
>>> r = recognize("CCO")          # SMILES for ethanol, or a three-residue peptide?
>>> r.ambiguous, r.best
(True, None)
>>> [c.type for c in r.candidates]
['smiles', 'sequence', 'name']
>>> validate(IdentifierType.CAS, "50-00-1")
Traceback (most recent call last):
  ...
pharmakon_core.identifiers.InvalidIdentifierError: CAS 50-00-1: check digit should be 0, not 1
```

Install `pharmakon-core[rdkit]` for canonical SMILES and local InChI/InChIKey
computation (`pharmakon_core.structure`). Everything else works without RDKit.
