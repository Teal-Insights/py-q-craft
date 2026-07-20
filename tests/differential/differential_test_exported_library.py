"""Exported-library differential test harness.

Compare the generated standalone package against Microsoft Excel via xlwings.
Workbook-specific scenario definitions live in
``tests/differential/qcraft_scenario_matrix.py`` (see ``artifacts/differential_scenario_spec.md``).

Run from the extraction repo after export::

    uv run python -m tests.differential.differential_test_exported_library

From the exported ``dist/`` project (Windows + Excel)::

    uv run --project dist --group validation python -m tests.differential.differential_test_exported_library --layout exported
"""

from __future__ import annotations

import argparse
import csv
import importlib
import logging
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any, Literal, cast

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from excel_grapher.core.address_keys import normalize_key, parse_address

from tests.differential.comparison_utils import (
    apply_health_expectation,
    classify_comparison,
)
from tests.differential.differential_excel import parity_exit_code, read_cell_value
from tests.differential.differential_types import ATOL, Scenario

logger = logging.getLogger(__name__)

LayoutName = Literal["repo", "exported"]


@dataclass(frozen=True)
class DifferentialConfig:
    """Runtime paths and import settings for one differential run."""

    workbook_path: Path
    package_dir: Path
    package_name: str
    import_root: Path
    report_dir: Path
    library_name: str
    atol: float = ATOL
    allow_matched_errors: bool = False


@dataclass(frozen=True)
class Comparison:
    scenario_id: str
    cell_address: str
    cell_label: str
    excel_value: Any
    mvp_value: Any
    abs_diff: float | None
    rel_diff: float | None
    passed: bool
    healthy: bool = False
    outcome: str = "mismatched"
    note: str = ""
    flagged_matched_error: bool = False


CSV_COLUMNS: tuple[str, ...] = (
    "scenario_id",
    "cell_address",
    "cell_label",
    "excel_value",
    "mvp_value",
    "passed",
    "healthy",
    "outcome",
    "abs_diff",
    "rel_diff",
    "note",
    "flagged_matched_error",
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Differential test for the exported standalone library.",
    )
    parser.add_argument(
        "--layout",
        choices=("repo", "exported"),
        default="repo",
        help="Path preset: extraction repo (default) or exported dist/tests copy.",
    )
    parser.add_argument(
        "--workbook-path",
        type=Path,
        default=None,
        help="Override workbook path (defaults depend on --layout).",
    )
    parser.add_argument(
        "--package-name",
        default=None,
        help="Override import module for the MVP oracle (defaults depend on --layout).",
    )
    parser.add_argument(
        "--import-root",
        type=Path,
        default=None,
        help="Directory added to sys.path before importing the MVP oracle.",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=None,
        help="Directory for parity_report.{csv,txt} output.",
    )
    parser.add_argument(
        "--allow-matched-errors",
        action="store_true",
        help=(
            "Triage escape hatch: do not fail the run when both oracles return "
            "the same Excel error on a scenario without expects_error_values=True. "
            "Flagged comparisons are still listed in the report."
        ),
    )
    return parser.parse_args(argv)


def _project_root_from_module(module_path: Path, layout: LayoutName) -> Path:
    return module_path.resolve().parents[2]


def resolve_config(
    *,
    module_path: Path,
    layout: LayoutName,
    workbook_path: Path | None = None,
    package_name: str | None = None,
    import_root: Path | None = None,
    report_dir: Path | None = None,
    allow_matched_errors: bool = False,
) -> DifferentialConfig:
    """Resolve paths from ``workbook_config.py`` and the selected layout."""
    module_path = module_path.resolve()
    repo_root = _project_root_from_module(module_path, layout)

    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from src.pipeline_config import load_pipeline_config

    pipeline = load_pipeline_config(repo_root=repo_root)
    package_dir = pipeline.package_root
    package_slug = pipeline.dist_metadata.package_name
    library_name = pipeline.dist_metadata.library_name

    if layout == "exported":
        tests_root = module_path.parent
        dist_root = repo_root
        defaults = DifferentialConfig(
            workbook_path=tests_root / "fixtures" / pipeline.workbook_path.name,
            package_dir=dist_root / package_slug,
            package_name=f"{package_slug}.api",
            import_root=dist_root,
            report_dir=tests_root / "results" / "local",
            library_name=library_name,
        )
    else:
        defaults = DifferentialConfig(
            workbook_path=pipeline.workbook_path,
            package_dir=package_dir,
            package_name=f"dist.{package_slug}.api",
            import_root=repo_root,
            report_dir=repo_root / pipeline.differential_report_dir_rel,
            library_name=library_name,
        )

    return DifferentialConfig(
        workbook_path=(workbook_path or defaults.workbook_path).resolve(),
        package_dir=defaults.package_dir.resolve(),
        package_name=package_name or defaults.package_name,
        import_root=(import_root or defaults.import_root).resolve(),
        report_dir=(report_dir or defaults.report_dir).resolve(),
        library_name=library_name,
        atol=ATOL,
        allow_matched_errors=allow_matched_errors,
    )


