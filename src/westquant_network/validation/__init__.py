"""Translation report — documents parameter translation status."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class TranslationStatus(str, Enum):
    """Status of a parameter translation between WestQuant and a backend.

    - EXACT: Parameter maps exactly to backend equivalent.
    - SEMANTICALLY_EQUIVALENT: Maps with same scientific meaning.
    - APPROXIMATED: Maps with some loss of fidelity/precision.
    - BACKEND_NATIVE: Backend uses its own native representation.
    - IGNORED: Parameter is silently ignored by the backend.
    - UNSUPPORTED: Backend cannot represent this parameter.
    - UNKNOWN: Translation status not yet determined.
    """

    EXACT = "EXACT"
    SEMANTICALLY_EQUIVALENT = "SEMANTICALLY_EQUIVALENT"
    APPROXIMATED = "APPROXIMATED"
    BACKEND_NATIVE = "BACKEND_NATIVE"
    IGNORED = "IGNORED"
    UNSUPPORTED = "UNSUPPORTED"
    UNKNOWN = "UNKNOWN"


class TranslationEntry(BaseModel):
    """A single parameter translation entry."""

    parameter: str = Field(description="WestQuant parameter name")
    status: TranslationStatus = Field(description="Translation status")
    backend_equivalent: str | None = Field(
        default=None, description="Backend parameter name"
    )
    notes: str | None = Field(default=None, description="Translation notes")
    warning: str | None = Field(
        default=None, description="Warning if translation is lossy"
    )


class TranslationReport(BaseModel):
    """Complete translation report for an experiment-backend pair."""

    backend: str = Field(description="Backend name")
    experiment_id: str = Field(description="Experiment ID")
    entries: list[TranslationEntry] = Field(
        default_factory=list, description="Translation entries"
    )

    @property
    def has_warnings(self) -> bool:
        """Whether any translation entry has a warning."""
        return any(e.warning is not None for e in self.entries)

    @property
    def has_unsupported(self) -> bool:
        """Whether any parameter is UNSUPPORTED."""
        return any(e.status == TranslationStatus.UNSUPPORTED for e in self.entries)

    @property
    def has_ignored(self) -> bool:
        """Whether any parameter is IGNORED."""
        return any(e.status == TranslationStatus.IGNORED for e in self.entries)

    def summary(self) -> dict[str, int]:
        """Count entries by status."""
        counts: dict[str, int] = {}
        for entry in self.entries:
            counts[entry.status.value] = counts.get(entry.status.value, 0) + 1
        return counts

    def add(
        self,
        parameter: str,
        status: TranslationStatus,
        backend_equivalent: str | None = None,
        notes: str | None = None,
        warning: str | None = None,
    ) -> None:
        """Add a translation entry."""
        self.entries.append(
            TranslationEntry(
                parameter=parameter,
                status=status,
                backend_equivalent=backend_equivalent,
                notes=notes,
                warning=warning,
            )
        )
