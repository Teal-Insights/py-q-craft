"""Series topology for the interactive Q-CRAFT dependency-graph viz.

Dashboard scalars and the hand-written story edges stay. Every series in the
input, internal, and output binding shards is also a node so FormulaEvaluator
can return the full bound surface. Addresses come from ``data``.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

from . import data
from .model import Model

_BINDINGS_DIR = Path(__file__).resolve().parents[1] / "bindings"

BackendName = Literal["export", "formula_evaluator"]

# Full Model constructor surface (includes matrix shocks used at evaluate time).
INPUT_IDS: tuple[str, ...] = tuple(Model._INPUT_IDS)

# Story inputs. Bound shock matrices are appended after the binding shards load.
VIZ_INPUT_IDS: tuple[str, ...] = (
    "country",
    "demography_scenario",
    "productivity_start",
    "productivity_end",
    "inflation_start",
    "inflation_end",
    "interest_rate_mode",
    "real_interest_rate",
    "fiscal_rule_enabled",
    "debt_target",
    "expenditure_rigidity",
)

SERIES_IDS: tuple[str, ...] = VIZ_INPUT_IDS + (
    "productivity_growth",
    "inflation_path",
    "baseline_interest_rate",
    "macrofiscal_debt_to_gdp",
    "demography_total_population",
    "climate_data_labour_productivity_growth_variation_paris",
    "baseline_debt_to_gdp",
    "baseline_primary_balance_pct_gdp",
    "baseline_overall_balance_pct_gdp",
    "baseline_real_gdp_growth",
    "baseline_fiscal_consolidation_gap",
    "paris_engine_gross_debt_pct_gdp",
    "hot_unadapted_engine_gross_debt_pct_gdp",
    "output_scenarios_debt_to_gdp_summary_paris",
    "output_scenarios_debt_to_gdp_summary_hot_unadapted",
)

EDGES: tuple[tuple[str, str], ...] = (
    ("productivity_start", "productivity_growth"),
    ("productivity_end", "productivity_growth"),
    ("inflation_start", "inflation_path"),
    ("inflation_end", "inflation_path"),
    ("interest_rate_mode", "baseline_interest_rate"),
    ("real_interest_rate", "baseline_interest_rate"),
    ("country", "macrofiscal_debt_to_gdp"),
    ("country", "demography_total_population"),
    ("demography_scenario", "demography_total_population"),
    ("country", "climate_data_labour_productivity_growth_variation_paris"),
    ("macrofiscal_debt_to_gdp", "baseline_debt_to_gdp"),
    ("productivity_growth", "baseline_debt_to_gdp"),
    ("demography_total_population", "baseline_debt_to_gdp"),
    ("baseline_interest_rate", "baseline_debt_to_gdp"),
    ("inflation_path", "baseline_debt_to_gdp"),
    ("fiscal_rule_enabled", "baseline_debt_to_gdp"),
    ("debt_target", "baseline_debt_to_gdp"),
    ("expenditure_rigidity", "baseline_debt_to_gdp"),
    ("macrofiscal_debt_to_gdp", "baseline_primary_balance_pct_gdp"),
    ("productivity_growth", "baseline_primary_balance_pct_gdp"),
    ("baseline_interest_rate", "baseline_primary_balance_pct_gdp"),
    ("fiscal_rule_enabled", "baseline_primary_balance_pct_gdp"),
    ("debt_target", "baseline_primary_balance_pct_gdp"),
    ("expenditure_rigidity", "baseline_primary_balance_pct_gdp"),
    ("baseline_primary_balance_pct_gdp", "baseline_overall_balance_pct_gdp"),
    ("baseline_interest_rate", "baseline_overall_balance_pct_gdp"),
    ("productivity_growth", "baseline_real_gdp_growth"),
    ("demography_total_population", "baseline_real_gdp_growth"),
    ("baseline_debt_to_gdp", "baseline_fiscal_consolidation_gap"),
    ("baseline_primary_balance_pct_gdp", "baseline_fiscal_consolidation_gap"),
    ("debt_target", "baseline_fiscal_consolidation_gap"),
    ("baseline_debt_to_gdp", "paris_engine_gross_debt_pct_gdp"),
    ("baseline_primary_balance_pct_gdp", "paris_engine_gross_debt_pct_gdp"),
    ("climate_data_labour_productivity_growth_variation_paris", "paris_engine_gross_debt_pct_gdp"),
    ("baseline_debt_to_gdp", "hot_unadapted_engine_gross_debt_pct_gdp"),
    ("baseline_primary_balance_pct_gdp", "hot_unadapted_engine_gross_debt_pct_gdp"),
    ("paris_engine_gross_debt_pct_gdp", "output_scenarios_debt_to_gdp_summary_paris"),
    (
        "hot_unadapted_engine_gross_debt_pct_gdp",
        "output_scenarios_debt_to_gdp_summary_hot_unadapted",
    ),
)


def axes() -> dict[str, list[Any]]:
    years = list(getattr(getattr(data, "TIME_PERIOD_AXIS", None), "keys", ()) or ())
    countries = list(getattr(getattr(data, "COUNTRY_AXIS", None), "keys", ()) or ())
    scenarios = list(getattr(getattr(data, "SCENARIO_AXIS", None), "keys", ()) or ())
    return {
        "years": years,
        "countries": countries,
        "scenarios": scenarios,
        "shock_params": [],
    }


def _flat_addresses(cells: Mapping[Any, str]) -> dict[Any, str]:
    out: dict[Any, str] = {}
    for coord, address in cells.items():
        if isinstance(coord, tuple) and len(coord) == 1:
            out[coord[0]] = address
        elif coord == ():
            continue
        else:
            out[coord] = address
    return out


def _scalar_address(cells: Mapping[Any, str]) -> str:
    return cells[()]


def _sheet_of(address: str) -> str:
    return address.split("!", 1)[0]


def _domain(min_value: float, max_value: float) -> dict[str, float]:
    return {"min": min_value, "max": max_value}


def _keys_from_spec(spec: Any) -> list[Any]:
    keys: list[Any] = []
    for coord in spec.domain:
        if isinstance(coord, tuple) and len(coord) == 1:
            keys.append(coord[0])
        else:
            keys.append(coord)
    return keys


def _node(
    *,
    series_id: str,
    role: str,
    kind: str,
    keys: list[Any],
    address: str | None = None,
    addresses: dict[Any, str] | None = None,
    domain: dict[str, float] | None = None,
    options: list[Any] | None = None,
    option_labels: dict[Any, str] | None = None,
) -> dict[str, Any]:
    if address is not None:
        sample = address
    elif addresses:
        sample = next(iter(addresses.values()))
    else:
        raise ValueError(f"{series_id} needs address or addresses")
    node: dict[str, Any] = {
        "id": series_id,
        "role": role,
        "label": series_id,
        "sheet": _sheet_of(sample),
        "kind": kind,
        "keys": keys,
    }
    if address is not None:
        node["address"] = address
    if addresses is not None:
        node["addresses"] = {
            (str(k) if not isinstance(k, (str, int, float)) else k): v
            for k, v in addresses.items()
        }
    if domain is not None:
        node["domain"] = domain
    if options is not None:
        node["options"] = options
    if option_labels is not None:
        node["optionLabels"] = option_labels
    return node


def _year_node(series_id: str, role: str, spec: Any, *, domain: dict[str, float]) -> dict[str, Any]:
    return _node(
        series_id=series_id,
        role=role,
        kind="year_map",
        keys=_keys_from_spec(spec),
        addresses=_flat_addresses(spec.cells),
        domain=domain,
    )


def _json_key(coord: Any) -> Any:
    """Match ``graph_api`` flat maps: one-tuples unwrap, longer tuples join with ``|``."""
    if isinstance(coord, tuple) and len(coord) == 1:
        return _json_key(coord[0])
    if isinstance(coord, tuple):
        return "|".join(str(part) for part in coord)
    return coord


def _binding_series(filename: str) -> list[dict[str, Any]]:
    path = _BINDINGS_DIR / filename
    if not path.is_file():
        return []
    import yaml

    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    series = document.get("series") or []
    return [entry for entry in series if isinstance(entry.get("id"), str) and entry.get("id")]


def _lane(series: dict[str, Any], default: str) -> str:
    groups = series.get("groups") or []
    if groups:
        path = (groups[0] or {}).get("path") or []
        if path:
            return str(path[0])
    sheet = series.get("sheet")
    if isinstance(sheet, str) and sheet:
        return sheet
    return default


def _quote_sheet(address: str) -> str:
    if "!" not in address:
        return address
    sheet, cell = address.split("!", 1)
    if " " in sheet and not (sheet.startswith("'") and sheet.endswith("'")):
        sheet = f"'{sheet}'"
    return f"{sheet}!{cell}"


def _bound_series_node(
    series_id: str,
    role: str,
    lane: str,
    data_range: Any,
) -> dict[str, Any]:
    spec = getattr(data, series_id.upper(), None)
    if spec is not None and hasattr(spec, "cells") and hasattr(spec, "domain"):
        flat = _flat_addresses(spec.cells)
        keys: list[Any] = []
        addresses: dict[Any, str] = {}
        for coord in spec.domain:
            raw = coord[0] if isinstance(coord, tuple) and len(coord) == 1 else coord
            key = _json_key(raw)
            keys.append(key)
            addresses[key] = flat[raw]
        kind = "matrix" if keys and isinstance(keys[0], str) and "|" in keys[0] else "year_map"
        node = _node(
            series_id=series_id,
            role=role,
            kind=kind,
            keys=keys,
            addresses=addresses,
        )
        node["lane"] = lane
        return node
    if isinstance(data_range, str):
        cell = data_range.split("!", 1)[-1]
        if ":" not in cell:
            node = _node(
                series_id=series_id,
                role=role,
                kind="float",
                keys=[None],
                address=_quote_sheet(data_range),
            )
            node["lane"] = lane
            return node
    raise KeyError(f"no cell map for bound series {series_id}")


def _append_bound(
    nodes: tuple[dict[str, Any], ...],
    filename: str,
    role: str,
) -> tuple[dict[str, Any], ...]:
    """Append bound series that are not already story nodes."""
    present = {node["id"] for node in nodes}
    extra: list[dict[str, Any]] = []
    for series in _binding_series(filename):
        series_id = series["id"]
        if series_id in present:
            continue
        extra.append(
            _bound_series_node(series_id, role, _lane(series, role), series.get("data_range"))
        )
        present.add(series_id)
    if not extra:
        return nodes
    return nodes + tuple(extra)


NODES: tuple[dict[str, Any], ...] = (
    _node(
        series_id="country",
        role="input",
        kind="enum",
        keys=[None],
        address=_scalar_address(data.COUNTRY_CELLS),
        options=list(data.COUNTRY_AXIS.keys),
    ),
    _node(
        series_id="demography_scenario",
        role="input",
        kind="enum",
        keys=[None],
        address=_scalar_address(data.DEMOGRAPHY_SCENARIO_CELLS),
        options=["High", "Low", "Medium"],
    ),
    _node(
        series_id="productivity_start",
        role="input",
        kind="float",
        keys=[None],
        address=_scalar_address(data.PRODUCTIVITY_START_CELLS),
        domain=_domain(-100.0, 100.0),
    ),
    _node(
        series_id="productivity_end",
        role="input",
        kind="float",
        keys=[None],
        address=_scalar_address(data.PRODUCTIVITY_END_CELLS),
        domain=_domain(-100.0, 100.0),
    ),
    _node(
        series_id="inflation_start",
        role="input",
        kind="float",
        keys=[None],
        address=_scalar_address(data.INFLATION_START_CELLS),
        domain=_domain(-100.0, 100.0),
    ),
    _node(
        series_id="inflation_end",
        role="input",
        kind="float",
        keys=[None],
        address=_scalar_address(data.INFLATION_END_CELLS),
        domain=_domain(-100.0, 100.0),
    ),
    _node(
        series_id="interest_rate_mode",
        role="input",
        kind="enum",
        keys=[None],
        address=_scalar_address(data.INTEREST_RATE_MODE_CELLS),
        options=[
            "Interest-growth differential",
            "Nominal interest rate",
            "Real interest rate (a)",
        ],
    ),
    _node(
        series_id="real_interest_rate",
        role="input",
        kind="float",
        keys=[None],
        address=_scalar_address(data.REAL_INTEREST_RATE_CELLS),
        domain=_domain(-20.0, 20.0),
    ),
    _node(
        series_id="fiscal_rule_enabled",
        role="input",
        kind="enum",
        keys=[None],
        address=_scalar_address(data.FISCAL_RULE_ENABLED_CELLS),
        options=["No", "Yes"],
    ),
    _node(
        series_id="debt_target",
        role="input",
        kind="float",
        keys=[None],
        address=_scalar_address(data.DEBT_TARGET_CELLS),
        domain=_domain(0.0, 300.0),
    ),
    _node(
        series_id="expenditure_rigidity",
        role="input",
        kind="float",
        keys=[None],
        address=_scalar_address(data.EXPENDITURE_RIGIDITY_CELLS),
        domain=_domain(0.0, 1.0),
    ),
    _year_node(
        "productivity_growth",
        "internal",
        data.PRODUCTIVITY_GROWTH,
        domain=_domain(-20.0, 20.0),
    ),
    _year_node(
        "inflation_path",
        "internal",
        data.INFLATION_PATH,
        domain=_domain(-20.0, 40.0),
    ),
    _year_node(
        "baseline_interest_rate",
        "internal",
        data.BASELINE_INTEREST_RATE,
        domain=_domain(-5.0, 40.0),
    ),
    _year_node(
        "macrofiscal_debt_to_gdp",
        "internal",
        data.MACROFISCAL_DEBT_TO_GDP,
        domain=_domain(0.0, 400.0),
    ),
    _year_node(
        "demography_total_population",
        "internal",
        data.DEMOGRAPHY_TOTAL_POPULATION,
        domain=_domain(0.0, 1_000_000.0),
    ),
    _year_node(
        "climate_data_labour_productivity_growth_variation_paris",
        "internal",
        data.CLIMATE_DATA_LABOUR_PRODUCTIVITY_GROWTH_VARIATION_PARIS,
        domain=_domain(-5.0, 5.0),
    ),
    _year_node(
        "baseline_debt_to_gdp",
        "output",
        data.BASELINE_DEBT_TO_GDP,
        domain=_domain(0.0, 400.0),
    ),
    _year_node(
        "baseline_primary_balance_pct_gdp",
        "output",
        data.BASELINE_PRIMARY_BALANCE_PCT_GDP,
        domain=_domain(-50.0, 50.0),
    ),
    _year_node(
        "baseline_overall_balance_pct_gdp",
        "output",
        data.BASELINE_OVERALL_BALANCE_PCT_GDP,
        domain=_domain(-50.0, 50.0),
    ),
    _year_node(
        "baseline_real_gdp_growth",
        "output",
        data.BASELINE_REAL_GDP_GROWTH,
        domain=_domain(-20.0, 20.0),
    ),
    _year_node(
        "baseline_fiscal_consolidation_gap",
        "output",
        data.BASELINE_FISCAL_CONSOLIDATION_GAP,
        domain=_domain(-200.0, 200.0),
    ),
    _year_node(
        "paris_engine_gross_debt_pct_gdp",
        "internal",
        data.PARIS_ENGINE_GROSS_DEBT_PCT_GDP,
        domain=_domain(0.0, 400.0),
    ),
    _year_node(
        "hot_unadapted_engine_gross_debt_pct_gdp",
        "internal",
        data.HOT_UNADAPTED_ENGINE_GROSS_DEBT_PCT_GDP,
        domain=_domain(0.0, 400.0),
    ),
    _year_node(
        "output_scenarios_debt_to_gdp_summary_paris",
        "output",
        data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_PARIS,
        domain=_domain(0.0, 400.0),
    ),
    _year_node(
        "output_scenarios_debt_to_gdp_summary_hot_unadapted",
        "output",
        data.OUTPUT_SCENARIOS_DEBT_TO_GDP_SUMMARY_HOT_UNADAPTED,
        domain=_domain(0.0, 400.0),
    ),
)

NODES = _append_bound(NODES, "inputs.bindings.yaml", "input")
NODES = _append_bound(NODES, "internals.bindings.yaml", "internal")
NODES = _append_bound(NODES, "outputs.bindings.yaml", "output")
NODES_BY_ID: dict[str, dict[str, Any]] = {node["id"]: node for node in NODES}
SERIES_IDS = tuple(node["id"] for node in NODES)
VIZ_INPUT_IDS = tuple(node["id"] for node in NODES if node["role"] == "input")


def all_cell_addresses() -> tuple[str, ...]:
    addresses: list[str] = []
    for node in NODES:
        if "address" in node:
            addresses.append(node["address"])
        addresses.extend(node.get("addresses", {}).values())
    return tuple(dict.fromkeys(addresses))


def input_cell_writes(flat_inputs: Mapping[str, Any]) -> dict[str, Any]:
    """Map flat viz inputs to sheet-qualified leaf cells for FormulaEvaluator."""
    writes: dict[str, Any] = {}
    for series_id in VIZ_INPUT_IDS:
        node = NODES_BY_ID.get(series_id)
        if node is None:
            continue
        if "address" in node:
            writes[node["address"]] = flat_inputs[series_id]
            continue
        for key, address in node.get("addresses", {}).items():
            writes[address] = flat_inputs[series_id][key]
    return writes


__all__ = [
    "EDGES",
    "INPUT_IDS",
    "NODES",
    "NODES_BY_ID",
    "SERIES_IDS",
    "VIZ_INPUT_IDS",
    "BackendName",
    "_flat_addresses",
    "_node",
    "_scalar_address",
    "all_cell_addresses",
    "axes",
    "input_cell_writes",
]