def config_from_args(module_path: Path, args: argparse.Namespace) -> DifferentialConfig:
    return resolve_config(
        module_path=module_path,
        layout=args.layout,
        workbook_path=args.workbook_path,
        package_name=args.package_name,
        import_root=args.import_root,
        report_dir=args.report_dir,
        allow_matched_errors=args.allow_matched_errors,
    )


def compare_cell(
    scenario_id: str,
    cell_address: str,
    cell_label: str,
    excel: Any,
    mvp: Any,
    *,
    atol: float,
    expects_error_values: bool = False,
) -> Comparison:
    passed, healthy, outcome, abs_diff, rel_diff, note = classify_comparison(
        excel, mvp, atol=atol
    )
    healthy = apply_health_expectation(
        expects_error_values=expects_error_values,
        parity_match=passed,
        healthy=healthy,
        outcome=outcome,
    )
    flagged_matched_error = (
        passed and outcome == "matched_error" and not expects_error_values
    )
    return Comparison(
        scenario_id=scenario_id,
        cell_address=cell_address,
        cell_label=cell_label,
        excel_value=excel,
        mvp_value=mvp,
        abs_diff=abs_diff,
        rel_diff=rel_diff,
        passed=passed,
        healthy=healthy,
        outcome=outcome,
        note=note,
        flagged_matched_error=flagged_matched_error,
    )


def compare_scenario(
    scenario: Scenario,
    excel_outputs: dict[str, Any],
    mvp_outputs: dict[str, Any],
    cell_labels: tuple[tuple[str, str], ...],
    *,
    atol: float,
) -> list[Comparison]:
    return [
        compare_cell(
            scenario.id,
            cell_address,
            cell_label,
            excel_outputs.get(cell_address),
            mvp_outputs.get(cell_address),
            atol=atol,
            expects_error_values=scenario.expects_error_values,
        )
        for cell_label, cell_address in cell_labels
    ]


def crash_comparisons(
    scenario: Scenario,
    cell_labels: tuple[tuple[str, str], ...],
    exc: BaseException,
) -> list[Comparison]:
    err_repr = f"<exception: {type(exc).__name__}: {exc}>"
    return [
        Comparison(
            scenario_id=scenario.id,
            cell_address=cell_address,
            cell_label=cell_label,
            excel_value=err_repr,
            mvp_value=err_repr,
            abs_diff=None,
            rel_diff=None,
            passed=False,
        )
        for cell_label, cell_address in cell_labels
    ]


