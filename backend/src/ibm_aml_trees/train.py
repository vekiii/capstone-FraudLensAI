"""CLI: python -m ibm_aml_trees.train --data CSV --out artifacts/."""

import argparse
import json
import time

from .experiment import run_experiment


def main(argv=None):
    parser = argparse.ArgumentParser(description="Exploratory IBM AML notebook reproduction")
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", default="artifacts")
    parser.add_argument("--train-frac", type=float, default=1.0)
    parser.add_argument("--split", choices=("temporal", "stratified"), default="temporal")
    parser.add_argument("--retro", action="store_true", help="evaluate delayed alerts separately")
    parser.add_argument("--bootstrap", type=int, default=1000)
    args = parser.parse_args(argv)
    started = time.perf_counter()
    run_dir, manifest = run_experiment(
        args.data, args.out, args.train_frac, args.split, args.retro, args.bootstrap
    )
    print(json.dumps({
        "run_dir": str(run_dir), "split_mode": args.split, "train_frac": args.train_frac,
        "mean": {name: value["mean"] for name, value in manifest["variants"].items()},
        "stage_seconds": manifest["stage_seconds"],
        "total_wall_seconds": time.perf_counter() - started,
    }, indent=2))


if __name__ == "__main__":
    main()
