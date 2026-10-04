"""Dataset generation for AI — state/action/reward export."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AIState(BaseModel):
    """Observable network state at time t."""

    timestamp: float = Field(description="Simulation time (s)")
    topology: dict[str, Any] = Field(description="Topology summary")
    link_states: dict[str, dict[str, Any]] = Field(
        default_factory=dict, description="Link states by link ID"
    )
    memory_states: dict[str, dict[str, Any]] = Field(
        default_factory=dict, description="Memory states by node ID"
    )
    request_queues: dict[str, list[dict[str, Any]]] = Field(
        default_factory=dict, description="Request queues by node ID"
    )
    routing_table: dict[str, Any] = Field(
        default_factory=dict, description="Current routing table"
    )


class AIAction(BaseModel):
    """An action proposed by the AI/optimization layer."""

    action_type: str = Field(description="Action type")
    route: list[str] | None = Field(default=None, description="Route (node IDs)")
    memory_policy: str | None = Field(default=None, description="Memory policy")
    swap_policy: str | None = Field(default=None, description="Swap policy")
    purification_policy: str | None = Field(
        default=None, description="Purification policy"
    )
    memory_id: str | None = Field(default=None, description="Target memory slot")
    params: dict[str, Any] = Field(
        default_factory=dict, description="Action parameters"
    )


class AIReward(BaseModel):
    """Reward signal for an action."""

    value: float = Field(description="Reward value")
    goodput: float | None = Field(default=None, description="Resulting goodput")
    fidelity: float | None = Field(default=None, description="Resulting fidelity")
    latency: float | None = Field(default=None, description="Resulting latency")
    constraints: dict[str, Any] = Field(
        default_factory=dict, description="Active constraints"
    )


class DatasetRecord(BaseModel):
    """A single (state, action, reward, next_state) record for AI training."""

    state: AIState = Field(description="State at time t")
    action: AIAction = Field(description="Action taken")
    reward: AIReward = Field(description="Reward received")
    next_state: AIState | None = Field(default=None, description="State at t+1")
    done: bool = Field(default=False, description="Episode finished")
    backend: str = Field(description="Backend name")
    experiment_id: str = Field(description="Experiment ID")
    seed: int = Field(description="Random seed")
    representation_id: str | None = Field(
        default=None, description="Representation ID for RepGraph"
    )
    provenance: dict[str, Any] = Field(
        default_factory=dict, description="Provenance metadata"
    )


class Dataset(BaseModel):
    """A collection of AI training records."""

    schema_version: str = Field(default="wqt-network-policy-v0.1")
    records: list[DatasetRecord] = Field(default_factory=list)

    def add(self, record: DatasetRecord) -> None:
        """Add a record."""
        self.records.append(record)

    def to_jsonl(self) -> str:
        """Export as JSON Lines."""
        return "\n".join(r.model_dump_json() for r in self.records)
