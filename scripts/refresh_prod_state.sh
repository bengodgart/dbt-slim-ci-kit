#!/usr/bin/env bash
# Regenerate the committed prod state that Slim CI defers to.
#
# Run this whenever you merge changes to prod, so the manifest reflects the new
# production state. On a real warehouse you would instead pull the manifest your
# production job already produced (dbt Cloud artifacts, an S3 bucket, etc.) and
# only the manifest.json is committed, not a database file.
#
# Usage: scripts/refresh_prod_state.sh   (run from the repo root)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="${1:-$HERE/../example}"

cd "$PROJECT_DIR"
mkdir -p ci-state

# Build the full project into the committed prod database.
dbt build --target prod --profiles-dir . --no-partial-parse

# Freeze the manifest Slim CI compares against.
cp target/manifest.json ci-state/manifest.json

echo "Refreshed ci-state/manifest.json and ci-state/prod.duckdb"
