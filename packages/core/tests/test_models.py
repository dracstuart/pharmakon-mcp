import json
import os
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import BaseModel, ValidationError

from pharmakon_core.models import (
    BiologicReference,
    Citation,
    Conditions,
    CrossReference,
    Molecule,
    PropertyValue,
    Provenance,
    ValueKind,
)

SCHEMA_DIR = Path(__file__).resolve().parents[3] / "docs" / "schemas"

PUBCHEM_FIELDS = {
    "database": "pubchem",
    "record_id": "2244",
    "url": "https://pubchem.ncbi.nlm.nih.gov/compound/2244",
    "retrieved_at": datetime(2026, 11, 11, 12, 0, tzinfo=UTC),
}
PUBCHEM = Provenance.model_validate(PUBCHEM_FIELDS)


def logp(**overrides) -> PropertyValue:
    fields = {"property": "logp", "value": 1.2, "kind": "computed", "provenance": PUBCHEM}
    return PropertyValue(**(fields | overrides))


# --- Provenance (REQ-CORE-011) ----------------------------------------------------------


@pytest.mark.req("REQ-CORE-011")
@pytest.mark.parametrize("missing", ["provenance", "kind"])
def test_property_value_requires_provenance_and_kind(missing):
    fields = {"property": "logp", "value": 1.2, "kind": "computed", "provenance": PUBCHEM}
    del fields[missing]
    with pytest.raises(ValidationError, match=missing):
        PropertyValue(**fields)


@pytest.mark.req("REQ-CORE-011")
@pytest.mark.parametrize("missing", ["database", "record_id", "url", "retrieved_at"])
def test_provenance_requires_every_field(missing):
    fields = dict(PUBCHEM_FIELDS)
    del fields[missing]
    with pytest.raises(ValidationError, match=missing):
        Provenance.model_validate(fields)


@pytest.mark.req("REQ-CORE-011")
def test_retrieval_time_must_have_a_time_zone():
    fields = PUBCHEM_FIELDS | {"retrieved_at": datetime(2026, 11, 11, 12, 0)}
    with pytest.raises(ValidationError, match="timezone"):
        Provenance.model_validate(fields)


@pytest.mark.req("REQ-CORE-011")
def test_local_files_use_file_urls():
    fields = PUBCHEM_FIELDS | {"database": "acme_csv", "url": "file:///data/acme.csv"}
    assert str(Provenance.model_validate(fields).url) == "file:///data/acme.csv"


@pytest.mark.req("REQ-CORE-011")
def test_kind_must_be_measured_computed_or_predicted():
    assert logp(kind="measured").kind is ValueKind.MEASURED
    with pytest.raises(ValidationError, match="kind"):
        logp(kind="guessed")


@pytest.mark.req("REQ-CORE-011")
def test_unknown_fields_are_rejected():
    with pytest.raises(ValidationError, match="retreived_at"):
        Provenance.model_validate(PUBCHEM_FIELDS | {"retreived_at": PUBCHEM.retrieved_at})


# --- Values as reported -----------------------------------------------------------------


@pytest.mark.req("REQ-CORE-011")
def test_values_can_be_qualified_ranged_or_text():
    assert logp(property="solubility", value=100, qualifier=">", unit="mg/mL").qualifier == ">"
    assert logp(property="melting_point", value=50, value_max=60, unit="°C").value_max == 60
    assert logp(property="solubility", value=None, text="freely soluble").text


@pytest.mark.req("REQ-CORE-011")
@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"value": None}, "needs a number"),
        ({"value": 60, "value_max": 50}, "backwards"),
        ({"value": 50, "value_max": 60, "qualifier": ">"}, "cannot also have a qualifier"),
        ({"value": None, "text": "about 5", "qualifier": "~"}, "needs a number"),
        ({"value": float("nan")}, "finite"),
    ],
)
def test_inconsistent_values_are_rejected(overrides, message):
    with pytest.raises(ValidationError, match=message):
        logp(**overrides)


# --- Citation and conditions (REQ-CORE-012) -----------------------------------------------


@pytest.mark.req("REQ-CORE-012")
def test_citation_and_conditions_are_optional_and_kept():
    v = logp(
        kind="measured",
        method="shake flask",
        citation=Citation(text="Hansch C et al. (1995)", doi="10.1021/bk-1995-0606"),
        conditions=Conditions(temperature="25 °C", ph=7.4, other={"buffer": "phosphate"}),
    )
    assert v.citation is not None and v.citation.doi == "10.1021/bk-1995-0606"
    assert v.conditions is not None and v.conditions.temperature == "25 °C"
    assert logp().citation is None and logp().conditions is None


