# Project Overview

This repository, `devcoffee-schemas`, serves as the central source of truth for Apache Avro schemas used in integration events across the DevCoffee ecosystem. It facilitates a schema-first development approach, ensuring data consistency between services written in different languages.

The core schemas are located in the `schema/` directory and are categorized by domain (e.g., `token`, `user`). They are consumed in three ways:

- **Java:** `builder/jav` generates Avro `SpecificRecord` classes from `schema/` at build time (`avro-maven-plugin`) and packages them as `tech.devcoffee:devcoffee-event-schema`.
- **Python:** `builder/pyt` contains **hand-written** Pydantic models (`src/tech/devcoffee/integration/events/`) packaged as `devcoffee-integration-event`. They are NOT generated from the schemas — update them manually to match every schema change.
- **Schema Registry:** `sync.ps1` / `sync.cmd` registers the `.avsc` files in the Confluent Schema Registry.

See `README.md` for the full build, sync, and release steps.

---

## Building and Running

### Java Module (`builder/jav`)

**Prerequisites:** JDK 21 or higher.

```bash
cd builder/jav
./mvnw clean install
```

This generates Java classes from `../../schema` into `target/generated-sources/avro`, packages the JAR into `target/`, and installs it into the local Maven repository (`~/.m2`).

### Python Module (`builder/pyt`)

**Prerequisites:** Python 3.12 or higher, [uv](https://docs.astral.sh/uv/). The build backend is `uv_build`.

```bash
cd builder/pyt
uv sync    # create .venv from uv.lock
uv build   # build wheel + sdist into dist/
```

### Schema Registry sync

```powershell
./sync.ps1   # PowerShell
sync.cmd     # CMD
```

This only runs `tools/sync.exe`, which:

1. Reads `.env` from the repository root (`SCHEMA_REGISTRY_URL`, `SCHEMA_DIR`, `TRUST_CERT_PATH`, optional `HTTP_TIMEOUT` and `SUBJECT_NAME_STRATEGY`).
2. Collects every `*.avsc` under `SCHEMA_DIR`.
3. POSTs each schema to `{SCHEMA_REGISTRY_URL}/subjects/{subject}/versions` (subject from `RecordNameStrategy` by default: `<namespace>.<name>`).

It does **not** generate code or build the Java/Python packages. Its source lives in the workspace at `tools/schema-sync`.

---

## Development Conventions

- **Schema-First:** All data model changes must start with a modification to an Avro schema in the `schema/` directory. Never edit generated Java sources in `builder/jav/target/`.
- **Keep Python in sync manually:** After a schema change, update the matching Pydantic models in `builder/pyt` by hand.
- **Versioning:** Bump `builder/jav/pom.xml` and `builder/pyt/pyproject.toml` versions when schemas change.
- **Registry:** Producers such as `devcoffee-authorization-server` use `auto.register.schemas=false` and `use.latest.version=true`, so run `sync` to register new or changed schemas before they publish them.
- **Formatting:** The project uses `.prettierrc` and `.editorconfig` to maintain a consistent code style. Ensure your editor is configured to use these files.
