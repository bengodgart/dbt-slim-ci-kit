---
type: Playbook
title: Run dbt-slim-ci-kit locally
description: 'How to stand up the example project and run the Slim CI build the action runs.'
generated:
  by: claude-opus-5
  at: '2026-07-29T06:00:00+00:00'
status: stable
---

# Steps

Requires Python 3.13 or lower.

1. Clone the repo: `git clone https://github.com/bengodgart/dbt-slim-ci-kit.git`
2. `python -m venv .venv && . .venv/Scripts/activate` (or `.venv/bin/activate`)
3. `pip install dbt-duckdb==1.10.1`
4. `cd example`
5. `dbt build --target prod --profiles-dir .` stands up the demo prod.

Then change a model and run the build the action runs:

```
DBT_CI_PATH=ci.duckdb DBT_CI_SCHEMA=main_ci \
  dbt build --select state:modified+ --defer --state ci-state --target ci --profiles-dir .
```

## Available scripts

* `python scripts/test_format_comment.py` runs the PR-comment formatter smoke test against
  committed fixtures, no warehouse needed. Expected: `RESULT: all 14 passed`.

## Adopting it in another repo

Copy the workflow file, point `dbt-adapter` at your adapter, set your warehouse credentials
as GitHub secrets, and add a teardown command that drops the CI dataset.

## Common failures

* **Python 3.14 will not work.** dbt does not support it yet. Use 3.13 or lower.
* **Forgetting the teardown leaves CI schemas behind.** The kit builds into a throwaway
  staging schema; dropping it is the consuming repo's job, not the action's.
* Omitting `--defer` and `--state` rebuilds everything, which defeats the entire point of
  Slim CI.
