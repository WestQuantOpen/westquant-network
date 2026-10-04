"""Network policies: routing, memory, swapping, purification, admission."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RoutingPolicyType(str, Enum):
    """Routing policy types."""

    SHORTEST_HOP = "shortest_hop"
    SHORTEST_DISTANCE = "shortest_distance"
    DIJKSTRA_COST = "dijkstra_cost"
    K_SHORTEST = "k_shortest"
    LOSS_AWARE = "loss_aware"
    FIDELITY_AWARE = "fidelity_aware"
    MEMORY_AWARE = "memory_aware"
    CONGESTION_AWARE = "congestion_aware"
    DEADLINE_AWARE = "deadline_aware"
    MULTIPATH = "multipath"
    CUSTOM = "custom"


class MemoryPolicyType(str, Enum):
    """Memory scheduling policy types."""

    FIFO = "fifo"
    LIFO = "lifo"
    OLDEST_FIRST = "oldest_first"
    YOUNGEST_FIRST = "youngest_first"
    FIDELITY_FIRST = "fidelity_first"
    DEADLINE_FIRST = "deadline_first"
    PRIORITY_FIRST = "priority_first"
    RANDOM = "random"
    MAX_WEIGHT = "max_weight"
    LEARNED = "learned"


class SwapPolicyType(str, Enum):
    """Entanglement swapping policy types."""

    SWAP_ASAP = "swap_asap"
    BALANCED_TREE = "balanced_tree"
    LEFT_TO_RIGHT = "left_to_right"
    RIGHT_TO_LEFT = "right_to_left"
    AGE_AWARE = "age_aware"
    FIDELITY_AWARE = "fidelity_aware"


class PurificationPolicyType(str, Enum):
    """Entanglement purification policy types."""

    NEVER = "never"
    ALWAYS = "always"
    FIDELITY_THRESHOLD = "fidelity_threshold"
    AGE_THRESHOLD = "age_threshold"
    ADAPTIVE = "adaptive"


class AdmissionPolicyType(str, Enum):
    """Request admission policy types."""

    ACCEPT_ALL = "accept_all"
    PRIORITY = "priority"
    DEADLINE = "deadline"
    RESOURCE = "resource"
    CUSTOM = "custom"


class RoutingPolicy(BaseModel):
    """Routing policy configuration."""

    policy_type: RoutingPolicyType = Field(
        default=RoutingPolicyType.SHORTEST_HOP,
        description="Routing policy type",
    )
    k: int = Field(default=3, ge=1, description="K for K_SHORTEST")
    fidelity_threshold: float = Field(
        default=0.9, ge=0, le=1, description="Fidelity threshold for FIDELITY_AWARE"
    )
    params: dict[str, Any] = Field(
        default_factory=dict, description="Policy-specific parameters"
    )


class MemoryPolicy(BaseModel):
    """Memory scheduling policy configuration."""

    policy_type: MemoryPolicyType = Field(
        default=MemoryPolicyType.FIFO,
        description="Memory scheduling policy type",
    )
    params: dict[str, Any] = Field(
        default_factory=dict, description="Policy-specific parameters"
    )


class SwapPolicy(BaseModel):
    """Entanglement swapping policy configuration."""

    policy_type: SwapPolicyType = Field(
        default=SwapPolicyType.SWAP_ASAP,
        description="Swap policy type",
    )
    params: dict[str, Any] = Field(
        default_factory=dict, description="Policy-specific parameters"
    )


class PurificationPolicy(BaseModel):
    """Purification policy configuration."""

    policy_type: PurificationPolicyType = Field(
        default=PurificationPolicyType.NEVER,
        description="Purification policy type",
    )
    fidelity_threshold: float = Field(
        default=0.95, ge=0, le=1, description="Threshold for FIDELITY_THRESHOLD"
    )
    age_threshold: float = Field(
        default=0.5, ge=0, description="Age threshold for AGE_THRESHOLD (s)"
    )
    params: dict[str, Any] = Field(
        default_factory=dict, description="Policy-specific parameters"
    )


class AdmissionPolicy(BaseModel):
    """Request admission policy configuration."""

    policy_type: AdmissionPolicyType = Field(
        default=AdmissionPolicyType.ACCEPT_ALL,
        description="Admission policy type",
    )
    params: dict[str, Any] = Field(
        default_factory=dict, description="Policy-specific parameters"
    )


class PolicySet(BaseModel):
    """Complete set of network policies for an experiment."""

    routing: RoutingPolicy = Field(default_factory=RoutingPolicy)
    memory: MemoryPolicy = Field(default_factory=MemoryPolicy)
    swapping: SwapPolicy = Field(default_factory=SwapPolicy)
    purification: PurificationPolicy = Field(default_factory=PurificationPolicy)
    admission: AdmissionPolicy = Field(default_factory=AdmissionPolicy)
