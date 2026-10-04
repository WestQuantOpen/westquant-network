"""WestQuant Network CLI."""

from __future__ import annotations

import argparse
import json
import sys

import yaml

from westquant_network.backend import compare, simulate
from westquant_network.ir import ExperimentSpec


def _experiment_from_yaml(path: str) -> ExperimentSpec:
    """Load experiment from YAML file."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return ExperimentSpec(**data)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="westquant-network",
        description="WestQuant Network — simulator-independent quantum network framework",
    )
    subparsers = parser.add_subparsers(dest="command")

    # Run
    run_parser = subparsers.add_parser("run", help="Run an experiment")
    run_parser.add_argument("experiment", help="Path to experiment YAML")
    run_parser.add_argument(
        "--backend", default="reference", help="Backend to use"
    )
    run_parser.add_argument("--output", "-o", default=None, help="Output JSON path")

    # Compare
    compare_parser = subparsers.add_parser("compare", help="Compare backends")
    compare_parser.add_argument("experiment", help="Path to experiment YAML")
    compare_parser.add_argument(
        "--backends", default="reference", help="Comma-separated backend list"
    )
    compare_parser.add_argument("--output", "-o", default=None, help="Output JSON path")

    # Benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Run golden benchmarks")
    bench_parser.add_argument("--output", "-o", default=None, help="Output JSON path")

    args = parser.parse_args()

    if args.command == "run":
        exp = _experiment_from_yaml(args.experiment)
        exp.backend = args.backend
        result = simulate(exp)
        output = result.model_dump_json(indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
        print(output)

    elif args.command == "compare":
        exp = _experiment_from_yaml(args.experiment)
        backends = args.backends.split(",")
        results = compare(exp, [b.strip() for b in backends])
        output = json.dumps(
            {k: v.model_dump() for k, v in results.items()},
            indent=2, default=str,
        )
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
        print(output)

    elif args.command == "benchmark":
        from westquant_network.benchmark import run_all_benchmarks

        results = run_all_benchmarks()
        output = json.dumps(results, indent=2, default=str)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
        print(output)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
