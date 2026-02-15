import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

# load .env if exists
load_dotenv()

REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")
SCHEMA_DIR = Path(os.getenv("SCHEMA_DIR", "./schemas"))


def register_schema(subject: str, schema: dict) -> int:
    payload = {"schema": json.dumps(schema)}

    resp = requests.post(
        f"{REGISTRY_URL}/subjects/{subject}/versions",
        headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
        json=payload,
        timeout=10,
    )

    if resp.status_code >= 300:
        print(f"❌ Failed: {subject}")
        print(resp.text)
        sys.exit(1)

    return resp.json()["id"]


def main() -> None:
    if not SCHEMA_DIR.exists():
        print(f"❌ Schema dir not found: {SCHEMA_DIR}")
        sys.exit(1)

    files = list(SCHEMA_DIR.glob("*.avsc"))

    if not files:
        print("⚠️ No schema files found")
        return

    print(f"🚀 Sync {len(files)} schemas to {REGISTRY_URL}")

    for file in files:
        subject = f"{file.stem}-value"

        with file.open() as f:
            schema = json.load(f)

        schema_id = register_schema(subject, schema)
        print(f"✅ {subject} -> id {schema_id}")

    print("🎉 Done")


if __name__ == "__main__":
    print(SCHEMA_DIR)
    # main()