def write_csv_report(comparisons: list[Comparison], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(CSV_COLUMNS)
        for comparison in comparisons:
            writer.writerow(
                [
                    comparison.scenario_id,
                    comparison.cell_address,
                    comparison.cell_label,
                    comparison.excel_value,
                    comparison.mvp_value,
                    comparison.passed,
                    comparison.healthy,
                    comparison.outcome,
                    comparison.abs_diff,
                    comparison.rel_diff,
                    comparison.note,
                    comparison.flagged_matched_error,
                ]
            )


def write_txt_summary(
    comparisons: list[Comparison],
    path: Path,
    *,
    config: DifferentialConfig,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    total = len(comparisons)
    failures = [comparison for comparison in comparisons if not comparison.passed]
    passed = total - len(failures)
    pass_rate = (100.0 * passed / total) if total else 0.0
    healthy = sum(1 for comparison in comparisons if comparison.healthy)
    matched_errors = sum(
        1 for comparison in comparisons if comparison.outcome == "matched_error"
    )
    health_rate = (100.0 * healthy / total) if total else 0.0
    flagged = [
        comparison for comparison in comparisons if comparison.flagged_matched_error
    ]
    failing_run = bool(failures) or bool(flagged and not config.allow_matched_errors)
    result = "FAIL" if failing_run else "PASS"
    health_result = "OK" if healthy == total else "WARN"
    first = failures[0] if failures else None

    with path.open("w", encoding="utf-8") as handle:
        handle.write(
            f"Parity report: exported {config.library_name} standalone library vs Excel\n"
        )
        handle.write(
            f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n"
        )
        handle.write(f"Workbook:  {config.workbook_path}\n")
        handle.write(
            f"Package:   {config.package_dir} (imported as {config.package_name})\n"
        )
        handle.write(f"Tolerance: atol = {config.atol}\n\n")
        handle.write(
            "PARITY (extraction agreement with Excel, including matched errors)\n"
        )
        handle.write(f"Total comparisons: {total}\n")
        handle.write(f"Passed:            {passed}\n")
        handle.write(f"Failed:            {len(failures)}\n")
        handle.write(f"Pass rate:         {pass_rate:.2f}%\n")
        handle.write("Acceptance bar:    100.00%\n")
        handle.write(f"Result:            {result}\n\n")
        handle.write("HEALTH (both sides numeric; matched errors excluded)\n")
        handle.write(f"Healthy:           {healthy}\n")
        handle.write(f"Matched errors:    {matched_errors}\n")
        if flagged:
            allowed_note = (
                " (allowed by --allow-matched-errors)"
                if config.allow_matched_errors
                else " (fails the run)"
            )
            handle.write(f"Flagged errors:    {len(flagged)} flagged{allowed_note}\n")
        handle.write(f"Health rate:       {health_rate:.2f}%\n")
        handle.write(f"Health result:     {health_result}\n")
        if first is not None:
            handle.write("\nFirst divergence:\n")
            handle.write(f"  scenario:  {first.scenario_id}\n")
            handle.write(f"  cell:      {first.cell_address}  ({first.cell_label})\n")
            handle.write(f"  excel:     {first.excel_value!r}\n")
            handle.write(f"  mvp:       {first.mvp_value!r}\n")
            handle.write(f"  abs_diff:  {first.abs_diff!r}\n")
            handle.write(f"  rel_diff:  {first.rel_diff!r}\n")
        if flagged:
            handle.write(
                "\nMATCHED ERROR VALUES (both oracles returned the same Excel "
                "error; fails the run unless the scenario sets "
                "expects_error_values=True or --allow-matched-errors is passed):\n"
            )
            for comparison in flagged:
                handle.write(f"  {comparison.scenario_id} :: ")
                handle.write(f"{comparison.cell_address} ({comparison.cell_label})\n")
                handle.write(f"    excel: {comparison.excel_value!r}\n")
                handle.write(f"    mvp:   {comparison.mvp_value!r}\n")


def load_exported_library(import_root: Path, package_name: str) -> ModuleType:
    root_str = str(import_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return importlib.import_module(package_name)


def run_excel_oracle(
    workbook_path: Path,
    scenario: Scenario,
    output_addresses: tuple[str, ...],
) -> dict[str, Any]:
    import xlwings as xw

    logger.info("Excel oracle: %s", scenario.id)
    app = xw.App(visible=False, add_book=False)
    try:
        workbook = app.books.open(str(workbook_path))
        try:
            app.calculation = "manual"
            for address, value in inputs_for_excel(scenario).items():
                sheet, cell = parse_address(normalize_key(address))
                workbook.sheets[sheet].range(cell).value = value
            workbook.app.calculate()

            def read(address: str) -> Any:
                return read_cell_value(workbook.sheets, address)

            return {address: read(address) for address in output_addresses}
        finally:
            workbook.close()
    finally:
        app.quit()


def _records_to_cells(
    records: list[dict[str, Any]],
    cells: tuple[str, ...],
) -> dict[str, Any]:
    if len(records) != len(cells):
        raise ValueError(f"expected {len(cells)} records, got {len(records)}")
    raw_periods = [record.get("TIME_PERIOD") for record in records]
    if all(period is not None for period in raw_periods):
        periods = cast(list[Any], raw_periods)
        if any(a >= b for a, b in zip(periods, periods[1:], strict=False)):
            raise ValueError(
                f"records' TIME_PERIOD values are not strictly increasing: {periods!r}"
            )
    by_cell: dict[str, Any] = {}
    for index, (record, cell) in enumerate(zip(records, cells, strict=True)):
        if "OBS_VALUE" not in record:
            raise ValueError(f"record {index}: missing OBS_VALUE: {record!r}")
        by_cell[cell] = record["OBS_VALUE"]
    return by_cell


# Optional hook: return compared outputs keyed by cell address without zipping
# full compute_* series. Workbook-specific modules may set this to compare output
# subsets (see tests/differential/qcraft_scenario_matrix.py).
mvp_outputs_for_scenario: Any = None


def run_mvp_oracle(api: ModuleType, scenario: Scenario) -> dict[str, Any]:
    logger.info("MVP oracle:   %s", scenario.id)
    if mvp_outputs_for_scenario is not None:
        return mvp_outputs_for_scenario(api, scenario)
    ctx = api.make_context()
    apply_inputs_to_mvp(api, ctx, scenario)
    outputs: dict[str, Any] = {}
    for entrypoint, cells in output_ranges():
        compute_fn = getattr(api, f"compute_{entrypoint}")
        records = compute_fn(ctx=ctx)
        outputs.update(_records_to_cells(records, cells))
    return outputs


def _verify_paths(config: DifferentialConfig) -> None:
    if not config.workbook_path.is_file():
        raise FileNotFoundError(
            f"Workbook not found: {config.workbook_path}. "
            "Populate data/ and workbook_config.py before running parity tests."
        )
    if (
        not (config.package_dir / "__init__.py").is_file()
        or not (config.package_dir / "api.py").is_file()
    ):
        raise FileNotFoundError(
            f"Exported package incomplete at {config.package_dir} "
            "(expected __init__.py and api.py). "
            "Run 'uv run python -m src.extraction_pipeline' to regenerate."
        )


def _check_staleness(config: DifferentialConfig) -> None:
    data_path = config.package_dir / "data.py"
    if not data_path.is_file():
        return
    workbook_mtime = config.workbook_path.stat().st_mtime
    data_mtime = data_path.stat().st_mtime
    if workbook_mtime > data_mtime:
        logger.warning(
            "Workbook is newer than exported data.py; regenerate dist/ if constants changed."
        )


def _validate_workbook_hooks() -> None:
    scenarios = build_scenarios()
    if not scenarios:
        raise RuntimeError(
            "No differential scenarios configured. Author build_scenarios(), "
            "output_cell_labels(), output_ranges(), inputs_for_excel(), and "
            "apply_inputs_to_mvp() in "
            "tests/differential/qcraft_scenario_matrix.py."
        )
    if not output_cell_labels():
        raise RuntimeError(
            "output_cell_labels() returned no cells. Mirror your output bindings "
            "as (label, address) pairs."
        )
    if not output_ranges() and mvp_outputs_for_scenario is None:
        raise RuntimeError(
            "output_ranges() returned no compute groups. Map each compute_* "
            "entrypoint to its output cell addresses, or provide "
            "mvp_outputs_for_scenario()."
        )


def run_differential_test(config: DifferentialConfig) -> int:
    _validate_workbook_hooks()
    _verify_paths(config)
    _check_staleness(config)

    api = load_exported_library(config.import_root, config.package_name)
    scenarios = build_scenarios()
    cell_labels = output_cell_labels()
    output_addresses = tuple(address for _, address in cell_labels)

    comparisons: list[Comparison] = []
    for scenario in scenarios:
        try:
            excel_outputs = run_excel_oracle(
                config.workbook_path,
                scenario,
                output_addresses,
            )
            mvp_outputs = run_mvp_oracle(api, scenario)
        except Exception as exc:
            logger.exception("Scenario %s crashed; recording as failure.", scenario.id)
            comparisons.extend(crash_comparisons(scenario, cell_labels, exc))
            continue
        comparisons.extend(
            compare_scenario(
                scenario,
                excel_outputs,
                mvp_outputs,
                cell_labels,
                atol=config.atol,
            )
        )

    config.report_dir.mkdir(parents=True, exist_ok=True)
    write_csv_report(comparisons, config.report_dir / "parity_report.csv")
    write_txt_summary(
        comparisons,
        config.report_dir / "parity_report.txt",
        config=config,
    )

    failed = sum(1 for comparison in comparisons if not comparison.passed)
    flagged = sum(1 for comparison in comparisons if comparison.flagged_matched_error)
    logger.info("Done. Failures: %d / %d", failed, len(comparisons))
    if flagged:
        log = logger.warning if config.allow_matched_errors else logger.error
        log(
            "Matched error values in %d comparison(s); see MATCHED ERROR VALUES in %s "
            "(set Scenario.expects_error_values=True when intentional)",
            flagged,
            config.report_dir / "parity_report.txt",
        )
    return parity_exit_code(
        failed=failed,
        flagged_matched_errors=flagged,
        allow_matched_errors=config.allow_matched_errors,
    )


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        args = parse_args(argv)
        config = config_from_args(Path(__file__).resolve(), args)
        return run_differential_test(config)
    except RuntimeError as exc:
        logger.error("%s", exc)
        return 2
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return 2
    except Exception:
        logger.exception("Differential test failed with an unhandled exception.")
        return 2


# --------------------------------------------------------------------------
# Workbook-specific hooks — Q-CRAFT scenario matrix (see artifacts/differential_scenario_spec.md).
# --------------------------------------------------------------------------

from tests.differential.qcraft_scenario_matrix import (  # noqa: E402
    apply_inputs_to_mvp,
    build_scenarios,
    inputs_for_excel,
    mvp_outputs_for_scenario,  # noqa: F811
    output_cell_labels,
    output_ranges,
)


if __name__ == "__main__":
    sys.exit(main())
