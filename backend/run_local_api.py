"""Repository-root launcher for the loopback-only development API."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))


def run() -> None:
    from fraudlens.local_api import main

    main()


if __name__ == "__main__":
    run()
