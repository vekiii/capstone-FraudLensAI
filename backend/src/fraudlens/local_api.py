"""Launch the development API on IPv4 loopback only."""

from __future__ import annotations

import uvicorn


def main() -> None:
    """Run the local API without accepting a configurable public bind address."""
    uvicorn.run("fraudlens.main:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
