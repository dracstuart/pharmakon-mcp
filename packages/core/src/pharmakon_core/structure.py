"""Structure tools that need RDKit: SMILES parsing, canonical SMILES, InChI and InChIKey.

RDKit is optional (``pip install 'pharmakon-core[rdkit]'``). Without it, every function
here raises ``StructureToolUnavailable`` with a message saying what to install, and the
rest of pharmakon-core keeps working. See ADR 0003, REQ-CORE-006 and REQ-CORE-007.
"""

from __future__ import annotations

import importlib
from typing import Any

from pharmakon_core.identifiers import InvalidIdentifierError


class StructureToolUnavailable(RuntimeError):
    """A structure operation needs RDKit, which is not installed."""


_UNAVAILABLE = (
    "{what} needs RDKit, which is not installed. Install it with "
    "pip install 'pharmakon-core[rdkit]', or look the structure up in a network source "
    "such as PubChem."
)


def _rdkit(what: str) -> tuple[Any, Any]:
    """Return the ``rdkit.Chem`` and ``rdkit.rdBase`` modules, or explain how to get them."""
    try:
        chem = importlib.import_module("rdkit.Chem")
        base = importlib.import_module("rdkit.rdBase")
    except ImportError as exc:
        raise StructureToolUnavailable(_UNAVAILABLE.format(what=what)) from exc
    return chem, base


def rdkit_available() -> bool:
    """True if RDKit can be imported."""
    try:
        _rdkit("check")
    except StructureToolUnavailable:
        return False
    return True


def _parse(smiles: str, what: str) -> tuple[Any, Any]:
    chem, base = _rdkit(what)
    s = smiles.strip()
    _block = base.BlockLogs()  # keep RDKit parse warnings off stderr while parsing
    mol = chem.MolFromSmiles(s) if s else None
    del _block
    if mol is None:
        raise InvalidIdentifierError(f"invalid smiles '{s}': RDKit could not parse it")
    return chem, mol


def validate_smiles(smiles: str) -> str:
    """Parse ``smiles`` with RDKit and return its canonical form."""
    chem, mol = _parse(smiles, "SMILES validation")
    return chem.MolToSmiles(mol)


def inchi_from_smiles(smiles: str) -> str:
    """Compute the standard InChI for ``smiles`` locally."""
    chem, mol = _parse(smiles, "InChI computation")
    inchi = chem.MolToInchi(mol)
    if not inchi:
        raise InvalidIdentifierError(f"RDKit could not compute an InChI for '{smiles}'")
    return inchi


def inchikey_from_smiles(smiles: str) -> str:
    """Compute the standard InChIKey for ``smiles`` locally."""
    chem, mol = _parse(smiles, "InChIKey computation")
    key = chem.MolToInchiKey(mol)
    if not key:
        raise InvalidIdentifierError(f"RDKit could not compute an InChIKey for '{smiles}'")
    return key
