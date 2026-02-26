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

    request_kwarg = {"timeout": settings.timeout}
    if settings.trust_cert_path and settings.trust_cert_path.exists():
        request_kwarg["verify"] = str(settings.trust_cert_path)

    worker = SyncWorker(
        settings.schema_dir,
        registry_url=settings.registry_url,
        subject_name_strategy=settings.subject_name_strategy,
        request_kwarg=request_kwarg,
        max_workers=calculate_workers(),
    )
    worker.run()


if __name__ == "__main__":
    main()
