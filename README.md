# WestQuant Network

**Simulator-independent experimentation, optimization, and AI layer for quantum networks.**

WestQuant Network is an open framework for quantum-network modelling, simulation, benchmarking, representation search, and AI-driven optimization. It sits on top of existing quantum-network simulators — SeQUeNCe, NetSquid, SimQN, and Qoala — providing a common experiment specification, normalized metrics, cross-simulator validation, and an optimization/AI interface.

## Installation

```bash
pip install westquant-network
```

With simulator backends (installed separately):

```bash
pip install westquant-network[sequence,simqn]
# NetSquid and Qoala require registration — see their docs
```

## Quick start

```python
from westquant.network import Experiment

exp = Experiment.from_yaml("experiment.yaml")
results = exp.compare(backends=["reference", "sequence", "simqn"])
```

```bash
westquant-network run experiment.yaml
westquant-network compare experiment.yaml --backends reference,sequence,simqn
```

## Architecture

```
westquant-network
├── ir          — WQIR Network representation
├── policies    — routing, memory, swapping, purification, admission
├── metrics     — normalized SimulationResult
├── trace       — common trace format
├── datasets    — AI dataset export
├── benchmark   — golden experiments
├── validation  — cross-simulator invariance
├── reference   — WestQuant reference discrete-event simulator
└── adapters
    ├── sequence
    ├── netsquid
    ├── simqn
    └── qoala
```

## Status

Phase A — Simulator Audit. See [STATUS.md](STATUS.md) and [docs/PROGRAM_SPEC.md](docs/PROGRAM_SPEC.md).

## License

Apache-2.0
