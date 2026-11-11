import sys

import pytest

from pharmakon_core import structure
from pharmakon_core.identifiers import InvalidIdentifierError, recognize

ASPIRIN = "CC(=O)OC1=CC=CC=C1C(=O)O"


@pytest.fixture
def no_rdkit(monkeypatch):
    """Make RDKit unimportable, as if the extra were not installed."""
    for name in ("rdkit", "rdkit.Chem", "rdkit.rdBase"):
        monkeypatch.setitem(sys.modules, name, None)


@pytest.mark.req("REQ-CORE-006")
def test_without_rdkit_structure_tools_explain_what_to_install(no_rdkit):
    assert not structure.rdkit_available()
    with pytest.raises(structure.StructureToolUnavailable, match=r"pharmakon-core\[rdkit\]"):
        structure.inchikey_from_smiles(ASPIRIN)


@pytest.mark.req("REQ-CORE-006")
def test_without_rdkit_recognition_still_works(no_rdkit):
    r = recognize(ASPIRIN)
    assert r.best is not None
    assert r.best.type == "smiles"


rdkit = pytest.mark.skipif(not structure.rdkit_available(), reason="rdkit extra not installed")


@rdkit
@pytest.mark.req("REQ-CORE-007")
def test_canonical_smiles():
    assert structure.validate_smiles("OCC") == "CCO"


@rdkit
@pytest.mark.req("REQ-CORE-007")
def test_invalid_smiles_is_rejected():
    with pytest.raises(InvalidIdentifierError, match="could not parse"):
        structure.validate_smiles("C1CC")


@rdkit
@pytest.mark.req("REQ-CORE-007")
def test_local_inchi_and_inchikey():
    assert structure.inchi_from_smiles("C") == "InChI=1S/CH4/h1H4"
    assert structure.inchikey_from_smiles(ASPIRIN) == "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
