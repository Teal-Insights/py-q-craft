"""FormulaEvaluator backend for the series-graph API.

Builds one excel-grapher dependency graph over the output-series cells (plus
the Dashboard inputs drawn in the viz) and keeps it for the process lifetime.
The built graph is stored under ``.cache/dependency-graph`` and loaded on the
next start. Optional: requires ``excel-grapher`` and
``tests/fixtures/qcraft-toolv10.xlsx``.
"""

from __future__ import annotations

import hashlib
import json
import threading
from importlib.metadata import version
from pathlib import Path
from typing import Any, Literal

from .blank_ranges import BLANK_RANGES
from .graph_schema import (
    NODES_BY_ID,
    SERIES_IDS,
    VIZ_INPUT_IDS,
    all_cell_addresses,
    input_cell_writes,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKBOOK = _REPO_ROOT / "tests" / "fixtures" / "qcraft-toolv10.xlsx"
DEFAULT_BINDINGS = _REPO_ROOT / "bindings"
DEFAULT_CACHE_DIR = _REPO_ROOT / ".cache" / "dependency-graph"
_EVAL_LOCK = threading.Lock()

# Dynamic-ref domains used when no series bindings are shipped.
_CONSTRAINTS_SCHEMA: dict[str, Any] = {
    "Dashboard!C17": Literal["High", "Low", "Medium"],
    "Dashboard!C28": Literal[
        "Interest-growth differential",
        "Nominal interest rate",
        "Real interest rate (a)",
    ],
    "Dashboard!C33": Literal["No", "Yes"],
}

_driver: _FormulaEvaluatorDriver | None = None
_driver_workbook: Path | None = None


def is_available(*, workbook: Path | None = None) -> bool:
    path = workbook or DEFAULT_WORKBOOK
    if not path.is_file():
        return False
    try:
        import inspect

        import excel_grapher  # noqa: F401
        import fastpyxl
        from excel_grapher.grapher import (  # noqa: F401
            DynamicRefConfig,
            create_dependency_graph,
        )

        # excel-grapher may require a newer fastpyxl than is installed.
        if "keep_formula_cache" not in inspect.signature(fastpyxl.load_workbook).parameters:
            return False
    except ImportError:
        return False
    return True


def _as_json_number(value: object) -> Any:
    if hasattr(value, "value") and type(value).__name__ in {"FormulaValue", "XlError"}:
        value = getattr(value, "value", value)
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return int(value)
    if isinstance(value, float):
        return float(value)
    try:
        as_float = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return value
    if as_float.is_integer():
        return int(as_float)
    return as_float


def _build_dynamic_refs(workbook: Path) -> Any:
    from excel_grapher.grapher import DynamicRefConfig

    if DEFAULT_BINDINGS.is_dir():
        from excel_grapher.series_bindings import load_series_bindings

        bindings = load_series_bindings(DEFAULT_BINDINGS)
        return DynamicRefConfig.from_bindings(bindings, workbook, bindings_path=DEFAULT_BINDINGS)
    return DynamicRefConfig.from_constraints(_CONSTRAINTS_SCHEMA)


def _bindings_fingerprint(bindings_path: Path) -> str:
    digest = hashlib.sha256()
    if not bindings_path.is_dir():
        return digest.hexdigest()
    for path in sorted(bindings_path.glob("*.bindings.yaml")):
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _cache_key(workbook: Path, targets: list[str]) -> str:
    digest = hashlib.sha256()
    digest.update(version("excel-grapher").encode())
    digest.update(b"\0")
    digest.update(hashlib.sha256(workbook.read_bytes()).hexdigest().encode())
    digest.update(b"\0")
    digest.update(_bindings_fingerprint(DEFAULT_BINDINGS).encode())
    digest.update(b"\0")
    for target in targets:
        digest.update(target.encode("utf-8"))
        digest.update(b"\0")
    for blank in BLANK_RANGES:
        digest.update(blank.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def _cache_paths(cache_dir: Path, cache_key: str) -> tuple[Path, Path]:
    return cache_dir / f"{cache_key}.pkl.gz", cache_dir / f"{cache_key}.meta.json"


def _load_cached_graph(workbook: Path, targets: list[str], cache_dir: Path) -> Any | None:
    from excel_grapher.grapher import load_graph

    cache_key = _cache_key(workbook, targets)
    payload_path, meta_path = _cache_paths(cache_dir, cache_key)
    if not payload_path.is_file() or not meta_path.is_file():
        return None
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if meta.get("cache_key") != cache_key:
        return None
    if meta.get("excel_grapher_version") != version("excel-grapher"):
        return None
    return load_graph(payload_path)


def _save_cached_graph(graph: Any, workbook: Path, targets: list[str], cache_dir: Path) -> str:
    from excel_grapher.grapher import dump_graph

    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_key = _cache_key(workbook, targets)
    payload_path, meta_path = _cache_paths(cache_dir, cache_key)
    dump_graph(graph, payload_path)
    meta = {
        "cache_key": cache_key,
        "excel_grapher_version": version("excel-grapher"),
        "node_count": len(graph),
        "target_count": len(targets),
        "workbook": str(workbook),
    }
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return cache_key


def _open_graph(workbook: Path) -> Any:
    from excel_grapher.grapher import create_dependency_graph

    targets = list(all_cell_addresses())
    cached = _load_cached_graph(workbook, targets, DEFAULT_CACHE_DIR)
    if cached is not None:
        print(
            f"formula_evaluator: cache hit ({len(cached)} nodes, "
            f"{len(targets)} targets)"
        )
        return cached
    print(
        f"formula_evaluator: building dependency graph "
        f"({len(targets)} targets)…"
    )
    graph = create_dependency_graph(
        workbook,
        targets,
        load_values=True,
        dynamic_refs=_build_dynamic_refs(workbook),
        blank_ranges=BLANK_RANGES,
    )
    _save_cached_graph(graph, workbook, targets, DEFAULT_CACHE_DIR)
    print(f"formula_evaluator: cached graph ({len(graph)} nodes)")
    return graph


class _FormulaEvaluatorDriver:
    """Hold one DependencyGraph + FormulaEvaluator for repeated evaluates."""

    def __init__(self, workbook: Path) -> None:
        from excel_grapher import FormulaEvaluator

        self.workbook = workbook
        self.graph = _open_graph(workbook)
        self.evaluator = FormulaEvaluator(self.graph)
        self._baselines: dict[str, object] = {}
        for address in self._input_addresses():
            node = self.graph.get_node(address)
            if node is not None and getattr(node, "is_leaf", False):
                self._baselines[address] = node.value

    @staticmethod
    def _input_addresses() -> list[str]:
        addresses: list[str] = []
        for series_id in VIZ_INPUT_IDS:
            node = NODES_BY_ID[series_id]
            if "address" in node:
                addresses.append(node["address"])
            addresses.extend(node.get("addresses", {}).values())
        return addresses

    def reset_inputs(self) -> None:
        for address, value in self._baselines.items():
            self.graph.set_node_value(address, value)

    def apply_inputs(self, flat_inputs: dict[str, Any]) -> None:
        self.reset_inputs()
        for address, value in input_cell_writes(flat_inputs).items():
            self.graph.set_node_value(address, value)

    def _series_addresses(self) -> list[str]:
        addresses: list[str] = []
        for series_id in SERIES_IDS:
            if series_id in VIZ_INPUT_IDS:
                continue
            node = NODES_BY_ID[series_id]
            if "address" in node:
                addresses.append(node["address"])
            else:
                addresses.extend(node["addresses"].values())
        return list(dict.fromkeys(addresses))

    def read_series_values(self, flat_inputs: dict[str, Any]) -> dict[str, Any]:
        addresses = self._series_addresses()
        evaluated = self.evaluator.evaluate(addresses) if addresses else {}
        if not isinstance(evaluated, dict):
            evaluated = {addresses[0]: evaluated}
        values: dict[str, Any] = {name: flat_inputs[name] for name in VIZ_INPUT_IDS}
        for series_id in SERIES_IDS:
            if series_id in values:
                continue
            node = NODES_BY_ID[series_id]
            if "address" in node:
                values[series_id] = _as_json_number(evaluated[node["address"]])
                continue
            series_map: dict[Any, Any] = {}
            for key, address in node["addresses"].items():
                series_map[key] = _as_json_number(evaluated[address])
            values[series_id] = series_map
        return values

    def series_dependency_edges(self) -> list[tuple[str, str]]:
        """Upstream → downstream series edges for hop layout.

        A series depends on another when one of its cells reads that series,
        walking through formula cells that are not themselves a series. Cells
        in the same series do not count, so a year chain is one node.
        """
        cached = getattr(self, "_series_edges", None)
        if cached is not None:
            return cached
        cell_to_series: dict[str, str] = {}
        series_cells: dict[str, list[str]] = {}
        for series_id, node in NODES_BY_ID.items():
            addresses: list[str] = []
            if "address" in node:
                addresses.append(node["address"])
            addresses.extend(node.get("addresses", {}).values())
            series_cells[series_id] = addresses
            for address in addresses:
                cell_to_series[address] = series_id
        edges: list[tuple[str, str]] = []
        for series_id, cells in series_cells.items():
            stack = list(cells)
            seen = set(cells)
            upstream: set[str] = set()
            while stack:
                cell = stack.pop()
                for dep in self.graph.get_dependencies(cell):
                    if dep in seen:
                        continue
                    owner = cell_to_series.get(dep)
                    if owner is None:
                        if self.graph.get_node(dep) is None:
                            continue
                        seen.add(dep)
                        stack.append(dep)
                    elif owner != series_id:
                        upstream.add(owner)
            for source in sorted(upstream):
                edges.append((source, series_id))
        self._series_edges = edges
        return edges


def series_dependency_edges(*, workbook: Path | None = None) -> list[tuple[str, str]]:
    """Series hop edges from the cached FormulaEvaluator graph."""
    with _EVAL_LOCK:
        return list(_get_driver(workbook).series_dependency_edges())


def _get_driver(workbook: Path | None = None) -> _FormulaEvaluatorDriver:
    global _driver, _driver_workbook
    path = (workbook or DEFAULT_WORKBOOK).resolve()
    if _driver is None or _driver_workbook != path:
        if not is_available(workbook=path):
            raise RuntimeError(
                "formula_evaluator backend requires excel-grapher and "
                f"workbook at {path}"
            )
        _driver = _FormulaEvaluatorDriver(path)
        _driver_workbook = path
    return _driver


def evaluate(flat_inputs: dict[str, Any], *, workbook: Path | None = None) -> dict[str, Any]:
    """Write flat inputs onto the graph and return full series value maps."""
    with _EVAL_LOCK:
        driver = _get_driver(workbook)
        driver.apply_inputs(flat_inputs)
        return driver.read_series_values(flat_inputs)


def warm(*, workbook: Path | None = None) -> dict[str, Any]:
    """Load or build the cached graph and construct FormulaEvaluator."""
    with _EVAL_LOCK:
        driver = _get_driver(workbook)
    return {
        "nodes": len(driver.graph),
        "series": len(SERIES_IDS),
        "workbook": str(driver.workbook),
    }


def reset_driver() -> None:
    """Drop the cached graph (tests / workbook swap)."""
    global _driver, _driver_workbook
    _driver = None
    _driver_workbook = None


__all__ = [
    "DEFAULT_CACHE_DIR",
    "DEFAULT_WORKBOOK",
    "evaluate",
    "is_available",
    "reset_driver",
    "series_dependency_edges",
    "warm",
]
