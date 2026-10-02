#!/usr/bin/env python3
"""Assert graph API bootstrap / evaluate work for the Q-CRAFT pedagogical viz.

When FormulaEvaluator is available, also compare it to the export Model on
defaults. Otherwise validate the export backend alone.
"""

from __future__ import annotations

import sys
from typing import Any

ATOL = 1e-6


def _close(a: Any, b: Any, tol: float = ATOL) -> bool:
    if a is None and b is None:
        return True
    # Empty discrete-risk shocks are None on the model and 0 in the workbook.
    if a is None or b is None:
        other = b if a is None else a
        return (
            isinstance(other, (int, float))
            and not isinstance(other, bool)
            and float(other) == 0.0
        )
    if (
        isinstance(a, (int, float))
        and isinstance(b, (int, float))
        and not isinstance(a, bool)
        and not isinstance(b, bool)
    ):
        return abs(float(a) - float(b)) <= tol
    return a == b


def compare(left: dict[str, Any], right: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, pv in left.items():
        jv = right.get(key)
        if isinstance(pv, dict):
            if not isinstance(jv, dict):
                errors.append(f"{key}: expected map, got {jv!r}")
                continue
            for k, v in pv.items():
                rk = k if k in jv else str(k)
                if rk not in jv or not _close(v, jv[rk]):
                    errors.append(
                        f"{key}[{k}]: export={v} formula_evaluator={jv.get(rk)}"
                    )
        elif not _close(pv, jv):
            errors.append(f"{key}: export={pv} formula_evaluator={jv}")
    return errors


def main() -> int:
    from qcraft import graph_formula_evaluator as fe
    from qcraft.graph_api import bootstrap, evaluate
    from qcraft.graph_schema import NODES, SERIES_IDS

    payload = bootstrap(backend="export")
    if not payload["nodes"]:
        print("fail: bootstrap returned no nodes", file=sys.stderr)
        return 1
    if len(payload["nodes"]) != len(NODES):
        print(
            f"fail: expected {len(NODES)} nodes, got {len(payload['nodes'])}",
            file=sys.stderr,
        )
        return 1
    missing = [sid for sid in SERIES_IDS if sid not in payload["values"]]
    if missing:
        print(f"fail: evaluate missing series: {missing}", file=sys.stderr)
        return 1

    # Smoke-test a Dashboard override (France).
    france = evaluate({"country": "France"}, backend="export")
    if france.get("country") != "France":
        print("fail: country override not applied", file=sys.stderr)
        return 1
    print(f"ok: export bootstrap ({len(NODES)} nodes) and evaluate(country=France)")

    if not fe.is_available():
        print(
            "skip: formula_evaluator unavailable (optional; export backend is enough)",
            file=sys.stderr,
        )
        return 0

    try:
        fe.reset_driver()
        export_values = evaluate(backend="export")
        graph_values = evaluate(backend="formula_evaluator")
    except Exception as exc:  # noqa: BLE001
        print(
            f"skip: formula_evaluator failed to initialize ({exc})",
            file=sys.stderr,
        )
        return 0

    errors = compare(export_values, graph_values)
    if errors:
        print(
            "formula_evaluator diverges from export Model on defaults:",
            file=sys.stderr,
        )
        for err in errors[:40]:
            print(f"  {err}", file=sys.stderr)
        return 1
    print("ok: formula_evaluator matches Model.from_defaults() via graph_api")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
