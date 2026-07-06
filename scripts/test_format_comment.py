#!/usr/bin/env python3
"""Smoke test for format_comment.py. No dbt or warehouse needed: it runs the
formatter against committed run_results fixtures and asserts the output.

Run:  python scripts/test_format_comment.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import json
import format_comment as fc

FIXTURES = os.path.join(ROOT, "tests", "fixtures")
checks = 0
failures = []


def check(cond, label):
    global checks
    checks += 1
    if not cond:
        failures.append(label)


def load(name):
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as f:
        return json.load(f)


def main():
    name_map = fc.load_name_map(os.path.join(FIXTURES, "manifest.json"))
    check(len(name_map) > 0, "manifest name map is non-empty")

    # --- passing run ---
    passing = fc.build_comment(load("run_results.pass.json"), "state:modified+", name_map)
    check("dbt Slim CI: SUCCESS" in passing, "passing run reports SUCCESS")
    check("0 failed" in passing, "passing run shows 0 failed")
    check("| model | `stg_orders` |" in passing, "passing run lists the changed model stg_orders")
    check("| model | `customers` |" in passing, "passing run lists descendant customers")
    check("| model | `order_stats` |" in passing, "passing run lists descendant order_stats")
    # stg_customers is unchanged and deferred: it must NOT appear as a built row.
    check("`stg_customers`" not in passing, "passing run does not build the deferred stg_customers")
    check("state:modified+" in passing, "passing run states the selection expression")

    # --- failing run ---
    failing = fc.build_comment(load("run_results.fail.json"), "state:modified+", name_map)
    check("dbt Slim CI: FAILURE" in failing, "failing run reports FAILURE")
    check("1 failed" in failing, "failing run shows 1 failed")
    check("accepted_values_stg_orders_status" in failing, "failing run names the failing test")
    # Failures sort to the top row of the table.
    table_start = failing.index("| --- | --- | --- | --- |")
    first_row = failing[table_start:].splitlines()[1]
    check(first_row.startswith("| FAIL "), "failing run sorts the failure to the top")

    # --- missing artifact path is handled, not crashed ---
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fc.main([os.path.join(FIXTURES, "does_not_exist.json")])
    check(rc == 0 and "no run_results.json" in buf.getvalue(), "missing artifact yields an honest comment, not a crash")

    # --- no em-dash anywhere the formatter can emit ---
    em_dash = chr(0x2014)
    check(em_dash not in passing and em_dash not in failing, "formatter output contains no em-dash")

    print("ran {} checks".format(checks))
    if failures:
        for f in failures:
            print("FAIL: " + f)
        print("RESULT: {} FAILED".format(len(failures)))
        return 1
    print("RESULT: all {} passed".format(checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
