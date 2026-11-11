import pytest
from pydantic import ValidationError

from pharmakon_core.identifiers import (
    Confidence,
    CustomIdentifierType,
    IdentifierType,
    InvalidIdentifierError,
    recognize,
    validate,
)

T = IdentifierType


@pytest.mark.req("REQ-CORE-001")
@pytest.mark.parametrize(
    ("text", "expected_type", "expected_value"),
    [
        ("BSYNRYMUTXBXSQ-UHFFFAOYSA-N", T.INCHIKEY, "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"),
        ("InChI=1S/CH4/h1H4", T.INCHI, "InChI=1S/CH4/h1H4"),
        ("CC(=O)OC1=CC=CC=C1C(=O)O", T.SMILES, "CC(=O)OC1=CC=CC=C1C(=O)O"),
        ("[Na+].[Cl-]", T.SMILES, "[Na+].[Cl-]"),
        ("50-78-2", T.CAS, "50-78-2"),
        ("CID 2244", T.PUBCHEM_CID, "2244"),
        ("2244", T.PUBCHEM_CID, "2244"),
        ("chembl25", T.CHEMBL_ID, "CHEMBL25"),
        ("R16CO5Y76E", T.UNII, "R16CO5Y76E"),
        ("Q18216", T.WIKIDATA_QID, "Q18216"),
        ("GIVEQCCTSICSLYQLENYCN", T.SEQUENCE, "GIVEQCCTSICSLYQLENYCN"),
        ("PEPTIDE1{A.G.C}$$$$V2.0", T.HELM, "PEPTIDE1{A.G.C}$$$$V2.0"),
        ("acetylsalicylic acid", T.NAME, "acetylsalicylic acid"),
    ],
)
def test_recognizes_each_type(text, expected_type, expected_value):
    r = recognize(text)
    assert r.best is not None
    assert r.best.type == expected_type
    assert r.best.value == expected_value


@pytest.mark.req("REQ-CORE-001")
def test_ambiguous_input_returns_ranked_candidates_and_no_best():
    r = recognize("CCO")  # ethanol as SMILES, or Cys-Cys-Pyl as a sequence
    assert r.ambiguous
    assert r.best is None
    types = [c.type for c in r.candidates]
    assert {T.SMILES, T.SEQUENCE} <= set(types[:2])
    assert types[-1] == T.NAME


@pytest.mark.req("REQ-CORE-001")
def test_candidates_are_sorted_by_confidence():
    r = recognize("2244")
    ranks = [list(Confidence).index(c.confidence) for c in r.candidates]
    assert ranks == sorted(ranks)


@pytest.mark.req("REQ-CORE-001")
def test_high_confidence_match_has_no_name_fallback():
    assert [c.type for c in recognize("CHEMBL25").candidates] == [T.CHEMBL_ID]


@pytest.mark.req("REQ-CORE-001")
def test_empty_input_is_rejected():
    with pytest.raises(InvalidIdentifierError, match="empty"):
        recognize("   ")


@pytest.mark.req("REQ-CORE-001")
def test_recognition_serializes_best_and_ambiguous():
    data = recognize("CCO").model_dump()
    assert data["ambiguous"] is True
    assert data["best"] is None


@pytest.mark.req("REQ-CORE-002")
@pytest.mark.parametrize("cas", ["50-00-0", "7732-18-5", "50-78-2", "64-17-5"])
def test_valid_cas_numbers(cas):
    assert validate(T.CAS, cas) == cas


@pytest.mark.req("REQ-CORE-002")
def test_invalid_cas_check_digit_is_explained():
    with pytest.raises(InvalidIdentifierError, match="check digit should be 0, not 1"):
        validate(T.CAS, "50-00-1")


@pytest.mark.req("REQ-CORE-002")
def test_recognize_notes_a_cas_number_with_a_bad_check_digit():
    r = recognize("50-00-1")
    assert T.CAS not in [c.type for c in r.candidates]
    assert any("check digit" in n for n in r.notes)


