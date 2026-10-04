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

- Phase A: Simulator Audit — installing and inspecting SeQUeNCe, NetSquid, SimQN, Qoala

## Findings

- (pending audit)

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
