# devcoffee-schema

Avro schemas (source of truth) for DevCoffee integration events, plus the Java and Python packages built from them.

| Path | Content |
|---|---|
| `schema/<domain>/<event>.avsc` | Avro schemas, e.g. `schema/user/user.created.avsc` |
| `builder/jav` | Maven project → `tech.devcoffee:devcoffee-event-schema` (classes generated from `schema/`) |
| `builder/pyt` | uv project → `devcoffee-integration-event` (hand-written Pydantic models) |
| `sync.ps1`, `sync.cmd`, `tools/sync.exe` | Register schemas in the Schema Registry |

## Workflow when changing a schema

1. Add or edit the `.avsc` under `schema/`. Keep changes backward compatible (new optional fields with defaults).
2. Bump the Java version in `builder/jav/pom.xml` and build it (see [Java package](#java-package)).
3. Update the Pydantic models in `builder/pyt/src/tech/devcoffee/integration/events/` by hand, bump `version` in `builder/pyt/pyproject.toml`, and build it (see [Python package](#python-package)).
4. Register the schemas in the Schema Registry (see [Schema Registry sync](#schema-registry-sync)).
5. Publish the packages and update consumers to the new version.

`sync` does **not** generate code or build packages; steps 2–4 are separate.

## Java package

Requires JDK 21+.

```bash
cd builder/jav
./mvnw clean install
```

- `avro-maven-plugin` generates classes from `../../schema` into `target/generated-sources/avro` (`stringType=String`).
- The JAR is written to `target/devcoffee-event-schema-<version>.jar` and installed into `~/.m2`, so local services can use it immediately.

Publish to GitHub Packages (`distributionManagement` id `devcoffee-github`):

```bash
cd builder/jav
./mvnw clean deploy
```

This needs a `<server>` with id `devcoffee-github` in `~/.m2/settings.xml`, holding a GitHub username and a token with `write:packages`.

## Python package

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/). Build backend: `uv_build`.

```bash
cd builder/pyt
uv sync    # create .venv from uv.lock
uv build   # write wheel + sdist to dist/
```

Output: `dist/devcoffee_integration_event-<version>-py3-none-any.whl` and `.tar.gz`. Import path: `tech.devcoffee.integration.events`.

The models are **not** generated from `.avsc`; keep them in line with the schemas manually.

## Schema Registry sync

Windows only (`tools/sync.exe`).

1. Create `.env` in the repository root (git-ignored) from `.env.example`:

   ```dotenv
   SCHEMA_REGISTRY_URL=http://localhost:8081
   TRUST_CERT_PATH=./.config/rootCA/devcoffee.ca.crt
   SCHEMA_DIR=./schema
   ```

   | Variable | Default | Meaning |
   |---|---|---|
   | `SCHEMA_REGISTRY_URL` | — | Registry base URL |
   | `SCHEMA_DIR` | `schema` | Directory scanned recursively for `*.avsc` (relative to repo root) |
   | `TRUST_CERT_PATH` | — | CA certificate used to verify HTTPS, if the file exists |
   | `HTTP_TIMEOUT` | `10` | Request timeout in seconds |
   | `SUBJECT_NAME_STRATEGY` | `RecordNameStrategy` | `RecordNameStrategy` → subject `<namespace>.<name>`; `TopicNameStrategy` → `<file-stem>-value` |

2. Run from the repository root:

   ```powershell
   ./sync.ps1
   ```

   or `sync.cmd` from CMD. Both set `BASE_DIR` to the repository root and run `tools/sync.exe`.

3. For every `*.avsc` the tool sends `POST {SCHEMA_REGISTRY_URL}/subjects/{subject}/versions`. It exits with code 1 if any schema is rejected, for example when it is incompatible with the subject's compatibility setting.

Use `RecordNameStrategy`: services serialize with `value.subject.name.strategy=RecordNameStrategy` and `auto.register.schemas=false`, so an event cannot be published until its schema is registered.

The source of `sync.exe` is the `tools/schema-sync` project in the DevCoffee workspace (built with PyInstaller).
