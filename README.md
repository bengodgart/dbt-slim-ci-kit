# dbt Slim CI Kit

Free "Slim CI" for dbt Core. On every pull request it builds and tests **only the models you changed and their descendants**, in a throwaway staging schema, then comments the result on the PR and blocks the merge if anything fails. This is the feature dbt Cloud charges for, packaged so a dbt Core team can adopt it by copying one workflow file.

The repo runs the kit on itself. See the green run on `main` in the [Actions tab](../../actions), and the two example pull requests: one that changes a model and passes, one that breaks a test and is blocked.

## What a run looks like

When a pull request changes `stg_orders`, the kit builds that model plus the three models downstream of it, runs their tests, and leaves the comment below. The unchanged models are deferred to prod, not rebuilt. This is the formatter output verbatim, with the passing test rows trimmed for length (the live comment lists every one):

```
## dbt Slim CI: SUCCESS

Built **4** models, ran **13** tests (13 passed, 0 failed) in **0.5s**.

Selection: `state:modified+`. Only models changed in this pull request and their descendants were built; every unchanged model was deferred to prod.

| Result | Type | Name | Time |
| --- | --- | --- | --- |
| PASS | model | `customers` | 0.05s |
| PASS | model | `order_stats` | 0.02s |
| PASS | model | `orders` | 0.05s |
| PASS | model | `stg_orders` | 0.07s |
| PASS | test | `not_null_stg_orders_order_id` | 0.07s |
| ... | test | (12 more tests) | ... |
```

When a change breaks a test, the same run reports `FAILURE`, names the failing test, and the job exits non-zero so the merge is blocked:

```
## dbt Slim CI: FAILURE

Built **1** models, ran **5** tests (4 passed, 1 failed) in **0.3s**.

| Result | Type | Name | Time |
| --- | --- | --- | --- |
| FAIL | test | `accepted_values_stg_orders_status__placed__shipped__completed__returned` | 0.06s |
| PASS | model | `stg_orders` | 0.07s |
| PASS | test | `not_null_stg_orders_order_id` | 0.06s |
```

## Why this exists

dbt Cloud's Slim CI builds only the modified assets in a PR and their downstream dependencies, in a staging schema, and posts the status to your git provider. That is a paid feature. dbt Core users rebuild it by hand every time, which is a weekend of GitHub Actions YAML and defer flags. There was no free packaged version, only a pile of blog walkthroughs.

This kit is that packaged version. The technique is exactly the one the dbt docs describe: compare the PR against a committed production manifest with `state:modified+`, build the selected slice into a staging schema, and `--defer` every unchanged reference to prod.

## Adopt it in your project

1. Add a CI workflow that calls the action:

   ```yaml
   # .github/workflows/dbt-ci.yml
   name: dbt Slim CI
   on:
     pull_request:
       branches: [main]
   permissions:
     contents: read
     pull-requests: write
   jobs:
     slim-ci:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: bengodgart/dbt-slim-ci-kit@v1
           with:
             project-dir: .
             dbt-adapter: dbt-bigquery   # your adapter
             target: ci                  # a target that points at a staging schema
   ```

2. Commit your production `manifest.json` to `ci-state/manifest.json` (this is the artifact your production run already produces). The action defers against it.

3. Open a pull request. You get a comment, and a red check on any failure.

That is the whole adoption path: one `uses:` line, one committed manifest, one staging target.

## How it works

- **`state:modified+`** selects the nodes that changed versus the committed prod manifest, plus everything downstream (`+`). Unchanged models are never rebuilt.
- **`--defer --state ci-state`** points every unbuilt reference at the production relations recorded in the manifest, so a changed model can still join to unchanged upstream tables without rebuilding them.
- **A staging schema** (the `ci` target) isolates the PR's build from prod. Nothing the PR builds touches production data.
- **Teardown** drops the staging schema after the run, so CI leaves nothing behind.
- **The exit code gates the merge.** Any failed model or test makes the job exit non-zero, which fails the required check.

Note on forks: a pull request opened from a fork gets a read-only token, so the comment cannot be posted. The kit does not treat that as a failure, so the build check still runs and gates the merge; only the comment is skipped on fork PRs.

## The demo warehouse: DuckDB

So the demo is self-contained, costs nothing, and never sleeps, this repo targets DuckDB running inside the Actions runner. Because DuckDB is a single file rather than an always-on warehouse, the repo commits a tiny prod database (`example/ci-state/prod.duckdb`) that stands in for your live prod, and the CI job attaches it read-only as the catalog Slim CI defers to. The Slim CI step still builds only the changed models. Nothing else about the technique changes.

## Swap in a real warehouse

Replace the `ci` output in `profiles.yml` with your warehouse and drop the DuckDB attach block. On BigQuery, Snowflake, or Postgres, prod already exists as a live schema, so you commit only `manifest.json`, not a database file:

```yaml
# profiles.yml (example: BigQuery)
your_project:
  target: dev
  outputs:
    ci:
      type: bigquery
      method: service-account
      project: your-gcp-project
      dataset: "ci_pr_{{ env_var('PR_NUMBER', '0') }}"   # staging schema per PR
      keyfile: "{{ env_var('KEYFILE') }}"
      threads: 4
```

Point `dbt-adapter` at `dbt-bigquery` in the workflow, set your credentials as GitHub secrets, and add a teardown command that drops the CI dataset.

## Run the example locally

Requires Python 3.13 or lower (dbt does not yet run on 3.14).

```bash
python -m venv .venv && . .venv/Scripts/activate   # or .venv/bin/activate
pip install dbt-duckdb==1.10.1
cd example
dbt build --target prod --profiles-dir .           # stand up the demo prod
```

Then change a model, and run the Slim CI build the action runs:

```bash
DBT_CI_PATH=ci.duckdb DBT_CI_SCHEMA=main_ci \
  dbt build --select state:modified+ --defer --state ci-state --target ci --profiles-dir .
```

## Tests

The PR-comment formatter has a smoke test that runs against committed `run_results.json` fixtures, no warehouse needed:

```bash
python scripts/test_format_comment.py
# ran 14 checks
# RESULT: all 14 passed
```

## What is not here

This is deliberately small. It is not a full dbt project, not dbt Cloud, not a scheduled production runner, and not a multi-warehouse abstraction. It does one thing: give dbt Core a free Slim CI check on pull requests.

## License

MIT. See [LICENSE](LICENSE).
