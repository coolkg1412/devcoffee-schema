#!/usr/bin/env python
"""Schema Sync's command-line utility for administrative tasks."""

import os
from pathlib import Path

base_url = Path(__file__).resolve().parent
os.environ.setdefault("BASE_DIR", str(base_url))


def calculate_workers() -> int:
    cpu = os.cpu_count()

    if not cpu:
        return 2

    return max(1, cpu // 2)


def main():
    """Run administrative tasks."""
    from devcoffee_schema import SyncWorker, settings, setup_logging

    setup_logging(log_file=Path.joinpath(base_url, "./logs/sync.log"))

    worker = SyncWorker(
        settings.schema_dir,
        registry_url=settings.from_env,
        request_kwarg={"timeout": settings.timeout},
        max_workers=calculate_workers(),
    )
    worker.run()


if __name__ == "__main__":
    main()
