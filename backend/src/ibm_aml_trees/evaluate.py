"""Display measured metrics from a completed local run manifest."""

import argparse
import json
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True, help="run directory or run ID under artifacts/")
    args = parser.parse_args(argv)
    run_dir = Path(args.run)
    if not run_dir.is_dir():
        run_dir = Path("artifacts") / args.run
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    print(f"Run: {manifest['run_id']} | split_mode={manifest['split_mode']} | "
          f"train_frac={manifest['train_frac']}")
    print("variant\tseed\tF1\tprecision\trecall\tPR-AUC\tTP\tFP\tTN\tFN")
    for variant, result in manifest["variants"].items():
        for entry in result["per_seed"]:
            metrics = entry["test"]
            print(f"{variant}\t{entry['seed']}\t{metrics['f1']:.4f}\t"
                  f"{metrics['precision']:.4f}\t{metrics['recall']:.4f}\t"
                  f"{metrics['pr_auc']:.4f}\t{metrics['tp']}\t{metrics['fp']}\t"
                  f"{metrics['tn']}\t{metrics['fn']}")
            if "delayed_alerts_not_real_time" in entry:
                delayed = entry["delayed_alerts_not_real_time"]["test"]
                print(f"delayed alerts, not real-time\t{entry['seed']}\t"
                      f"{delayed['f1']:.4f}\t{delayed['precision']:.4f}\t"
                      f"{delayed['recall']:.4f}\tn/a\t"
                      f"{delayed['tp']}\t{delayed['fp']}\t{delayed['tn']}\t{delayed['fn']}")
        print(f"{variant} mean: {json.dumps(result['mean'], sort_keys=True)}")
        delayed_rows = [entry["delayed_alerts_not_real_time"]["test"]
                        for entry in result["per_seed"]
                        if "delayed_alerts_not_real_time" in entry]
        if delayed_rows:
            mean = {name: sum(row[name] for row in delayed_rows) / len(delayed_rows)
                    for name in ("f1", "precision", "recall")}
            print(f"delayed alerts, not real-time mean: {json.dumps(mean, sort_keys=True)}")


if __name__ == "__main__":
    main()
