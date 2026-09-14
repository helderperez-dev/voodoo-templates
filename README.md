# Voodoo Templates

This repository intentionally contains a single supported scaffold: `default/`.

The default scaffold is the canary for the current public Voodoo experience. It should stay small, stable, and aligned with the recommended Store-first runtime path.

## Policy

- `default/` uses only stable, recommended Voodoo APIs.
- Fresh scaffolds resolve the latest published `voodoo-framework` release; the generated project's lockfile owns reproducibility after creation.
- Voodoo Store is the default durable application infrastructure (`.voodoo/application.vstore`).
- SQLite/PostgreSQL/Redis/S3 remain explicit adapters, not scaffold defaults.
- Specialized templates (agents, MCP, Edge, showcases, etc.) are intentionally deferred until their public APIs are stable enough to support as long-lived scaffolds.

A Voodoo release should not be considered healthy if a fresh `default/` project cannot install, start, create its Runtime Store, stop, and restart successfully.
