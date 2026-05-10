#!/usr/bin/env python3
"""
Scenario runner. Executes one or more attack scenarios and records outcomes.

Usage:
    python runner.py [scenario-id ...]
    python runner.py --all
"""

import argparse
import csv
import importlib.util
import os
import pathlib
import sys
import time

SCENARIOS_DIR = pathlib.Path(__file__).parent / "scenarios"
RESULTS_DIR = pathlib.Path("/results")


def load_scenario(path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_one(scenario_path: pathlib.Path, control_profile: str) -> dict:
    print(f"=== Running scenario {scenario_path.name} (controls: {control_profile}) ===")
    try:
        module = load_scenario(scenario_path)
        result = module.run()
    except Exception as e:
        result = {
            "scenario": scenario_path.stem,
            "stride_hc": getattr(module, "STRIDE_HC", "?"),
            "outcome": "ERROR",
            "detail": str(e),
        }
    result["control_profile"] = control_profile
    result["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    return result


def write_results(results: list, run_id: str):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"run-{run_id}.csv"
    fieldnames = ["timestamp", "scenario", "stride_hc", "control_profile", "outcome", "detail"]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in results:
            w.writerow(r)
    print(f"Results written to {out}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scenarios", nargs="*", help="Scenario file names (without path)")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--control-profile", default=os.environ.get("CONTROL_PROFILE", "baseline"))
    args = parser.parse_args()

    if args.all:
        paths = sorted(SCENARIOS_DIR.glob("*.py"))
    else:
        paths = [SCENARIOS_DIR / s for s in args.scenarios]
        for p in paths:
            if not p.exists():
                print(f"Scenario not found: {p}")
                sys.exit(1)

    if not paths:
        print("No scenarios specified. Use --all to run all.")
        sys.exit(1)

    results = []
    for path in paths:
        results.append(run_one(path, args.control_profile))

    run_id = time.strftime("%Y%m%d-%H%M%S")
    write_results(results, run_id)

    # Print summary
    print("\nSummary:")
    for r in results:
        print(f"  {r['scenario']:50s} {r['stride_hc']:4s} {r['outcome']}")


if __name__ == "__main__":
    main()