@pytest.mark.req("REQ-CORE-002")
def test_malformed_cas_is_explained():
    with pytest.raises(InvalidIdentifierError, match="2-7 digits"):
        validate(T.CAS, "5-00-0")


@pytest.mark.req("REQ-CORE-003")
@pytest.mark.parametrize(
    ("id_type", "value", "normalized"),
    [
        (T.INCHIKEY, "bsynrymutxbxsq-uhfffaoysa-n", "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"),
        (T.CHEMBL_ID, "ChEMBL25", "CHEMBL25"),
        (T.UNII, "r16co5y76e", "R16CO5Y76E"),
        (T.WIKIDATA_QID, "q18216", "Q18216"),
    ],
)
def test_valid_formats_are_normalized(id_type, value, normalized):
    assert validate(id_type, value) == normalized


@pytest.mark.req("REQ-CORE-003")
@pytest.mark.parametrize(
    ("id_type", "value"),
    [
        (T.INCHIKEY, "BSYNRYMUTXBXSQ-UHFFFAOYSA"),
        (T.INCHIKEY, "BSYNRYMUTXBXSQ-UHFFFAOYXA-N"),
        (T.CHEMBL_ID, "CHEMBL"),
        (T.CHEMBL_ID, "CHEMBL25X"),
        (T.UNII, "R16CO5Y76"),
        (T.UNII, "R16CO5Y76E!"),
        (T.WIKIDATA_QID, "Q0"),
        (T.WIKIDATA_QID, "P31"),
    ],
)
def test_invalid_formats_are_rejected_with_explanation(id_type, value):
    with pytest.raises(InvalidIdentifierError, match=f"invalid {id_type.value}"):
        validate(id_type, value)


@pytest.mark.req("REQ-CORE-004")
def test_custom_identifier_type_is_recognized():
    acme = CustomIdentifierType(name="acme_id", pattern=r"ACME-\d{6}")
    r = recognize("ACME-001234", custom_types=[acme])
    assert r.best is not None
    assert r.best.type == "acme_id"
    assert r.best.custom
    assert validate(acme, "ACME-001234") == "ACME-001234"


@pytest.mark.req("REQ-CORE-004")
def test_custom_pattern_must_match_whole_input():
    acme = CustomIdentifierType(name="acme_id", pattern=r"ACME-\d{6}")
    with pytest.raises(InvalidIdentifierError, match="acme_id"):
        validate(acme, "ACME-0012345")


@pytest.mark.req("REQ-CORE-004")
@pytest.mark.parametrize(
    ("name", "pattern", "message"),
    [
        ("cas", r"\d+", "built-in"),
        ("Acme ID", r"\d+", "pattern"),
        ("acme_id", r"ACME-(\d+", "regular expression"),
    ],
)
def test_bad_custom_types_are_rejected(name, pattern, message):
    with pytest.raises(ValidationError, match=message):
        CustomIdentifierType(name=name, pattern=pattern)


@pytest.mark.req("REQ-CORE-005")
@pytest.mark.parametrize("text", ["aspirin", "acetylsalicylic acid", "50-00-1"])
def test_name_matches_are_low_confidence(text):
    names = [c for c in recognize(text).candidates if c.type == T.NAME]
    assert names
    assert all(c.confidence == Confidence.LOW for c in names)
    assert "low confidence" in names[0].reason


@pytest.mark.req("REQ-CORE-005")
def test_name_is_whitespace_normalized():
    assert validate(T.NAME, "  acetylsalicylic   acid ") == "acetylsalicylic acid"


@pytest.mark.req("REQ-CORE-001")
@pytest.mark.parametrize("text", ["CO2", "C1CC", "CC(C", "Na"])
def test_text_that_is_not_smiles_syntax_is_not_offered_as_smiles(text):
    assert T.SMILES not in [c.type for c in recognize(text).candidates]