@pytest.mark.req("REQ-CORE-012")
def test_ph_must_be_on_the_ph_scale():
    with pytest.raises(ValidationError, match="ph"):
        Conditions(ph=15)


# --- Molecule (REQ-CORE-010) --------------------------------------------------------------


@pytest.mark.req("REQ-CORE-010")
def test_molecule_holds_identifiers_structure_xrefs_and_properties():
    m = Molecule(
        name="aspirin",
        synonyms=["acetylsalicylic acid"],
        smiles="CC(=O)OC1=CC=CC=C1C(=O)O",
        inchikey="bsynrymutxbxsq-uhfffaoysa-n",
        xrefs=[
            CrossReference(type="chembl_id", value="chembl25", source="pubchem"),
            CrossReference(type="cas", value="50-78-2"),
            CrossReference(type="acme_id", value=" ACME-000123 "),
        ],
        properties=[logp()],
        provenance=[PUBCHEM],
    )
    assert m.inchikey == "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
    assert [x.value for x in m.xrefs] == ["CHEMBL25", "50-78-2", "ACME-000123"]


@pytest.mark.req("REQ-CORE-010")
def test_peptide_molecule_has_sequence_and_helm():
    m = Molecule(name="example peptide", sequence="GIVEQCC", helm="PEPTIDE1{G.I.V}$$$$V2.0")
    assert m.sequence == "GIVEQCC"


@pytest.mark.req("REQ-CORE-010")
@pytest.mark.parametrize(
    ("field", "bad"),
    [("inchikey", "not-a-key"), ("smiles", "C1CC"), ("sequence", "B"), ("helm", "A.G.C")],
)
def test_molecule_rejects_invalid_identifiers(field, bad):
    with pytest.raises(ValidationError, match=field):
        Molecule(**{field: bad})


@pytest.mark.req("REQ-CORE-010")
def test_xref_with_invalid_builtin_identifier_is_rejected():
    with pytest.raises(ValidationError, match="check digit"):
        CrossReference(type="cas", value="50-78-3")


@pytest.mark.req("REQ-CORE-010")
def test_molecule_needs_something_that_identifies_it():
    with pytest.raises(ValidationError, match="at least one of"):
        Molecule(properties=[logp()])


# --- BiologicReference (REQ-CORE-014) -----------------------------------------------------


@pytest.mark.req("REQ-CORE-014")
def test_biologic_reference():
    b = BiologicReference(
        name="example antibody",
        inn="examplizumab",
        xrefs=[CrossReference(type="unii", value="r16co5y76e")],
        sequence="EVQLVESGGGLVQPGG",
    )
    assert b.inn == "examplizumab"
    assert b.xrefs[0].value == "R16CO5Y76E"


@pytest.mark.req("REQ-CORE-014")
def test_biologic_reference_needs_a_name():
    with pytest.raises(ValidationError, match="name"):
        BiologicReference(name="")


# --- Round trip and immutability ----------------------------------------------------------


@pytest.mark.req("REQ-CORE-013")
def test_json_round_trip():
    m = Molecule(
        name="aspirin", properties=[logp(citation=Citation(text="x"))], provenance=[PUBCHEM]
    )
    assert Molecule.model_validate_json(m.model_dump_json()) == m


def test_models_are_immutable():
    with pytest.raises(ValidationError, match="frozen"):
        logp().value = 2.0  # pyright: ignore[reportAttributeAccessIssue]


# --- Saved schemas (REQ-CORE-013) ---------------------------------------------------------

PUBLIC_MODELS: dict[str, type[BaseModel]] = {
    "molecule": Molecule,
    "biologic_reference": BiologicReference,
    "property_value": PropertyValue,
}


@pytest.mark.req("REQ-CORE-013")
@pytest.mark.parametrize("name", PUBLIC_MODELS)
def test_json_schema_matches_saved_copy(name):
    current = json.dumps(PUBLIC_MODELS[name].model_json_schema(), indent=2, ensure_ascii=False)
    path = SCHEMA_DIR / f"{name}.json"
    if os.environ.get("PHARMAKON_UPDATE_SCHEMAS") == "1":
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(current + "\n", encoding="utf-8")
    assert path.exists(), f"{path} missing; run PHARMAKON_UPDATE_SCHEMAS=1 uv run pytest"
    assert path.read_text(encoding="utf-8") == current + "\n", (
        f"The public format of {PUBLIC_MODELS[name].__name__} changed. If this is deliberate, "
        "run PHARMAKON_UPDATE_SCHEMAS=1 uv run pytest and commit docs/schemas/. "
        "Changing or removing a field is a breaking change."
    )
