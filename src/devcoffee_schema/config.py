import os
from dataclasses import dataclass
from pathlib import Path

import environ

BASE_DIR = Path(os.getenv("BASE_DIR", str(Path(__file__).resolve().parent)))

env = environ.Env()
env.read_env(Path.joinpath(BASE_DIR, ".env"))


@dataclass(slots=True)
class Settings:
    registry_url: str
    schema_dir: Path
    timeout: int = 10

    @classmethod
    def from_env(cls) -> "Settings":
        registry_url = env.str("SCHEMA_REGISTRY_URL", "")

        schema_dir = Path(env.str("SCHEMA_DIR", "schema"))
        if not schema_dir.is_absolute():
            schema_dir = Path.joinpath(BASE_DIR, schema_dir)

        timeout = env.int("HTTP_TIMEOUT", 10)

        return cls(
            registry_url=registry_url,
            schema_dir=schema_dir,
            timeout=timeout,
        )


settings = Settings.from_env()
