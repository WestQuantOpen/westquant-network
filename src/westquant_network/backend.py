"""Backend dispatcher — route experiments to the correct adapter."""

from __future__ import annotations

from westquant_network.ir import ExperimentSpec
from westquant_network.metrics import SimulationResult
from westquant_network.policies import PolicySet
from westquant_network.reference import simulate as reference_simulate


def simulate(
    experiment: ExperimentSpec,
    policies: PolicySet | None = None,
    backend: str | None = None,
) -> SimulationResult:
    """Run an experiment on the specified backend.

    Args:
        experiment: WestQuant experiment specification.
        policies: Policy set (optional).
        backend: Backend name override. If None, uses experiment.backend.

    Returns:
        Normalized SimulationResult.
    """
    backend_name = backend or experiment.backend

    if backend_name == "reference":
        return reference_simulate(experiment, policies)

    elif backend_name == "simqn":
        from westquant_network.adapters.simqn import SimQNAdapter
        simqn_adapter = SimQNAdapter()
        return simqn_adapter.simulate(experiment, policies)

    elif backend_name == "sequence":
        from westquant_network.adapters.sequence import SequenceAdapter
        seq_adapter = SequenceAdapter()
        return seq_adapter.simulate(experiment, policies)

    elif backend_name == "netsquid":
        try:
            from westquant_network.adapters.netsquid import NetSquidAdapter
            adapter = NetSquidAdapter()
            return adapter.simulate(experiment, policies)
        except ImportError:
            return SimulationResult(
                backend="netsquid",
                experiment_id=experiment.experiment_id,
                seed=experiment.seed,
                simulation_time=experiment.duration,
                wall_time=0.0,
                missing_reasons={
                    "netsquid": "NetSquid not installed. Register at https://forum.netsquid.org",
                },
            )

    elif backend_name == "qoala":
        try:
            from westquant_network.adapters.qoala import QoalaAdapter
            adapter = QoalaAdapter()
            return adapter.simulate(experiment, policies)
        except ImportError:
            return SimulationResult(
                backend="qoala",
                experiment_id=experiment.experiment_id,
                seed=experiment.seed,
                simulation_time=experiment.duration,
                wall_time=0.0,
                missing_reasons={
                    "qoala": "Qoala not installed. Requires NetSquid registration.",
                },
            )

    else:
        raise ValueError(f"Unknown backend: {backend_name}")


def compare(
    experiment: ExperimentSpec,
    backends: list[str],
    policies: PolicySet | None = None,
) -> dict[str, SimulationResult]:
    """Run experiment on multiple backends and return results.

    Args:
        experiment: WestQuant experiment specification.
        backends: List of backend names.
        policies: Policy set (optional).

    Returns:
        Dict mapping backend name to SimulationResult.
    """
    results = {}
    for backend in backends:
        exp_copy = experiment.model_copy()
        exp_copy.backend = backend
        try:
            results[backend] = simulate(exp_copy, policies, backend)
        except Exception as e:
            results[backend] = SimulationResult(
                backend=backend,
                experiment_id=experiment.experiment_id,
                seed=experiment.seed,
                simulation_time=experiment.duration,
                wall_time=0.0,
                missing_reasons={backend: str(e)},
            )
    return results
