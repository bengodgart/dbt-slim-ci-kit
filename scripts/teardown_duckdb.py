#!/usr/bin/env python3
"""Drop the staging schema the DuckDB demo built into, so CI leaves nothing behind.

On a real warehouse you would drop the CI staging schema with a warehouse-native
statement instead (documented in the README). Best-effort: never fails the job.

Usage: python teardown_duckdb.py <ci_database_path> <staging_schema>
"""
import sys


def main():
    if len(sys.argv) < 3:
        print("teardown: nothing to do (missing args)")
        return 0
    db_path, schema = sys.argv[1], sys.argv[2]
    try:
        import duckdb
    except ImportError:
        print("teardown: duckdb not available, skipping")
        return 0
    try:
        con = duckdb.connect(db_path)
        con.execute('DROP SCHEMA IF EXISTS "{}" CASCADE'.format(schema))
        con.close()
        print("teardown: dropped staging schema {}".format(schema))
    except Exception as exc:  # noqa: BLE001  best-effort cleanup
        print("teardown: skipped ({})".format(exc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
