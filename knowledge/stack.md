---
type: Tech Stack
title: dbt-slim-ci-kit stack
description: 'Frameworks, storage and services dbt-slim-ci-kit runs on.'
runtime: 'Python 3.13 or lower'
framework: dbt
database: 'DuckDB in the example. Swap the adapter for a real warehouse.'
ci: 'GitHub Actions, via action.yml'
build: 'dbt build with state:modified+ and --defer'
tests: 'python scripts/test_format_comment.py, 19 checks'
generated:
  by: claude-opus-5
  at: '2026-07-29T04:24:12+00:00'
status: stable
---

# Stack

* **Runtime**: Python **3.13 or lower**. dbt does not yet run on 3.14.
* **Transformations**: dbt Core. The bundled example uses `dbt-duckdb==1.10.1` so it runs
  locally with no warehouse; point `dbt-adapter` at `dbt-bigquery` or another adapter for
  real use.
* **CI**: GitHub Actions. `action.yml` at the repo root is the composite action a consuming
  repo references.
* **Selection**: `state:modified+` with `--defer`, so only models changed in the pull
  request and their descendants are built. Everything unchanged is deferred to prod.
* **Scripts**: `scripts/` holds the run-results formatter that writes the PR comment.
* **Example**: `example/` is a complete small dbt project the kit runs against itself.
* **Tests**: `python scripts/test_format_comment.py`, 19 checks against committed
  `run_results.json` fixtures, no warehouse needed.

## What is deliberately not here

Not a full dbt project, not dbt Cloud, not a scheduled production runner, not a
multi-warehouse abstraction. It gives dbt Core a free Slim CI check on pull requests and
nothing else.
