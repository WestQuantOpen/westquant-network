"""WestQuant Network trace — common trace format for all backends."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TraceEvent(BaseModel):
    """A single trace event in the common WestQuant format."""

    timestamp: float = Field(description="Event timestamp (s)")
    backend: str = Field(description="Backend name")
    node: str | None = Field(default=None, description="Node ID")
    component: str | None = Field(default=None, description="Component name")
    event_type: str = Field(description="Event type")
    request_id: str | None = Field(default=None, description="Request ID")
    pair_id: str | None = Field(default=None, description="Entangled pair ID")
    memory_id: str | None = Field(default=None, description="Memory slot ID")
    link_id: str | None = Field(default=None, description="Link ID")
    route_id: str | None = Field(default=None, description="Route ID")
    fidelity: float | None = Field(default=None, description="Current fidelity")
    age: float | None = Field(default=None, description="Pair age (s)")
    state: str | None = Field(default=None, description="State name")
    action: str | None = Field(default=None, description="Action taken")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class Trace(BaseModel):
    """A complete simulation trace."""

    experiment_id: str = Field(description="Experiment ID")
    backend: str = Field(description="Backend name")
    events: list[TraceEvent] = Field(default_factory=list)

    def add(self, event: TraceEvent) -> None:
        """Add a trace event."""
        self.events.append(event)

    def to_jsonl(self) -> str:
        """Export as JSON Lines."""
        return "\n".join(e.model_dump_json() for e in self.events)
