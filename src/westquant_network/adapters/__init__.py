"""Backend capability discovery — what each simulator supports."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CapabilityLevel(str, Enum):
    """Capability support level.

    - FULL: Backend fully supports this capability natively.
    - PARTIAL: Backend supports some aspects; adapter fills gaps.
    - OBSERVE_ONLY: Backend can expose state but not be controlled.
    - UNSUPPORTED: Backend cannot represent this capability.
    """

    FULL = "FULL"
    PARTIAL = "PARTIAL"
    OBSERVE_ONLY = "OBSERVE_ONLY"
    UNSUPPORTED = "UNSUPPORTED"


class MemoryCapabilities(BaseModel):
    """Memory-related capabilities."""

    capacity: bool = Field(default=True, description="Configurable capacity")
    T1: bool = Field(default=False, description="T1 decoherence")
    T2: bool = Field(default=False, description="T2 decoherence")
    write_efficiency: bool = Field(default=False, description="Write efficiency")
    read_efficiency: bool = Field(default=False, description="Read efficiency")
    write_latency: bool = Field(default=False, description="Write latency")
    read_latency: bool = Field(default=False, description="Read latency")
    multiplexing: bool = Field(default=False, description="Multiplexing modes")
    custom_decoherence: bool = Field(
        default=False, description="Custom decoherence model"
    )
    heterogeneous: bool = Field(
        default=False, description="Heterogeneous memories per node"
    )
    scheduling_policies: list[str] = Field(
        default_factory=list, description="Supported scheduling policies"
    )


class LinkCapabilities(BaseModel):
    """Link-related capabilities."""

    distance: bool = Field(default=True, description="Configurable distance")
    attenuation: bool = Field(default=False, description="Attenuation model")
    loss_probability: bool = Field(default=False, description="Explicit loss probability")
    source_rate: bool = Field(default=False, description="Source rate")
    detector_efficiency: bool = Field(default=False, description="Detector efficiency")
    detector_dark_count: bool = Field(default=False, description="Dark counts")
    classical_latency: bool = Field(default=False, description="Classical latency")
    asymmetric: bool = Field(default=False, description="Asymmetric links")


class RoutingCapabilities(BaseModel):
    """Routing-related capabilities."""

    static: bool = Field(default=True, description="Static routing")
    dynamic: bool = Field(default=False, description="Dynamic routing")
    multipath: bool = Field(default=False, description="Multipath routing")
    fidelity_aware: bool = Field(default=False, description="Fidelity-aware routing")
    memory_aware: bool = Field(default=False, description="Memory-aware routing")
    congestion_aware: bool = Field(default=False, description="Congestion-aware routing")
    policies: list[str] = Field(
        default_factory=list, description="Supported routing policies"
    )


class RepeaterCapabilities(BaseModel):
    """Repeater/swap capabilities."""

    swapping: bool = Field(default=True, description="Entanglement swapping")
    swap_success_probability: bool = Field(
        default=False, description="Configurable swap success"
    )
    swap_policies: list[str] = Field(
        default_factory=list, description="Supported swap policies"
    )
    purification: bool = Field(default=False, description="Purification support")
    purification_policies: list[str] = Field(
        default_factory=list, description="Supported purification policies"
    )


class StateFormalism(str, Enum):
    """Quantum state formalism."""

    PURE_STATE = "pure_state"
    DENSITY_MATRIX = "density_matrix"
    STABILIZER = "stabilizer"
    BELL_PAIR = "bell_pair"
    FIDELITY_ONLY = "fidelity_only"
    CUSTOM = "custom"


class ObservabilityCapabilities(BaseModel):
    """Observability capabilities."""

    network_state: bool = Field(default=False)
    link_state: bool = Field(default=False)
    memory_state: bool = Field(default=False)
    pair_age: bool = Field(default=False)
    pair_fidelity: bool = Field(default=False)
    routing_table: bool = Field(default=False)
    request_queues: bool = Field(default=False)
    resource_reservations: bool = Field(default=False)
    event_history: bool = Field(default=False)
    protocol_state: bool = Field(default=False)


class ActionInjectionCapabilities(BaseModel):
    """Dynamic action injection capabilities."""

    route: bool = Field(default=False, description="Can change route mid-simulation")
    memory_allocation: bool = Field(default=False)
    swap_order: bool = Field(default=False)
    purification_decision: bool = Field(default=False)
    admission_decision: bool = Field(default=False)
    priority: bool = Field(default=False)
    reservation: bool = Field(default=False)
    cutoff_time: bool = Field(default=False)


class BackendCapabilities(BaseModel):
    """Complete capability set for a backend."""

    backend_name: str = Field(description="Backend name")
    backend_version: str | None = Field(default=None, description="Backend version")

    memory: MemoryCapabilities = Field(default_factory=MemoryCapabilities)
    link: LinkCapabilities = Field(default_factory=LinkCapabilities)
    routing: RoutingCapabilities = Field(default_factory=RoutingCapabilities)
    repeater: RepeaterCapabilities = Field(default_factory=RepeaterCapabilities)
    observability: ObservabilityCapabilities = Field(
        default_factory=ObservabilityCapabilities
    )
    action_injection: ActionInjectionCapabilities = Field(
        default_factory=ActionInjectionCapabilities
    )

    state_formalisms: list[StateFormalism] = Field(
        default_factory=list, description="Supported state formalisms"
    )

    topologies: list[str] = Field(
        default_factory=list, description="Supported topology types"
    )

    max_nodes: int | None = Field(
        default=None, description="Maximum nodes tested (None = untested)"
    )

    installation_complexity: str = Field(
        default="UNKNOWN", description="LOW | MEDIUM | HIGH"
    )
    ci_friendly: str = Field(default="UNKNOWN", description="YES | PARTIAL | NO")
    license: str | None = Field(default=None, description="License")

    def supports(self, feature: str) -> bool:
        """Check if a feature is supported."""
        parts = feature.split(".")
        obj: Any = self
        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return False
        return bool(obj)

    def explain(self, feature: str) -> str:
        """Explain a feature's support level."""
        parts = feature.split(".")
        obj: Any = self
        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return f"Feature '{feature}' not found"
        if isinstance(obj, bool):
            return f"{feature}: {'supported' if obj else 'not supported'}"
        return f"{feature}: {obj}"
