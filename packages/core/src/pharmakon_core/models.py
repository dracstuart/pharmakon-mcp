"""Data models with provenance on every value.

These models are a public contract: adding an optional field is fine, while changing or
removing one is a breaking change. A saved copy of each JSON Schema lives in
``docs/schemas/`` and is checked by the tests. See ADR 0004, ADR 0011 and
REQ-CORE-010 to 014.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal, Self

from pydantic import (
    AnyUrl,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    FiniteFloat,
    ValidationInfo,
    field_validator,
    model_validator,
)

from pharmakon_core.identifiers import IdentifierType, validate

_BUILTIN_TYPES = frozenset(t.value for t in IdentifierType)


class _Model(BaseModel):
    """Shared settings: immutable, and unknown fields are rejected."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class ValueKind(StrEnum):
    """How a value was obtained."""

    MEASURED = "measured"
    COMPUTED = "computed"
    PREDICTED = "predicted"


class Provenance(_Model):
    """Where a value or record came from (ADR 0004)."""

    database: str = Field(min_length=1, description="Source database, e.g. 'pubchem'")
    record_id: str = Field(min_length=1, description="Record ID in that database")
    url: AnyUrl = Field(description="Link to the record; file:// for local files")
    retrieved_at: AwareDatetime = Field(description="When the value was retrieved")


class Citation(_Model):
    """The original publication behind a value, when the source names one."""

    text: str = Field(min_length=1, description="Citation as given by the source")
    doi: str | None = None
    pmid: str | None = None


class Conditions(_Model):
    """Measurement conditions, exactly as reported. Never converted (REQ-CORE-024)."""

    temperature: str | None = Field(default=None, description="As reported, e.g. '25 °C'")
    ph: float | None = Field(default=None, ge=0, le=14)
    solvent: str | None = None
    other: dict[str, str] = Field(default_factory=dict, description="Any other stated condition")


Qualifier = Literal["<", "<=", ">", ">=", "~"]


class PropertyValue(_Model):
    """One reported value of one property, with its provenance (REQ-CORE-011, 012).

    ``value``, ``value_max``, ``qualifier``, ``unit`` and ``text`` hold the value exactly
    as the source reported it. Unit conversions are added alongside, never in place.
    """

    property: str = Field(min_length=1, description="Property name, e.g. 'logp', 'solubility'")
    value: FiniteFloat | None = Field(default=None, description="Number as reported")
    value_max: FiniteFloat | None = Field(
        default=None, description="Upper end when the source reports a range"
    )
    qualifier: Qualifier | None = Field(default=None, description="For values like '> 100'")
    unit: str | None = Field(default=None, description="Unit as reported; None if unitless")
    text: str | None = Field(
        default=None, description="Original wording, e.g. 'freely soluble' or '50-60 °C'"
    )
    kind: ValueKind
    method: str | None = Field(
        default=None, description="Method or predictor, e.g. 'XLogP3 3.0' or 'shake flask'"
    )
    provenance: Provenance
    citation: Citation | None = None
    conditions: Conditions | None = None
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _consistent(self) -> Self:
        if self.value is None and not self.text:
            raise ValueError("a property value needs a number (value) or wording (text)")
        if self.value_max is not None:
            if self.value is None:
                raise ValueError("value_max is set but value is missing; a range needs both")
            if self.value_max < self.value:
                raise ValueError(f"range runs backwards: {self.value} to {self.value_max}")
            if self.qualifier is not None:
                raise ValueError("a range cannot also have a qualifier such as '>'")
        if self.qualifier is not None and self.value is None:
            raise ValueError(f"qualifier '{self.qualifier}' needs a number in value")
        return self


class CrossReference(_Model):
    """An identifier for the same entity in another database."""

    type: str = Field(min_length=1, description="An IdentifierType value or a custom type name")
    value: str = Field(min_length=1, description="Normalized identifier")
    source: str | None = Field(default=None, description="Database that states this link")

    @field_validator("value")
    @classmethod
    def _normalize(cls, value: str, info: ValidationInfo) -> str:
        id_type = info.data.get("type")
        if id_type in _BUILTIN_TYPES:
            return validate(IdentifierType(id_type), value)
        return value.strip()


def _validated(id_type: IdentifierType, value: str | None) -> str | None:
    return None if value is None else validate(id_type, value)


class Molecule(_Model):
    """A small molecule or peptide: something with a defined structure (REQ-CORE-010)."""

    name: str | None = None
    synonyms: list[str] = Field(default_factory=list)
    smiles: str | None = None
    inchi: str | None = None
    inchikey: str | None = None
    sequence: str | None = Field(default=None, description="One-letter amino acid sequence")
    helm: str | None = None
    xrefs: list[CrossReference] = Field(default_factory=list)
    properties: list[PropertyValue] = Field(default_factory=list)
    provenance: list[Provenance] = Field(
        default_factory=list, description="Records this molecule was built from"
    )

    @field_validator("smiles")
    @classmethod
    def _smiles(cls, v: str | None) -> str | None:
        return _validated(IdentifierType.SMILES, v)

    @field_validator("inchi")
    @classmethod
    def _inchi(cls, v: str | None) -> str | None:
        return _validated(IdentifierType.INCHI, v)

    @field_validator("inchikey")
    @classmethod
    def _inchikey(cls, v: str | None) -> str | None:
        return _validated(IdentifierType.INCHIKEY, v)

    @field_validator("sequence")
    @classmethod
    def _sequence(cls, v: str | None) -> str | None:
        return _validated(IdentifierType.SEQUENCE, v)

    @field_validator("helm")
    @classmethod
    def _helm(cls, v: str | None) -> str | None:
        return _validated(IdentifierType.HELM, v)

    @model_validator(mode="after")
    def _identified(self) -> Self:
        fields = (self.name, self.synonyms, self.smiles, self.inchi, self.inchikey)
        if not any(fields + (self.sequence, self.helm, self.xrefs)):
            raise ValueError(
                "a molecule needs at least one of: name, synonyms, smiles, inchi, inchikey, "
                "sequence, helm or xrefs"
            )
        return self


class BiologicReference(_Model):
    """An expressed biologic such as an antibody, referenced rather than drawn (ADR 0011)."""

    name: str = Field(min_length=1)
    inn: str | None = Field(default=None, description="International Nonproprietary Name")
    xrefs: list[CrossReference] = Field(default_factory=list)
    sequence: str | None = Field(default=None, description="One-letter amino acid sequence")
    properties: list[PropertyValue] = Field(default_factory=list)
    provenance: list[Provenance] = Field(default_factory=list)

    @field_validator("sequence")
    @classmethod
    def _sequence(cls, v: str | None) -> str | None:
        return _validated(IdentifierType.SEQUENCE, v)
