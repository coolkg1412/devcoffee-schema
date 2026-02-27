# Project Overview

This repository, `devcoffee-schemas`, serves as the central source of truth for Apache Avro schemas used in integration events across the DevCoffee ecosystem. It facilitates a schema-first development approach, ensuring data consistency between services written in different languages.

The repository is structured to automatically generate language-specific data models from the base Avro schemas:
- **Java:** Generates Plain Old Java Objects (POJOs) for use in Java-based services.
- **Python:** Generates Pydantic models for data validation and serialization in Python-based services.

The core schemas are located in the `schema/` directory and are categorized by domain (e.g., `token`, `user`).

---

## Building and Running

A master synchronization script orchestrates the build process for all target languages.

**To build everything:**
```bash
# Powershell
./sync.ps1

# CMD
./sync.cmd
```
This command executes `tools/sync.exe`, which will:
1.  Generate Java classes from the Avro schemas.
2.  Build the Java project into a JAR file.
3.  Generate Python Pydantic models from the Avro schemas.
4.  Build the Python project into a distributable wheel.

---

### Manual Builds

You can also build the language-specific modules individually.

#### Java Module

The Java project is managed with Maven.

**Prerequisites:**
- JDK 21 or higher

**To build:**
Navigate to the `builder/jav` directory and run:
```bash
./mvnw clean install
```
This command cleans the project, generates Java classes from the `.avsc` files into the `target/generated-sources/avro` directory, and packages the project into a JAR file in the `target/` directory.

#### Python Module

The Python project is managed with [PDM](https://pdm-project.org/).

**Prerequisites:**
- Python 3.12 or higher
- PDM installed

**To install dependencies and build:**
Navigate to the `builder/pyt` directory and run:
```bash
# Install dependencies
pdm install

# Build the distributable wheel
pdm build
```
The resulting wheel file will be located in the `dist/` directory.

---

## Development Conventions

- **Schema-First:** All data model changes must start with a modification to an Avro schema in the `schema/` directory. Direct modifications to the generated source code in the `builder/` sub-projects will be overwritten.
- **Synchronization:** After modifying a schema, run the main `sync` script to propagate the changes to all language-specific modules.
- **Formatting:** The project uses `.prettierrc` and `.editorconfig` to maintain a consistent code style. Ensure your editor is configured to use these files.
