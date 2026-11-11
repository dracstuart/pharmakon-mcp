"""Recognize, validate and normalize molecule identifiers.

Recognition is pattern-based and works without RDKit. When an input could be more than
one kind of identifier, every plausible type is returned ranked, and ``Recognition.best``
is ``None``, so callers never get a silent guess. See ADR 0003 and REQ-CORE-001 to 007.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class IdentifierType(StrEnum):
    """Built-in identifier types."""

    INCHIKEY = "inchikey"
    INCHI = "inchi"
    SMILES = "smiles"
    CAS = "cas"
    PUBCHEM_CID = "pubchem_cid"
    CHEMBL_ID = "chembl_id"
    UNII = "unii"
    WIKIDATA_QID = "wikidata_qid"
    SEQUENCE = "sequence"
    HELM = "helm"
    NAME = "name"


class Confidence(StrEnum):
    """How sure recognition is that an input has a given type."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


_CONFIDENCE_RANK = {Confidence.HIGH: 0, Confidence.MEDIUM: 1, Confidence.LOW: 2}
_BUILTIN_NAMES = frozenset(t.value for t in IdentifierType)


class InvalidIdentifierError(ValueError):
    """An identifier failed validation. The message explains why."""


class CustomIdentifierType(BaseModel):
    """An identifier type defined in configuration, such as an internal compound number."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(pattern=r"^[a-z][a-z0-9_]*$", description="Lowercase name, e.g. acme_id")
    pattern: str = Field(description="Regular expression that must match the whole input")
    description: str | None = None

    @field_validator("name")
    @classmethod
    def _not_builtin(cls, name: str) -> str:
        if name in _BUILTIN_NAMES:
            raise ValueError(f"'{name}' is a built-in identifier type; choose another name")
        return name

    @field_validator("pattern")
    @classmethod
    def _compiles(cls, pattern: str) -> str:
        try:
            re.compile(pattern)
        except re.error as exc:
            raise ValueError(f"not a valid regular expression: {exc}") from exc
        return pattern

    def matches(self, value: str) -> bool:
        return re.fullmatch(self.pattern, value) is not None


class Candidate(BaseModel):
    """One possible reading of an input."""

    model_config = ConfigDict(frozen=True)

    type: str = Field(description="An IdentifierType value, or the name of a custom type")
    value: str = Field(description="The normalized identifier")
    confidence: Confidence
    reason: str
    custom: bool = False


class Recognition(BaseModel):
    """The result of ``recognize``: every plausible reading, best first."""

    model_config = ConfigDict(frozen=True)

    input: str
    candidates: list[Candidate]
    notes: list[str] = Field(
        default_factory=list,
        description="Explanations for near misses, such as a CAS number with a bad check digit",
    )

    @computed_field
    @property
    def ambiguous(self) -> bool:
        """True when the top two candidates are equally likely."""
        c = self.candidates
        return len(c) > 1 and c[0].confidence == c[1].confidence

    @computed_field
    @property
    def best(self) -> Candidate | None:
        """The single best reading, or None when the input is ambiguous."""
        return None if self.ambiguous else self.candidates[0]


# --- Patterns --------------------------------------------------------------------------

_INCHIKEY = re.compile(r"[A-Z]{14}-[A-Z]{8}[SN][A-Z]-[A-Z]")
_INCHI = re.compile(r"InChI=1S?/\S+")
_CAS = re.compile(r"(\d{2,7})-(\d{2})-(\d)")
_CID_PREFIXED = re.compile(r"(?i)(?:pubchem\s*)?cid[\s:]*([1-9]\d*)")
_CID_BARE = re.compile(r"[1-9]\d*")
_CHEMBL = re.compile(r"(?i)chembl(\d+)")
_QID = re.compile(r"(?i)q([1-9]\d*)")
_UNII = re.compile(r"[A-Z0-9]{10}")
_HELM = re.compile(r"(?:PEPTIDE|RNA|CHEM|BLOB)\d+\{[^}]*\}.*")
# 20 standard amino acids plus selenocysteine (U) and pyrrolysine (O).
_SEQUENCE = re.compile(r"[ACDEFGHIKLMNPQRSTVWYUO]{2,}")

_SMILES_CHARS = re.compile(r"[A-Za-z0-9@+\-\[\]()=#$/\\%.:*~]+")
_SMILES_BRACKET_ATOM = re.compile(r"\[[^\[\]]+\]")
# Atoms allowed outside brackets: the organic subset, aromatic forms, and the wildcard.
_SMILES_BARE_ATOMS = re.compile(r"Cl|Br|[BCNOPSFI]|[bcnops]|\*")
_SMILES_SYNTAX_ONLY = re.compile(r"[\[\]()=#@/\\%.\d]|[bcnops]")


def _cas_check_digit(body: str) -> int:
    """CAS check digit: digits right to left, weighted 1, 2, 3 ..., sum mod 10."""
    return sum(i * int(d) for i, d in enumerate(reversed(body), start=1)) % 10


def _cas_problem(text: str) -> str | None:
    """Return why ``text`` is not a valid CAS number, or None if it is valid."""
    m = _CAS.fullmatch(text)
    if not m:
        return "CAS numbers have the form 2-7 digits, 2 digits, 1 check digit (e.g. 50-00-0)"
    expected = _cas_check_digit(m[1] + m[2])
    if int(m[3]) != expected:
        return f"CAS {text}: check digit should be {expected}, not {m[3]}"
    return None


def _smiles_problem(text: str) -> str | None:
    """Return why ``text`` does not look like SMILES, or None if it plausibly is.

    This is a syntax check only. Use ``pharmakon_core.structure.validate_smiles`` with
    RDKit installed for a real parse.
    """
    if not _SMILES_CHARS.fullmatch(text):
        return "contains characters that never appear in SMILES"
    if text.count("(") != text.count(")"):
        return "unbalanced parentheses"
    outside = _SMILES_BRACKET_ATOM.sub("", text)
    if "[" in outside or "]" in outside:
        return "unbalanced square brackets"
    letters = re.sub(r"[^A-Za-z*]", "", outside)
    if _SMILES_BARE_ATOMS.sub("", letters):
        return "contains letters that are not atoms outside square brackets"
    if not letters and not _SMILES_BRACKET_ATOM.search(text):
        return "contains no atoms"
    closures = re.findall(r"%\d\d|\d", outside)
    if any(closures.count(c) % 2 for c in set(closures)):
        return "a ring-closure number is opened but never closed"
    return None


# --- Recognition -----------------------------------------------------------------------


def recognize(text: str, custom_types: Sequence[CustomIdentifierType] = ()) -> Recognition:
    """Work out which kinds of identifier ``text`` could be.

    Candidates are ranked by confidence. A name candidate (always low confidence) is
    added when nothing matched with high confidence.

    Raises:
        InvalidIdentifierError: if ``text`` is empty.
    """
    s = text.strip()
    if not s:
        raise InvalidIdentifierError("empty input: nothing to recognize")

    found: list[Candidate] = []
    notes: list[str] = []

    def add(t: str, value: str, conf: Confidence, reason: str, custom: bool = False) -> None:
        found.append(Candidate(type=t, value=value, confidence=conf, reason=reason, custom=custom))

    H, M, L = Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW
    T = IdentifierType

    if _INCHIKEY.fullmatch(s.upper()):
        add(T.INCHIKEY, s.upper(), H, "matches the InChIKey format")
    if _INCHI.fullmatch(s):
        add(T.INCHI, s, H, "starts with the InChI prefix")
    if _CAS.fullmatch(s):
        problem = _cas_problem(s)
        if problem:
            notes.append(f"looks like a CAS number, but {problem}")
        else:
            add(T.CAS, s, H, "CAS format with a valid check digit")
    if m := _CID_PREFIXED.fullmatch(s):
        add(T.PUBCHEM_CID, m[1], H, "number labelled as a PubChem CID")
    elif _CID_BARE.fullmatch(s):
        add(T.PUBCHEM_CID, s, M, "a bare positive integer is most often a PubChem CID")
    if m := _CHEMBL.fullmatch(s):
        add(T.CHEMBL_ID, f"CHEMBL{m[1]}", H, "matches the ChEMBL ID format")
    if m := _QID.fullmatch(s):
        add(T.WIKIDATA_QID, f"Q{m[1]}", H, "matches the Wikidata item ID format")
    u = s.upper()
    if _UNII.fullmatch(u) and re.search(r"\d", u) and re.search(r"[A-Z]", u):
        add(T.UNII, u, M, "10 letters and digits, the FDA UNII format")
    if _HELM.fullmatch(s) and s.count("$") >= 4:
        add(T.HELM, s, H, "HELM polymer notation")
    if _SEQUENCE.fullmatch(s):
        add(T.SEQUENCE, s, M, "only one-letter amino acid codes")
    if _smiles_problem(s) is None and not _CID_BARE.fullmatch(s) and not _CAS.fullmatch(s):
        conf = H if _SMILES_SYNTAX_ONLY.search(s) and not _INCHIKEY.fullmatch(s) else M
        add(T.SMILES, s, conf, "looks like SMILES (syntax check only, not parsed)")
    for ct in custom_types:
        if ct.matches(s):
            add(ct.name, s, M, f"matches custom type '{ct.name}'", custom=True)

    if not any(c.confidence == H for c in found):
        add(T.NAME, " ".join(s.split()), L, "treated as a name; name matches are low confidence")

    order = list(IdentifierType)
    found.sort(
        key=lambda c: (
            _CONFIDENCE_RANK[c.confidence],
            order.index(IdentifierType(c.type)) if not c.custom else len(order),
        )
    )
    return Recognition(input=text, candidates=found, notes=notes)


# --- Validation ------------------------------------------------------------------------


def validate(type: IdentifierType | CustomIdentifierType, value: str) -> str:
    """Check that ``value`` is a valid identifier of ``type`` and return it normalized.

    Raises:
        InvalidIdentifierError: with a message explaining what is wrong.
    """
    s = value.strip()
    if isinstance(type, CustomIdentifierType):
        if not type.matches(s):
            raise InvalidIdentifierError(
                f"'{s}' does not match custom type '{type.name}' (pattern {type.pattern})"
            )
        return s

    T = IdentifierType

    def fail(msg: str) -> InvalidIdentifierError:
        return InvalidIdentifierError(f"invalid {type.value} '{s}': {msg}")

    match type:
        case T.INCHIKEY:
            if not _INCHIKEY.fullmatch(s.upper()):
                raise fail("expected 14 letters, hyphen, 10 letters, hyphen, 1 letter")
            return s.upper()
        case T.INCHI:
            if not _INCHI.fullmatch(s):
                raise fail("expected to start with 'InChI=1S/' or 'InChI=1/'")
            return s
        case T.CAS:
            if problem := _cas_problem(s):
                raise InvalidIdentifierError(problem)
            return s
        case T.PUBCHEM_CID:
            if m := _CID_PREFIXED.fullmatch(s):
                return m[1]
            if not _CID_BARE.fullmatch(s):
                raise fail("expected a positive whole number")
            return s
        case T.CHEMBL_ID:
            if not (m := _CHEMBL.fullmatch(s)):
                raise fail("expected 'CHEMBL' followed by digits, e.g. CHEMBL25")
            return f"CHEMBL{m[1]}"
        case T.UNII:
            if not _UNII.fullmatch(s.upper()):
                raise fail("expected 10 letters and digits, e.g. R16CO5Y76E")
            return s.upper()
        case T.WIKIDATA_QID:
            if not (m := _QID.fullmatch(s)):
                raise fail("expected 'Q' followed by digits, e.g. Q18216")
            return f"Q{m[1]}"
        case T.HELM:
            if not (_HELM.fullmatch(s) and s.count("$") >= 4):
                raise fail("expected HELM notation such as 'PEPTIDE1{A.G.C}$$$$V2.0'")
            return s
        case T.SEQUENCE:
            if not _SEQUENCE.fullmatch(s.upper()):
                raise fail("expected at least two one-letter amino acid codes")
            return s.upper()
        case T.SMILES:
            if problem := _smiles_problem(s):
                raise fail(problem)
            return s
        case T.NAME:
            if not s:
                raise fail("a name cannot be empty")
            return " ".join(s.split())
