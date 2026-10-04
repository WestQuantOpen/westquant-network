"""Normalized simulation result and formal metric definitions."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LatencyStats(BaseModel):
    """Latency distribution statistics."""

    mean: float | None = None
    p50: float | None = None
    p95: float | None = None
    p99: float | None = None
    std: float | None = None


class FidelityStats(BaseModel):
    """Fidelity distribution statistics."""

    mean: float | None = None
    std: float | None = None
    min: float | None = None
    max: float | None = None
    quantiles: dict[str, float] = Field(default_factory=dict)


class SimulationResult(BaseModel):
    """Normalized simulation result — backend-independent.

    Metrics unavailable in a simulator must be None + reason,
    not silently zero.

    Formal definitions:
        Qualified goodput: G_F = N_delivered(F >= F_min) / T_obs
        Deadline-qualified goodput: G_{F,D} = N(F >= F_min, L <= D) / T_obs
        Raw throughput: R = N_delivered / T_obs
        Memory utilization: U = mean(occupied_slots / capacity)
        Blocking: B = N_blocked / N_requested
        Expiration: E = N_expired / N_generated
    """

    # Identification
    backend: str = Field(description="Backend name")
    backend_version: str | None = Field(default=None, description="Backend version")
    experiment_id: str = Field(description="Experiment ID")
    seed: int = Field(description="Random seed")

    # Timing
    simulation_time: float = Field(description="Simulated time (s)")
    wall_time: float = Field(description="Wall-clock time (s)")
    cpu_seconds: float | None = Field(default=None, description="CPU time (s)")
    peak_memory_mb: float | None = Field(default=None, description="Peak RAM (MB)")

    # Pair counts
    requested_pairs: int = Field(default=0, description="Total requested pairs")
    generated_pairs: int = Field(default=0, description="Elementary pairs generated")
    delivered_pairs: int = Field(default=0, description="End-to-end pairs delivered")
    qualified_pairs: int = Field(
        default=0, description="Pairs meeting fidelity threshold"
    )
    expired_pairs: int = Field(default=0, description="Pairs expired before delivery")
    blocked_requests: int = Field(default=0, description="Requests blocked")

    # Rates
    raw_rate: float | None = Field(default=None, description="Raw throughput (pairs/s)")
    goodput: float | None = Field(
        default=None, description="Qualified goodput G_F (pairs/s)"
    )

    # Latency
    latency: LatencyStats = Field(default_factory=LatencyStats)

    # Fidelity
    fidelity: FidelityStats = Field(default_factory=FidelityStats)

    # Generation / swapping
    generation_attempts: int = Field(default=0, description="Total generation attempts")
    swap_attempts: int = Field(default=0, description="Total swap attempts")
    swap_successes: int = Field(default=0, description="Successful swaps")
    purification_attempts: int = Field(default=0, description="Purification attempts")

    # Memory
    memory_occupancy_mean: float | None = Field(
        default=None, description="Mean memory occupancy (fraction)"
    )
    memory_occupancy_peak: float | None = Field(
        default=None, description="Peak memory occupancy (fraction)"
    )
    mean_pair_age: float | None = Field(default=None, description="Mean pair age (s)")

    # Routing
    route_length_mean: float | None = Field(
        default=None, description="Mean route length (hops)"
    )
    reroutes: int = Field(default=0, description="Number of reroutes")

    # Quality
    fairness: float | None = Field(default=None, description="Fairness index [0,1]")
    deadline_misses: int = Field(default=0, description="Deadline-missed pairs")

    # Events
    event_count: int | None = Field(default=None, description="Total events processed")

    # Translation
    translation_report: dict[str, str] = Field(
        default_factory=dict, description="Parameter translation statuses"
    )

    # Missing metric reasons
    missing_reasons: dict[str, str] = Field(
        default_factory=dict,
        description="Reasons for None metrics",
    )

    # Raw backend output (optional)
    raw_output: dict[str, Any] | None = Field(
        default=None, description="Raw backend-specific output"
    )

    def compute_derived(self, min_fidelity: float = 0.9) -> None:
        """Compute derived metrics from raw counts."""
        if self.simulation_time > 0:
            self.raw_rate = self.delivered_pairs / self.simulation_time
            self.goodput = self.qualified_pairs / self.simulation_time
