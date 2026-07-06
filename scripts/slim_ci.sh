#!/usr/bin/env bash
# Run the Slim CI build: only the models changed in this pull request and their
# descendants are built and tested, in the CI target's staging schema. Every
# unchanged model is deferred to prod via the committed prod manifest.
#
# Usage: slim_ci.sh <project-dir> <state-dir> <target> <profiles-dir>
# The selection expression can be overridden with SLIM_CI_SELECT.
set -uo pipefail

PROJECT_DIR="${1:-.}"
STATE_DIR="${2:-ci-state}"
TARGET="${3:-ci}"
PROFILES_DIR="${4:-.}"
SELECT="${SLIM_CI_SELECT:-state:modified+}"

cd "$PROJECT_DIR" || exit 2

dbt build \
  --select "$SELECT" \
  --defer --state "$STATE_DIR" \
  --target "$TARGET" \
  --profiles-dir "$PROFILES_DIR" \
  --no-partial-parse
exit $?
