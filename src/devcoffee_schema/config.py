import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(slots=True)
class Settings:
    registry_url: str
    schema_dir: Path
    timeout: int = 10

    @classmethod
    def from_env(cls) -> "Settings":
        registry_url = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")
        schema_dir = Path(os.getenv("SCHEMA_DIR", "./schemas"))
        timeout = int(os.getenv("HTTP_TIMEOUT", "10"))

        return cls(
            registry_url=registry_url,
            schema_dir=schema_dir,
            timeout=timeout,
        )


settings = Settings.from_env()
