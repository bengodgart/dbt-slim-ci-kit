#!/usr/bin/env python3
"""Turn a dbt run_results.json into a Markdown comment for a pull request.

Reads the artifact dbt writes after `dbt build` and prints a compact summary:
an overall verdict, a counts line, and a table of what ran. Only nodes that
actually executed are listed (deferred and skipped nodes are counted, not
listed), because in Slim CI most of the project is intentionally not built.

Usage:
    python format_comment.py path/to/run_results.json [--select state:modified+]
"""
import argparse
import json
import sys

PASS_STATES = {"success", "pass"}
FAIL_STATES = {"error", "fail", "runtime error"}
SKIP_STATE = "skipped"


def classify(unique_id):
    kind = unique_id.split(".", 1)[0]
    return kind if kind in ("model", "test", "seed", "snapshot") else "other"


def short_name(unique_id, name_map=None):
    if name_map and unique_id in name_map:
        return name_map[unique_id]
    return unique_id.split(".")[-1]


def load_name_map(manifest_path):
    """Map unique_id to the clean node name from a manifest.

    dbt hashes long test unique_ids, so the tail of the id is unreadable; the
    manifest keeps the human name. Optional: falls back to the id tail.
    """
    if not manifest_path:
        return {}
    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    except (FileNotFoundError, ValueError):
        return {}
    name_map = {}
    for section in ("nodes", "sources", "unit_tests"):
        for uid, node in manifest.get(section, {}).items():
            if isinstance(node, dict) and node.get("name"):
                name_map[uid] = node["name"]
    return name_map


def verdict_icon(status):
    s = status.lower()
    if s in PASS_STATES:
        return "PASS"
    if s in FAIL_STATES:
        return "FAIL"
    if s == SKIP_STATE:
        return "SKIP"
    return status.upper()


def build_comment(data, select_expr, name_map=None):
    results = data.get("results", [])
    elapsed = data.get("elapsed_time", 0.0)

    models_built = tests_passed = tests_failed = models_failed = skipped = 0
    rows = []
    for r in results:
        uid = r.get("unique_id", "")
        status = (r.get("status") or "").lower()
        kind = classify(uid)
        exec_time = r.get("execution_time", 0.0)

        if status == SKIP_STATE:
            skipped += 1
            continue
        if kind == "test":
            if status in PASS_STATES:
                tests_passed += 1
            else:
                tests_failed += 1
        elif kind in ("model", "seed", "snapshot"):
            if status in PASS_STATES:
                models_built += 1
            else:
                models_failed += 1
        rows.append((verdict_icon(status), kind, short_name(uid, name_map), exec_time))

    failed = models_failed + tests_failed
    overall = "FAILURE" if failed else "SUCCESS"

    lines = []
    lines.append("## dbt Slim CI: {}".format(overall))
    lines.append("")
    lines.append(
        "Built **{}** models, ran **{}** tests "
        "({} passed, {} failed) in **{:.1f}s**.".format(
            models_built, tests_passed + tests_failed, tests_passed, tests_failed, elapsed
        )
    )
    lines.append("")
    lines.append(
        "Selection: `{}`. Only models changed in this pull request and their "
        "descendants were built; every unchanged model was deferred to prod.".format(
            select_expr
        )
    )
    lines.append("")

    if rows:
        # Failures first, then models, then tests, each alphabetical.
        order = {"FAIL": 0, "PASS": 1, "SKIP": 2}
        rows.sort(key=lambda x: (order.get(x[0], 3), x[1], x[2]))
        lines.append("| Result | Type | Name | Time |")
        lines.append("| --- | --- | --- | --- |")
        for icon, kind, name, t in rows:
            lines.append("| {} | {} | `{}` | {:.2f}s |".format(icon, kind, name, t))
    else:
        lines.append("_No nodes were selected. Nothing changed in this pull request._")

    lines.append("")
    lines.append("<sub>Posted by dbt-slim-ci-kit. Deferred and skipped nodes are counted, not listed.</sub>")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run_results", help="path to target/run_results.json")
    ap.add_argument("--select", default="state:modified+", help="selection expression used")
    ap.add_argument("--manifest", default=None, help="path to target/manifest.json for clean names")
    args = ap.parse_args(argv)

    try:
        with open(args.run_results, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        # No artifact means dbt did not produce results (for example a parse
        # error before any node ran). Emit an honest comment instead of crashing.
        print("## dbt Slim CI: FAILURE\n\ndbt produced no run_results.json. "
              "The run failed before any model was built. Check the job log.")
        return 0

    name_map = load_name_map(args.manifest)
    print(build_comment(data, args.select, name_map))
    return 0


if __name__ == "__main__":
    sys.exit(main())
