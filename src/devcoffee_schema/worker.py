import json
import logging
import sys
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

HEADERS = {"Content-Type": "application/vnd.schemaregistry.v1+json"}

logger = logging.getLogger(__name__)


class SyncWorker:
    def __init__(
        self,
        schema_dir: Path,
        registry_url: str,
        request_kwarg: dict[str, str] | None = None,
        max_workers: int = 8,
    ) -> None:
        self.schema_dir = schema_dir
        self.registry_url = registry_url
        self.request_kwarg = request_kwarg or {}
        self.max_workers = max_workers

    def run(self) -> None:
        files = list(self._collect_files())

        logger.info("schema_dir=%s", self.schema_dir)

        if not files:
            logger.warning("No schema files found")
            return

        logger.info(f"Sync {len(files)} schemas to '{self.registry_url}'")

        errors: list[Exception] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = [pool.submit(self._register_file, f) for f in files]

            for future in as_completed(futures):
                try:
                    subject, schema_id = future.result()
                    logger.info(f"Success: '{subject}' -> id '{schema_id}'")
                except Exception as e:
                    logger.error("Failed: error='{e}", exc_info=e)
                    errors.append(e)

        if errors:
            logger.error(f"Failed: {len(errors)} schema(s)")
            sys.exit(1)

        logger.info("Done")

    def _collect_files(self) -> Iterable[Path]:
        return sorted(self.schema_dir.rglob("*.avsc"))

    def _build_subject(self, file: Path) -> str:
        sub = file.stem.lower()

        if not sub.endswith("-value"):
            sub = f"{sub}-value"

        return sub

    def _register_file(self, file: Path) -> tuple[str, int]:
        subject = self._build_subject(file)

        with file.open() as f:
            schema = json.load(f)

        payload = {"schema": json.dumps(schema)}

        endpoint = f"{self.registry_url}/subjects/{subject}/versions"
        logger.debug(f"subject: '{subject}' - endpoint='{endpoint}' - payload='{payload}'")

        resp = requests.post(
            endpoint,
            headers=HEADERS,
            json=payload,
            **self.request_kwarg,
        )

        if resp.status_code >= 300:
            raise RuntimeError(f"{subject} -> {resp.text}")

        results = resp.json()

        logger.debug(f"response={results}")

        return subject, 1
