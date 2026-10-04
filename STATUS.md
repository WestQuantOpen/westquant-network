# WestQuant Network — Living Status

**Last updated:** 2026-10-04
**Current phase:** Phase A — Simulator Audit

---

## Completed

- [x] Program specification documented (`docs/PROGRAM_SPEC.md`)
- [x] Repository structure created
- [x] Package skeleton (`westquant-network` 0.1.0a1)
- [x] WQIR Network contracts: `Topology`, `Node`, `QuantumMemory`, `QuantumLink`, `ClassicalLink`, `RepeaterSpec`, `Request`, `Experiment`
- [x] Policies module: `RoutingPolicy`, `MemoryPolicy`, `SwapPolicy`, `PurificationPolicy`, `AdmissionPolicy`
- [x] Metrics module: `SimulationResult`, formal metric definitions
- [x] Translation report: `TranslationReport`, `TranslationStatus` enum
- [x] Capability discovery: `BackendCapabilities`, `CapabilityLevel`
- [x] Reference simulator: discrete-event, line/star/mesh topology, memory decay, entanglement generation, swapping, routing
- [x] CLI: `westquant-network run`, `westquant-network compare`

## Current work

- Phase A: Simulator Audit — SeQUeNCe and SimQN installed, NetSquid/Qoala pending registration

## Findings

### Simulator installation status

| Simulator | PyPI name | Version | Status | License |
|-----------|-----------|---------|--------|---------|
| SeQUeNCe | `sequence` | 0.8.0 | ✅ Installed | BSD-3 |
| SimQN | `qns` | 0.2.3 | ✅ Installed | GPLv3 |
| NetSquid | `netsquid` | — | ⚠️ Requires registration | Proprietary (free for non-commercial) |
| Qoala | `qoala` | 1.0.0 | ⚠️ Requires NetSquid | MIT (but depends on NetSquid) |

### Installation details

- **SeQUeNCe**: `pip install sequence` — installs from PyPI, includes QuTiP, Dash, JupyterLab. BSD-3 license, CI-friendly.
- **SimQN**: `pip install qns` — installs from PyPI, lightweight (numpy + pandas). GPLv3 license, CI-friendly.
- **NetSquid**: Requires forum registration at https://forum.netsquid.org. Install with `pip install netsquid --extra-index-url=https://pypi.netsquid.org`. Proprietary license, NOT CI-friendly without credentials.
- **Qoala**: Available on PyPI but depends on NetSquid. Install with `pip install qoala --extra-index-url=https://pypi.netsquid.org`. MIT license, but transitively constrained by NetSquid.

### Key architecture observations

- SeQUeNCe uses a custom discrete-event kernel with hardware/entanglement/resource/network/application layers
- SimQN is network-layer focused with heap-based event scheduling and Dijkstra routing
- NetSquid is physics-focused with time-dependent decoherence and multiple state formalisms
- Qoala adds software/hardware execution scheduling on top of NetSquid

## Unexpected differences

- (pending audit)

## Scientific risks

- NetSquid requires registration on private package registry — cannot be a hard dependency
- Qoala builds on NetSquid — same constraint applies transitively
- SimQN and SeQUeNCe are open-source and PyPI-installable

## Engineering risks

- NetSquid licence may restrict CI distribution
- Qoala depends on NetSquid internals — adapter may be fragile
- SeQUeNCe uses a custom discrete-event kernel — hook depth unknown

## Blocked items

- NetSquid installation pending registration/account
- Qoala installation pending NetSquid

## Next experiments

- Install SeQUeNCe and SimQN (open-source)
- Run hello-world on each
- Begin capability matrix
