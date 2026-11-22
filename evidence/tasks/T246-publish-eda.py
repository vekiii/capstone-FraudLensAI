"""Explicit T246 full-source EDA publisher for the exact local T210 snapshot.

Run from the repository root only when a full-source pass is authorized. The
publisher verifies the exact T210 snapshot and strips each label token from
bytes before parsing canonical non-label facts. Output stays Git-ignored.
"""

import resource
import sys
import time
from pathlib import Path

from fraudlens.eda.publisher import T210_EXPECTED, publish_eda_summary

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / 'data/processed/t210-hi-small-b19d39f5'
OUTPUT = ROOT / 'data/processed/t246-hi-small-eda-summary-v1.json'
MAX_PEAK_RSS_BYTES = 4 * 1024**3


def progress(seen: int) -> None:
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    peak_bytes = peak if sys.platform == 'darwin' else peak * 1024
    print(f'EDA accepted rows: {seen:,}/{T210_EXPECTED.source_count:,}; '
          f'peak RSS: {peak_bytes:,} bytes', flush=True)
    if peak_bytes > MAX_PEAK_RSS_BYTES:
        raise MemoryError('EDA memory ceiling exceeded; no summary published')


def main() -> None:
    started = time.monotonic()
    print(f'Verifying pinned T210 snapshot before label-free aggregation; '
          f'RSS ceiling: {MAX_PEAK_RSS_BYTES:,} bytes', flush=True)
    digest = publish_eda_summary(SNAPSHOT, T210_EXPECTED, OUTPUT,
                                 on_progress=progress)
    print(f'EDA summary SHA-256: {digest}')
    print(f'Output: {OUTPUT.relative_to(ROOT)}')
    print(f'Elapsed seconds: {time.monotonic() - started:.3f}')


if __name__ == '__main__':
    main()
