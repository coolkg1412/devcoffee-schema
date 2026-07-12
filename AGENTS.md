# devcoffee-schemas — Agent Guide

Central SSOT for Apache Avro schemas used in integration events across the DevCoffee
ecosystem. Schema-first: language-specific models (Java POJOs, Python Pydantic) are
GENERATED from `schema/` — never hand-edit generated output.

## Rules

1. Workspace contract first: root `../AGENTS.md` (Docs Gate, approval rules, truth
   order) applies to all work in this repo. This repo is not GitNexus-indexed, so the
   GitNexus-first rule does not apply here.
2. Repo guides: `./README.md` and `./GEMINI.md` (project overview, build commands).
   Build everything with `./sync.ps1` (or `./sync.cmd`); manual per-language builds
   are documented in `GEMINI.md`.
3. Every schema change is a cross-service contract change. Identify all consumers
   (`devcoffee-product`, `devcoffee-webhook-gateway`, Java services) before editing;
   breaking changes require a documented migration plan for every consumer.
4. Prefer backward-compatible schema evolution (add optional fields with defaults);
   never rename or remove a published field without a coordinated migration.
5. Schemas live under `schema/` grouped by domain; follow the existing domain layout
   when adding new event schemas.
