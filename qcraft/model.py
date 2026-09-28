"""Memoized evaluator and per-output input bundles."""

from __future__ import annotations

from dataclasses import Field, dataclass, fields
from dataclasses import field as _field
from functools import cached_property
from pathlib import Path
from typing import Annotated, Any, ClassVar, Literal, Self

from . import data, internals, validation
from .runtime import InputField, RealBetween, describe_inputs
from .workbook import read_bound_inputs


def _bind_inputs(target: object, inputs: dict[str, Any], *, validate: bool = True) -> None:
    if not validate:
        for name, value in inputs.items():
            setattr(target, name, value)
        return
    for name, value in inputs.items():
        check = validation.CHECKS.get(name)
        setattr(target, name, value if check is None else check(value))


class _BoundInputs:
    """Shared workbook bind and CHECKS validation for Model and input bundles."""

    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]
    _INPUT_IDS: tuple[str, ...] = ()

    @classmethod
    def from_workbook(cls, workbook: Path | str, **overrides: object) -> Self:
        """Bind input leaves from a populated workbook of this vintage."""
        declared = getattr(cls, "__dataclass_fields__", None)
        names = tuple(declared) if declared else cls._INPUT_IDS
        unknown = overrides.keys() - set(names)
        if unknown:
            raise TypeError(f"unknown inputs: {sorted(unknown)}")
        values = read_bound_inputs(Path(workbook), names, data)
        values.update(overrides)
        return cls(**values)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        holder = Model.__new__(Model)
        names = {field.name for field in fields(self)}
        values = {name: getattr(self, name) for name in names}
        _bind_inputs(holder, values)
        for name in names:
            object.__setattr__(self, name, getattr(holder, name))


class _SnapshotInputs(_BoundInputs):
    """Per-output bundle factory over `data.*_DEFAULT` leaves."""

    @classmethod
    def from_defaults(cls, **overrides: object) -> Self:
        names = {field.name for field in fields(cls)}
        unexpected = overrides.keys() - names
        if unexpected:
            listed = ", ".join(sorted(unexpected))
            raise TypeError(f"{cls.__name__}.from_defaults() got unknown argument(s): {listed}")
        values = {
            name: (
                overrides[name] if name in overrides else getattr(data, f"{name.upper()}_DEFAULT")
            )
            for name in names
        }
        return cls(**values)

    @classmethod
    def describe(cls) -> dict[str, InputField]:
        """Axes, keys, value annotation, default, and cells of each field."""
        return describe_inputs(cls)


class Model(_BoundInputs):
    """Formula series of the workbook, evaluated on demand from bound inputs.

    Each attribute evaluates its named formula once per model. Only the
    inputs bound at construction are available, so a public function
    supplies exactly the leaves of its output. Unknown constructor
    names fail closed. `from_defaults` binds every input from
    `data.*_DEFAULT`. `from_workbook` reads those input cells from a
    populated workbook of this vintage.
    """

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"]
    demography_scenario: Literal["High", "Low", "Medium"]
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)]
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)]
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)]
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)]
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"]
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)]
    fiscal_rule_enabled: Literal["No", "Yes"]
    debt_target: Annotated[float, RealBetween(0.0, 300.0)]
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)]
    discrete_revenue_shocks: data.DiscreteRevenueShocks
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks
    _INPUT_IDS: tuple[str, ...] = ("country", "demography_scenario", "productivity_start", "productivity_end", "inflation_start", "inflation_end", "interest_rate_mode", "real_interest_rate", "fiscal_rule_enabled", "debt_target", "expenditure_rigidity", "discrete_revenue_shocks", "discrete_primary_expenditure_shocks")

    def __init__(self, bundle: _BoundInputs | None = None, /, **inputs: Any) -> None:
        if bundle is not None:
            if not isinstance(bundle, _BoundInputs):
                raise TypeError(
                    f"Model() bundle must be a bound inputs instance, not {type(bundle).__name__}"
                )
            if inputs:
                raise TypeError("Model() does not accept keyword inputs with a bound bundle")
            values = {field.name: getattr(bundle, field.name) for field in fields(bundle)}
            _bind_inputs(self, values, validate=False)
            return
        unknown = inputs.keys() - {"country", "demography_scenario", "productivity_start", "productivity_end", "inflation_start", "inflation_end", "interest_rate_mode", "real_interest_rate", "fiscal_rule_enabled", "debt_target", "expenditure_rigidity", "discrete_revenue_shocks", "discrete_primary_expenditure_shocks"}
        if unknown:
            raise TypeError(f"unknown inputs: {sorted(unknown)}")
        _bind_inputs(self, inputs)

    @classmethod
    def from_defaults(
        cls,
        *,
        country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = data.COUNTRY_DEFAULT,
        demography_scenario: Literal["High", "Low", "Medium"] = data.DEMOGRAPHY_SCENARIO_DEFAULT,
        productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = data.PRODUCTIVITY_START_DEFAULT,
        productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = data.PRODUCTIVITY_END_DEFAULT,
        inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = data.INFLATION_START_DEFAULT,
        inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = data.INFLATION_END_DEFAULT,
        interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = data.INTEREST_RATE_MODE_DEFAULT,
        real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = data.REAL_INTEREST_RATE_DEFAULT,
        fiscal_rule_enabled: Literal["No", "Yes"] = data.FISCAL_RULE_ENABLED_DEFAULT,
        debt_target: Annotated[float, RealBetween(0.0, 300.0)] = data.DEBT_TARGET_DEFAULT,
        expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = data.EXPENDITURE_RIGIDITY_DEFAULT,
        discrete_revenue_shocks: data.DiscreteRevenueShocks = data.DISCRETE_REVENUE_SHOCKS_DEFAULT,
        discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT,
    ) -> Model:
        """Bind every input from `data.*_DEFAULT`, then apply overrides."""
        return cls(
            country=country,
            demography_scenario=demography_scenario,
            productivity_start=productivity_start,
            productivity_end=productivity_end,
            inflation_start=inflation_start,
            inflation_end=inflation_end,
            interest_rate_mode=interest_rate_mode,
            real_interest_rate=real_interest_rate,
            fiscal_rule_enabled=fiscal_rule_enabled,
            debt_target=debt_target,
            expenditure_rigidity=expenditure_rigidity,
            discrete_revenue_shocks=discrete_revenue_shocks,
            discrete_primary_expenditure_shocks=discrete_primary_expenditure_shocks,
        )

    @cached_property
    def baseline_engine_working_age_population(self) -> data.Series[float | str | None]:
        return internals.baseline_engine_working_age_population(demography_working_age_population=self.demography_working_age_population)

    @cached_property
    def baseline_engine_total_population(self) -> data.Series[float | str | None]:
        return internals.baseline_engine_total_population(demography_total_population=self.demography_total_population)

    @cached_property
    def _scan_baseline_engine_real_gdp_lcu(self) -> internals.ScanBaselineEngineRealGdpLcuResult:
        return internals.scan_baseline_engine_real_gdp_lcu(baseline_engine_working_age_population=self.baseline_engine_working_age_population, macrofiscal_real_gdp_lcu=self.macrofiscal_real_gdp_lcu, macrofiscal_real_gdp_growth=self.macrofiscal_real_gdp_growth, productivity_growth=self.productivity_growth)

    @cached_property
    def baseline_engine_real_gdp_lcu(self) -> data.Series[float | str | None]:
        return self._scan_baseline_engine_real_gdp_lcu.baseline_engine_real_gdp_lcu

    @cached_property
    def baseline_real_gdp_growth(self) -> data.BaselineRealGdpGrowth:
        return self._scan_baseline_engine_real_gdp_lcu.baseline_real_gdp_growth

    @cached_property
    def baseline_employment_growth(self) -> data.BaselineEmploymentGrowth:
        return self._scan_baseline_engine_real_gdp_lcu.baseline_employment_growth

    @cached_property
    def baseline_labour_productivity_growth(self) -> data.BaselineLabourProductivityGrowth:
        return self._scan_baseline_engine_real_gdp_lcu.baseline_labour_productivity_growth

    @cached_property
    def baseline_engine_nominal_gdp_lcu(self) -> data.Series[float | str | None]:
        return internals.baseline_engine_nominal_gdp_lcu(macrofiscal_nominal_gdp_lcu=self.macrofiscal_nominal_gdp_lcu, baseline_real_gdp_growth=self.baseline_real_gdp_growth, baseline_gdp_deflator_growth=self.baseline_gdp_deflator_growth)

    @cached_property
    def baseline_engine_revenue_lcu(self) -> data.Series[float | str | None]:
        return internals.baseline_engine_revenue_lcu(macrofiscal_revenue_lcu=self.macrofiscal_revenue_lcu, baseline_nominal_gdp_growth=self.baseline_nominal_gdp_growth)

    @cached_property
    def baseline_engine_primary_balance_lcu(self) -> data.Series[float | str | None]:
        return internals.baseline_engine_primary_balance_lcu(baseline_engine_revenue_lcu=self.baseline_engine_revenue_lcu, baseline_engine_primary_expenditure_lcu=self.baseline_engine_primary_expenditure_lcu, macrofiscal_primary_balance_lcu=self.macrofiscal_primary_balance_lcu)

    @cached_property
    def baseline_engine_overall_balance_lcu(self) -> data.Series[float | str | None]:
        return internals.baseline_engine_overall_balance_lcu(baseline_engine_revenue_lcu=self.baseline_engine_revenue_lcu, baseline_engine_total_expenditure_lcu=self.baseline_engine_total_expenditure_lcu, macrofiscal_overall_balance_lcu=self.macrofiscal_overall_balance_lcu)

    @cached_property
    def baseline_engine_interest_expenditure_pct_revenue(self) -> data.Series[float | str | None]:
        return internals.baseline_engine_interest_expenditure_pct_revenue(baseline_engine_revenue_lcu=self.baseline_engine_revenue_lcu, baseline_engine_interest_expenditure_lcu=self.baseline_engine_interest_expenditure_lcu)

    @cached_property
    def _scan_baseline_engine_total_expenditure_pct_gdp(self) -> internals.ScanBaselineEngineTotalExpenditurePctGdpResult:
        return internals.scan_baseline_engine_total_expenditure_pct_gdp(baseline_debt_direction_above_sentinel=data.BASELINE_DEBT_DIRECTION_ABOVE_SENTINEL, baseline_debt_direction_below_sentinel=data.BASELINE_DEBT_DIRECTION_BELOW_SENTINEL, baseline_engine_nominal_gdp_lcu=self.baseline_engine_nominal_gdp_lcu, baseline_fiscal_rule_flag=self.baseline_fiscal_rule_flag, baseline_debt_target_above=self.baseline_debt_target_above, baseline_debt_target_below=self.baseline_debt_target_below, macrofiscal_expenditure_lcu=self.macrofiscal_expenditure_lcu, macrofiscal_debt_lcu=self.macrofiscal_debt_lcu, macrofiscal_interest_expenditure_lcu=self.macrofiscal_interest_expenditure_lcu, macrofiscal_primary_expenditure_lcu=self.macrofiscal_primary_expenditure_lcu, macrofiscal_primary_expenditure_pct_gdp=self.macrofiscal_primary_expenditure_pct_gdp, macrofiscal_debt_to_gdp=self.macrofiscal_debt_to_gdp, macrofiscal_primary_balance_pct_gdp=self.macrofiscal_primary_balance_pct_gdp, baseline_interest_rate=self.baseline_interest_rate, baseline_nominal_gdp_growth=self.baseline_nominal_gdp_growth, baseline_revenue_pct_gdp=self.baseline_revenue_pct_gdp, baseline_labour_productivity_growth=self.baseline_labour_productivity_growth, baseline_gdp_deflator_growth=self.baseline_gdp_deflator_growth, baseline_population_growth=self.baseline_population_growth)

    @cached_property
    def baseline_engine_total_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return self._scan_baseline_engine_total_expenditure_pct_gdp.baseline_engine_total_expenditure_pct_gdp

    @cached_property
    def baseline_engine_total_expenditure_lcu(self) -> data.Series[float | str | None]:
        return self._scan_baseline_engine_total_expenditure_pct_gdp.baseline_engine_total_expenditure_lcu

    @cached_property
    def baseline_engine_interest_expenditure_lcu(self) -> data.Series[float | str | None]:
        return self._scan_baseline_engine_total_expenditure_pct_gdp.baseline_engine_interest_expenditure_lcu

    @cached_property
    def baseline_engine_primary_expenditure_lcu(self) -> data.Series[float | str | None]:
        return self._scan_baseline_engine_total_expenditure_pct_gdp.baseline_engine_primary_expenditure_lcu

    @cached_property
    def baseline_engine_gross_debt_lcu(self) -> data.Series[float | str | None]:
        return self._scan_baseline_engine_total_expenditure_pct_gdp.baseline_engine_gross_debt_lcu

    @cached_property
    def baseline_engine_fiscal_rule_adjustment(self) -> data.Series[float | str | None]:
        return self._scan_baseline_engine_total_expenditure_pct_gdp.baseline_engine_fiscal_rule_adjustment

    @cached_property
    def baseline_engine_debt_trajectory_direction(self) -> data.Series[float | str | None]:
        return self._scan_baseline_engine_total_expenditure_pct_gdp.baseline_engine_debt_trajectory_direction

    @cached_property
    def baseline_engine_fiscal_gap_above_target(self) -> data.Series[float | str | None]:
        return self._scan_baseline_engine_total_expenditure_pct_gdp.baseline_engine_fiscal_gap_above_target

    @cached_property
    def baseline_engine_fiscal_gap_below_target(self) -> data.Series[float | str | None]:
        return self._scan_baseline_engine_total_expenditure_pct_gdp.baseline_engine_fiscal_gap_below_target

    @cached_property
    def baseline_primary_expenditure_pct_gdp(self) -> data.BaselinePrimaryExpenditurePctGdp:
        return self._scan_baseline_engine_total_expenditure_pct_gdp.baseline_primary_expenditure_pct_gdp

    @cached_property
    def baseline_interest_expenditure_pct_gdp(self) -> data.BaselineInterestExpenditurePctGdp:
        return self._scan_baseline_engine_total_expenditure_pct_gdp.baseline_interest_expenditure_pct_gdp

    @cached_property
    def baseline_primary_balance_pct_gdp(self) -> data.BaselinePrimaryBalancePctGdp:
        return self._scan_baseline_engine_total_expenditure_pct_gdp.baseline_primary_balance_pct_gdp

    @cached_property
    def baseline_debt_to_gdp(self) -> data.BaselineDebtToGdp:
        return self._scan_baseline_engine_total_expenditure_pct_gdp.baseline_debt_to_gdp

    @cached_property
    def baseline_debt_stabilizing_primary_balance(self) -> data.BaselineDebtStabilizingPrimaryBalance:
        return self._scan_baseline_engine_total_expenditure_pct_gdp.baseline_debt_stabilizing_primary_balance

    @cached_property
    def baseline_fiscal_consolidation_gap(self) -> data.BaselineFiscalConsolidationGap:
        return self._scan_baseline_engine_total_expenditure_pct_gdp.baseline_fiscal_consolidation_gap

    @cached_property
    def baseline_fiscal_rule_flag(self) -> str | int | float | bool:
        return internals.baseline_fiscal_rule_flag(fiscal_rule_enabled=self.fiscal_rule_enabled)

    @cached_property
    def baseline_debt_target_above(self) -> float | str:
        return internals.baseline_debt_target_above(debt_target=self.debt_target)

    @cached_property
    def baseline_debt_target_below(self) -> float | str:
        return internals.baseline_debt_target_below(debt_target=self.debt_target)

    @cached_property
    def paris_engine_employment_growth(self) -> data.Series[float | str | None]:
        return internals.paris_engine_employment_growth(baseline_employment_growth=self.baseline_employment_growth)

    @cached_property
    def paris_engine_labour_productivity_growth(self) -> data.Series[float | str | None]:
        return internals.paris_engine_labour_productivity_growth(climate_data_labour_productivity_growth_variation_paris=self.climate_data_labour_productivity_growth_variation_paris, baseline_labour_productivity_growth=self.baseline_labour_productivity_growth)

    @cached_property
    def paris_engine_real_gdp_growth(self) -> data.Series[float | str | None]:
        return internals.paris_engine_real_gdp_growth(paris_engine_employment_growth=self.paris_engine_employment_growth, paris_engine_labour_productivity_growth=self.paris_engine_labour_productivity_growth)

    @cached_property
    def paris_engine_gdp_deflator_growth(self) -> data.Series[float | str | None]:
        return internals.paris_engine_gdp_deflator_growth(baseline_gdp_deflator_growth=self.baseline_gdp_deflator_growth)

    @cached_property
    def paris_engine_nominal_gdp_lcu(self) -> data.Series[float | str | None]:
        return internals.paris_engine_nominal_gdp_lcu(baseline_engine_nominal_gdp_lcu=self.baseline_engine_nominal_gdp_lcu, scenario_nominal_gdp_growth_paris=self.scenario_nominal_gdp_growth_paris)

    @cached_property
    def paris_engine_revenue_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.paris_engine_revenue_pct_gdp(paris_engine_discrete_risk_revenue_shock=self.paris_engine_discrete_risk_revenue_shock, baseline_revenue_pct_gdp=self.baseline_revenue_pct_gdp)

    @cached_property
    def paris_engine_overall_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.paris_engine_overall_balance_pct_gdp(paris_engine_revenue_pct_gdp=self.paris_engine_revenue_pct_gdp, paris_engine_total_expenditure_pct_gdp=self.paris_engine_total_expenditure_pct_gdp, baseline_overall_balance_pct_gdp=self.baseline_overall_balance_pct_gdp)

    @cached_property
    def paris_engine_revenue_lcu(self) -> data.Series[float | str | None]:
        return internals.paris_engine_revenue_lcu(baseline_engine_revenue_lcu=self.baseline_engine_revenue_lcu, paris_engine_nominal_gdp_lcu=self.paris_engine_nominal_gdp_lcu, paris_engine_revenue_pct_gdp=self.paris_engine_revenue_pct_gdp)

    @cached_property
    def paris_engine_primary_expenditure_lcu(self) -> data.Series[float | str | None]:
        return internals.paris_engine_primary_expenditure_lcu(expenditure_rigidity=self.expenditure_rigidity, baseline_engine_primary_expenditure_lcu=self.baseline_engine_primary_expenditure_lcu, paris_engine_nominal_gdp_lcu=self.paris_engine_nominal_gdp_lcu, paris_engine_discrete_risk_expenditure_shock=self.paris_engine_discrete_risk_expenditure_shock, paris_engine_recalibration_lcu=self.paris_engine_recalibration_lcu)

    @cached_property
    def paris_engine_primary_balance_lcu(self) -> data.Series[float | str | None]:
        return internals.paris_engine_primary_balance_lcu(baseline_engine_primary_balance_lcu=self.baseline_engine_primary_balance_lcu, paris_engine_revenue_lcu=self.paris_engine_revenue_lcu, paris_engine_primary_expenditure_lcu=self.paris_engine_primary_expenditure_lcu)

    @cached_property
    def paris_engine_overall_balance_lcu(self) -> data.Series[float | str | None]:
        return internals.paris_engine_overall_balance_lcu(baseline_engine_overall_balance_lcu=self.baseline_engine_overall_balance_lcu, paris_engine_revenue_lcu=self.paris_engine_revenue_lcu, paris_engine_total_expenditure_lcu=self.paris_engine_total_expenditure_lcu)

    @cached_property
    def paris_engine_weighted_interest_rate(self) -> data.Series[float | str | None]:
        return internals.paris_engine_weighted_interest_rate(baseline_interest_rate=self.baseline_interest_rate)

    @cached_property
    def paris_engine_interest_expenditure_pct_revenue(self) -> data.Series[float | str | None]:
        return internals.paris_engine_interest_expenditure_pct_revenue(paris_engine_revenue_lcu=self.paris_engine_revenue_lcu, paris_engine_interest_expenditure_lcu=self.paris_engine_interest_expenditure_lcu)

    @cached_property
    def paris_engine_discrete_risk_revenue_shock(self) -> data.Series[float | str | None]:
        return internals.paris_engine_discrete_risk_revenue_shock(discrete_revenue_shocks=self.discrete_revenue_shocks)

    @cached_property
    def paris_engine_discrete_risk_expenditure_shock(self) -> data.Series[float | str | None]:
        return internals.paris_engine_discrete_risk_expenditure_shock(discrete_primary_expenditure_shocks=self.discrete_primary_expenditure_shocks)

    @cached_property
    def paris_engine_memo_interest_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.paris_engine_memo_interest_expenditure_pct_gdp(baseline_interest_expenditure_pct_gdp=self.baseline_interest_expenditure_pct_gdp)

    @cached_property
    def paris_engine_memo_primary_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.paris_engine_memo_primary_expenditure_pct_gdp(baseline_primary_expenditure_pct_gdp=self.baseline_primary_expenditure_pct_gdp)

    @cached_property
    def paris_engine_memo_primary_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.paris_engine_memo_primary_balance_pct_gdp(baseline_primary_balance_pct_gdp=self.baseline_primary_balance_pct_gdp)

    @cached_property
    def paris_engine_memo_overall_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.paris_engine_memo_overall_balance_pct_gdp(baseline_overall_balance_pct_gdp=self.baseline_overall_balance_pct_gdp)

    @cached_property
    def paris_engine_memo_gross_debt_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.paris_engine_memo_gross_debt_pct_gdp(baseline_debt_to_gdp=self.baseline_debt_to_gdp)

    @cached_property
    def paris_engine_baseline_primary_expenditure_lcu(self) -> data.Series[float | str | None]:
        return internals.paris_engine_baseline_primary_expenditure_lcu(baseline_engine_primary_expenditure_lcu=self.baseline_engine_primary_expenditure_lcu)

    @cached_property
    def paris_engine_primary_expenditure_baseline_share_lcu(self) -> data.Series[float | str | None]:
        return internals.paris_engine_primary_expenditure_baseline_share_lcu(paris_engine_nominal_gdp_lcu=self.paris_engine_nominal_gdp_lcu, paris_engine_memo_primary_expenditure_pct_gdp=self.paris_engine_memo_primary_expenditure_pct_gdp)

    @cached_property
    def paris_engine_recalibration_lcu(self) -> data.Series[float | str | None]:
        return internals.paris_engine_recalibration_lcu(paris_engine_baseline_primary_expenditure_lcu=self.paris_engine_baseline_primary_expenditure_lcu, paris_engine_primary_expenditure_baseline_share_lcu=self.paris_engine_primary_expenditure_baseline_share_lcu)

    @cached_property
    def _scan_paris_engine_total_expenditure_pct_gdp(self) -> internals.ScanParisEngineTotalExpenditurePctGdpResult:
        return internals.scan_paris_engine_total_expenditure_pct_gdp(baseline_engine_total_expenditure_pct_gdp=self.baseline_engine_total_expenditure_pct_gdp, baseline_engine_total_expenditure_lcu=self.baseline_engine_total_expenditure_lcu, baseline_engine_interest_expenditure_lcu=self.baseline_engine_interest_expenditure_lcu, baseline_engine_gross_debt_lcu=self.baseline_engine_gross_debt_lcu, paris_engine_nominal_gdp_lcu=self.paris_engine_nominal_gdp_lcu, paris_engine_revenue_pct_gdp=self.paris_engine_revenue_pct_gdp, paris_engine_primary_expenditure_lcu=self.paris_engine_primary_expenditure_lcu, paris_engine_weighted_interest_rate=self.paris_engine_weighted_interest_rate, baseline_primary_expenditure_pct_gdp=self.baseline_primary_expenditure_pct_gdp, baseline_interest_expenditure_pct_gdp=self.baseline_interest_expenditure_pct_gdp, baseline_primary_balance_pct_gdp=self.baseline_primary_balance_pct_gdp, baseline_debt_to_gdp=self.baseline_debt_to_gdp, scenario_nominal_gdp_growth_paris=self.scenario_nominal_gdp_growth_paris)

    @cached_property
    def paris_engine_total_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return self._scan_paris_engine_total_expenditure_pct_gdp.paris_engine_total_expenditure_pct_gdp

    @cached_property
    def paris_engine_primary_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return self._scan_paris_engine_total_expenditure_pct_gdp.paris_engine_primary_balance_pct_gdp

    @cached_property
    def paris_engine_total_expenditure_lcu(self) -> data.Series[float | str | None]:
        return self._scan_paris_engine_total_expenditure_pct_gdp.paris_engine_total_expenditure_lcu

    @cached_property
    def paris_engine_interest_expenditure_lcu(self) -> data.Series[float | str | None]:
        return self._scan_paris_engine_total_expenditure_pct_gdp.paris_engine_interest_expenditure_lcu

    @cached_property
    def paris_engine_gross_debt_lcu(self) -> data.Series[float | str | None]:
        return self._scan_paris_engine_total_expenditure_pct_gdp.paris_engine_gross_debt_lcu

    @cached_property
    def paris_engine_gross_debt_pct_gdp(self) -> data.Series[float | str | None]:
        return self._scan_paris_engine_total_expenditure_pct_gdp.paris_engine_gross_debt_pct_gdp

    @cached_property
    def scenario_primary_expenditure_pct_gdp_paris(self) -> data.ScenarioPrimaryExpenditurePctGdpParis:
        return self._scan_paris_engine_total_expenditure_pct_gdp.scenario_primary_expenditure_pct_gdp_paris

    @cached_property
    def scenario_interest_expenditure_pct_gdp_paris(self) -> data.ScenarioInterestExpenditurePctGdpParis:
        return self._scan_paris_engine_total_expenditure_pct_gdp.scenario_interest_expenditure_pct_gdp_paris

    @cached_property
    def moderate_engine_employment_growth(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_employment_growth(baseline_employment_growth=self.baseline_employment_growth)

    @cached_property
    def moderate_engine_labour_productivity_growth(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_labour_productivity_growth(climate_data_labour_productivity_growth_variation_moderate=self.climate_data_labour_productivity_growth_variation_moderate, baseline_labour_productivity_growth=self.baseline_labour_productivity_growth)

    @cached_property
    def moderate_engine_real_gdp_growth(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_real_gdp_growth(moderate_engine_employment_growth=self.moderate_engine_employment_growth, moderate_engine_labour_productivity_growth=self.moderate_engine_labour_productivity_growth)

    @cached_property
    def moderate_engine_gdp_deflator_growth(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_gdp_deflator_growth(baseline_gdp_deflator_growth=self.baseline_gdp_deflator_growth)

    @cached_property
    def moderate_engine_nominal_gdp_lcu(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_nominal_gdp_lcu(baseline_engine_nominal_gdp_lcu=self.baseline_engine_nominal_gdp_lcu, scenario_nominal_gdp_growth_moderate=self.scenario_nominal_gdp_growth_moderate)

    @cached_property
    def moderate_engine_revenue_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_revenue_pct_gdp(moderate_engine_discrete_risk_revenue_shock=self.moderate_engine_discrete_risk_revenue_shock, baseline_revenue_pct_gdp=self.baseline_revenue_pct_gdp)

    @cached_property
    def moderate_engine_overall_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_overall_balance_pct_gdp(moderate_engine_revenue_pct_gdp=self.moderate_engine_revenue_pct_gdp, moderate_engine_total_expenditure_pct_gdp=self.moderate_engine_total_expenditure_pct_gdp, baseline_overall_balance_pct_gdp=self.baseline_overall_balance_pct_gdp)

    @cached_property
    def moderate_engine_revenue_lcu(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_revenue_lcu(baseline_engine_revenue_lcu=self.baseline_engine_revenue_lcu, moderate_engine_nominal_gdp_lcu=self.moderate_engine_nominal_gdp_lcu, moderate_engine_revenue_pct_gdp=self.moderate_engine_revenue_pct_gdp)

    @cached_property
    def moderate_engine_primary_expenditure_lcu(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_primary_expenditure_lcu(expenditure_rigidity=self.expenditure_rigidity, baseline_engine_primary_expenditure_lcu=self.baseline_engine_primary_expenditure_lcu, moderate_engine_nominal_gdp_lcu=self.moderate_engine_nominal_gdp_lcu, moderate_engine_discrete_risk_expenditure_shock=self.moderate_engine_discrete_risk_expenditure_shock, moderate_engine_recalibration_lcu=self.moderate_engine_recalibration_lcu)

    @cached_property
    def moderate_engine_primary_balance_lcu(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_primary_balance_lcu(baseline_engine_primary_balance_lcu=self.baseline_engine_primary_balance_lcu, moderate_engine_revenue_lcu=self.moderate_engine_revenue_lcu, moderate_engine_primary_expenditure_lcu=self.moderate_engine_primary_expenditure_lcu)

    @cached_property
    def moderate_engine_overall_balance_lcu(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_overall_balance_lcu(baseline_engine_overall_balance_lcu=self.baseline_engine_overall_balance_lcu, moderate_engine_revenue_lcu=self.moderate_engine_revenue_lcu, moderate_engine_total_expenditure_lcu=self.moderate_engine_total_expenditure_lcu)

    @cached_property
    def moderate_engine_weighted_interest_rate(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_weighted_interest_rate(baseline_interest_rate=self.baseline_interest_rate)

    @cached_property
    def moderate_engine_interest_expenditure_pct_revenue(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_interest_expenditure_pct_revenue(moderate_engine_revenue_lcu=self.moderate_engine_revenue_lcu, moderate_engine_interest_expenditure_lcu=self.moderate_engine_interest_expenditure_lcu)

    @cached_property
    def moderate_engine_discrete_risk_revenue_shock(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_discrete_risk_revenue_shock(discrete_revenue_shocks=self.discrete_revenue_shocks)

    @cached_property
    def moderate_engine_discrete_risk_expenditure_shock(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_discrete_risk_expenditure_shock(discrete_primary_expenditure_shocks=self.discrete_primary_expenditure_shocks)

    @cached_property
    def moderate_engine_memo_interest_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_memo_interest_expenditure_pct_gdp(baseline_interest_expenditure_pct_gdp=self.baseline_interest_expenditure_pct_gdp)

    @cached_property
    def moderate_engine_memo_primary_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_memo_primary_expenditure_pct_gdp(baseline_primary_expenditure_pct_gdp=self.baseline_primary_expenditure_pct_gdp)

    @cached_property
    def moderate_engine_memo_primary_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_memo_primary_balance_pct_gdp(baseline_primary_balance_pct_gdp=self.baseline_primary_balance_pct_gdp)

    @cached_property
    def moderate_engine_memo_overall_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_memo_overall_balance_pct_gdp(baseline_overall_balance_pct_gdp=self.baseline_overall_balance_pct_gdp)

    @cached_property
    def moderate_engine_memo_gross_debt_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_memo_gross_debt_pct_gdp(baseline_debt_to_gdp=self.baseline_debt_to_gdp)

    @cached_property
    def moderate_engine_baseline_primary_expenditure_lcu(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_baseline_primary_expenditure_lcu(baseline_engine_primary_expenditure_lcu=self.baseline_engine_primary_expenditure_lcu)

    @cached_property
    def moderate_engine_primary_expenditure_baseline_share_lcu(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_primary_expenditure_baseline_share_lcu(moderate_engine_nominal_gdp_lcu=self.moderate_engine_nominal_gdp_lcu, moderate_engine_memo_primary_expenditure_pct_gdp=self.moderate_engine_memo_primary_expenditure_pct_gdp)

    @cached_property
    def moderate_engine_recalibration_lcu(self) -> data.Series[float | str | None]:
        return internals.moderate_engine_recalibration_lcu(moderate_engine_baseline_primary_expenditure_lcu=self.moderate_engine_baseline_primary_expenditure_lcu, moderate_engine_primary_expenditure_baseline_share_lcu=self.moderate_engine_primary_expenditure_baseline_share_lcu)

    @cached_property
    def _scan_moderate_engine_total_expenditure_pct_gdp(self) -> internals.ScanModerateEngineTotalExpenditurePctGdpResult:
        return internals.scan_moderate_engine_total_expenditure_pct_gdp(baseline_engine_total_expenditure_pct_gdp=self.baseline_engine_total_expenditure_pct_gdp, baseline_engine_total_expenditure_lcu=self.baseline_engine_total_expenditure_lcu, baseline_engine_interest_expenditure_lcu=self.baseline_engine_interest_expenditure_lcu, baseline_engine_gross_debt_lcu=self.baseline_engine_gross_debt_lcu, moderate_engine_nominal_gdp_lcu=self.moderate_engine_nominal_gdp_lcu, moderate_engine_revenue_pct_gdp=self.moderate_engine_revenue_pct_gdp, moderate_engine_primary_expenditure_lcu=self.moderate_engine_primary_expenditure_lcu, moderate_engine_weighted_interest_rate=self.moderate_engine_weighted_interest_rate, baseline_primary_expenditure_pct_gdp=self.baseline_primary_expenditure_pct_gdp, baseline_interest_expenditure_pct_gdp=self.baseline_interest_expenditure_pct_gdp, baseline_primary_balance_pct_gdp=self.baseline_primary_balance_pct_gdp, baseline_debt_to_gdp=self.baseline_debt_to_gdp, scenario_nominal_gdp_growth_moderate=self.scenario_nominal_gdp_growth_moderate)

    @cached_property
    def moderate_engine_total_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return self._scan_moderate_engine_total_expenditure_pct_gdp.moderate_engine_total_expenditure_pct_gdp

    @cached_property
    def moderate_engine_primary_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return self._scan_moderate_engine_total_expenditure_pct_gdp.moderate_engine_primary_balance_pct_gdp

    @cached_property
    def moderate_engine_total_expenditure_lcu(self) -> data.Series[float | str | None]:
        return self._scan_moderate_engine_total_expenditure_pct_gdp.moderate_engine_total_expenditure_lcu

    @cached_property
    def moderate_engine_interest_expenditure_lcu(self) -> data.Series[float | str | None]:
        return self._scan_moderate_engine_total_expenditure_pct_gdp.moderate_engine_interest_expenditure_lcu

    @cached_property
    def moderate_engine_gross_debt_lcu(self) -> data.Series[float | str | None]:
        return self._scan_moderate_engine_total_expenditure_pct_gdp.moderate_engine_gross_debt_lcu

    @cached_property
    def moderate_engine_gross_debt_pct_gdp(self) -> data.Series[float | str | None]:
        return self._scan_moderate_engine_total_expenditure_pct_gdp.moderate_engine_gross_debt_pct_gdp

    @cached_property
    def scenario_primary_expenditure_pct_gdp_moderate(self) -> data.ScenarioPrimaryExpenditurePctGdpModerate:
        return self._scan_moderate_engine_total_expenditure_pct_gdp.scenario_primary_expenditure_pct_gdp_moderate

    @cached_property
    def scenario_interest_expenditure_pct_gdp_moderate(self) -> data.ScenarioInterestExpenditurePctGdpModerate:
        return self._scan_moderate_engine_total_expenditure_pct_gdp.scenario_interest_expenditure_pct_gdp_moderate

    @cached_property
    def high_engine_employment_growth(self) -> data.Series[float | str | None]:
        return internals.high_engine_employment_growth(baseline_employment_growth=self.baseline_employment_growth)

    @cached_property
    def high_engine_labour_productivity_growth(self) -> data.Series[float | str | None]:
        return internals.high_engine_labour_productivity_growth(climate_data_labour_productivity_growth_variation_high=self.climate_data_labour_productivity_growth_variation_high, baseline_labour_productivity_growth=self.baseline_labour_productivity_growth)

    @cached_property
    def high_engine_real_gdp_growth(self) -> data.Series[float | str | None]:
        return internals.high_engine_real_gdp_growth(high_engine_employment_growth=self.high_engine_employment_growth, high_engine_labour_productivity_growth=self.high_engine_labour_productivity_growth)

    @cached_property
    def high_engine_gdp_deflator_growth(self) -> data.Series[float | str | None]:
        return internals.high_engine_gdp_deflator_growth(baseline_gdp_deflator_growth=self.baseline_gdp_deflator_growth)

    @cached_property
    def high_engine_nominal_gdp_lcu(self) -> data.Series[float | str | None]:
        return internals.high_engine_nominal_gdp_lcu(baseline_engine_nominal_gdp_lcu=self.baseline_engine_nominal_gdp_lcu, scenario_nominal_gdp_growth_high=self.scenario_nominal_gdp_growth_high)

    @cached_property
    def high_engine_revenue_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.high_engine_revenue_pct_gdp(high_engine_discrete_risk_revenue_shock=self.high_engine_discrete_risk_revenue_shock, baseline_revenue_pct_gdp=self.baseline_revenue_pct_gdp)

    @cached_property
    def high_engine_overall_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.high_engine_overall_balance_pct_gdp(high_engine_revenue_pct_gdp=self.high_engine_revenue_pct_gdp, high_engine_total_expenditure_pct_gdp=self.high_engine_total_expenditure_pct_gdp, baseline_overall_balance_pct_gdp=self.baseline_overall_balance_pct_gdp)

    @cached_property
    def high_engine_revenue_lcu(self) -> data.Series[float | str | None]:
        return internals.high_engine_revenue_lcu(baseline_engine_revenue_lcu=self.baseline_engine_revenue_lcu, high_engine_nominal_gdp_lcu=self.high_engine_nominal_gdp_lcu, high_engine_revenue_pct_gdp=self.high_engine_revenue_pct_gdp)

    @cached_property
    def high_engine_primary_expenditure_lcu(self) -> data.Series[float | str | None]:
        return internals.high_engine_primary_expenditure_lcu(expenditure_rigidity=self.expenditure_rigidity, baseline_engine_primary_expenditure_lcu=self.baseline_engine_primary_expenditure_lcu, high_engine_nominal_gdp_lcu=self.high_engine_nominal_gdp_lcu, high_engine_discrete_risk_expenditure_shock=self.high_engine_discrete_risk_expenditure_shock, high_engine_recalibration_lcu=self.high_engine_recalibration_lcu)

    @cached_property
    def high_engine_primary_balance_lcu(self) -> data.Series[float | str | None]:
        return internals.high_engine_primary_balance_lcu(baseline_engine_primary_balance_lcu=self.baseline_engine_primary_balance_lcu, high_engine_revenue_lcu=self.high_engine_revenue_lcu, high_engine_primary_expenditure_lcu=self.high_engine_primary_expenditure_lcu)

    @cached_property
    def high_engine_overall_balance_lcu(self) -> data.Series[float | str | None]:
        return internals.high_engine_overall_balance_lcu(baseline_engine_overall_balance_lcu=self.baseline_engine_overall_balance_lcu, high_engine_revenue_lcu=self.high_engine_revenue_lcu, high_engine_total_expenditure_lcu=self.high_engine_total_expenditure_lcu)

    @cached_property
    def high_engine_weighted_interest_rate(self) -> data.Series[float | str | None]:
        return internals.high_engine_weighted_interest_rate(baseline_interest_rate=self.baseline_interest_rate)

    @cached_property
    def high_engine_interest_expenditure_pct_revenue(self) -> data.Series[float | str | None]:
        return internals.high_engine_interest_expenditure_pct_revenue(high_engine_revenue_lcu=self.high_engine_revenue_lcu, high_engine_interest_expenditure_lcu=self.high_engine_interest_expenditure_lcu)

    @cached_property
    def high_engine_discrete_risk_revenue_shock(self) -> data.Series[float | str | None]:
        return internals.high_engine_discrete_risk_revenue_shock(discrete_revenue_shocks=self.discrete_revenue_shocks)

    @cached_property
    def high_engine_discrete_risk_expenditure_shock(self) -> data.Series[float | str | None]:
        return internals.high_engine_discrete_risk_expenditure_shock(discrete_primary_expenditure_shocks=self.discrete_primary_expenditure_shocks)

    @cached_property
    def high_engine_memo_interest_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.high_engine_memo_interest_expenditure_pct_gdp(baseline_interest_expenditure_pct_gdp=self.baseline_interest_expenditure_pct_gdp)

    @cached_property
    def high_engine_memo_primary_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.high_engine_memo_primary_expenditure_pct_gdp(baseline_primary_expenditure_pct_gdp=self.baseline_primary_expenditure_pct_gdp)

    @cached_property
    def high_engine_memo_primary_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.high_engine_memo_primary_balance_pct_gdp(baseline_primary_balance_pct_gdp=self.baseline_primary_balance_pct_gdp)

    @cached_property
    def high_engine_memo_overall_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.high_engine_memo_overall_balance_pct_gdp(baseline_overall_balance_pct_gdp=self.baseline_overall_balance_pct_gdp)

    @cached_property
    def high_engine_memo_gross_debt_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.high_engine_memo_gross_debt_pct_gdp(baseline_debt_to_gdp=self.baseline_debt_to_gdp)

    @cached_property
    def high_engine_baseline_primary_expenditure_lcu(self) -> data.Series[float | str | None]:
        return internals.high_engine_baseline_primary_expenditure_lcu(baseline_engine_primary_expenditure_lcu=self.baseline_engine_primary_expenditure_lcu)

    @cached_property
    def high_engine_primary_expenditure_baseline_share_lcu(self) -> data.Series[float | str | None]:
        return internals.high_engine_primary_expenditure_baseline_share_lcu(high_engine_nominal_gdp_lcu=self.high_engine_nominal_gdp_lcu, high_engine_memo_primary_expenditure_pct_gdp=self.high_engine_memo_primary_expenditure_pct_gdp)

    @cached_property
    def high_engine_recalibration_lcu(self) -> data.Series[float | str | None]:
        return internals.high_engine_recalibration_lcu(high_engine_baseline_primary_expenditure_lcu=self.high_engine_baseline_primary_expenditure_lcu, high_engine_primary_expenditure_baseline_share_lcu=self.high_engine_primary_expenditure_baseline_share_lcu)

    @cached_property
    def _scan_high_engine_total_expenditure_pct_gdp(self) -> internals.ScanHighEngineTotalExpenditurePctGdpResult:
        return internals.scan_high_engine_total_expenditure_pct_gdp(baseline_engine_total_expenditure_pct_gdp=self.baseline_engine_total_expenditure_pct_gdp, baseline_engine_total_expenditure_lcu=self.baseline_engine_total_expenditure_lcu, baseline_engine_interest_expenditure_lcu=self.baseline_engine_interest_expenditure_lcu, baseline_engine_gross_debt_lcu=self.baseline_engine_gross_debt_lcu, high_engine_nominal_gdp_lcu=self.high_engine_nominal_gdp_lcu, high_engine_revenue_pct_gdp=self.high_engine_revenue_pct_gdp, high_engine_primary_expenditure_lcu=self.high_engine_primary_expenditure_lcu, high_engine_weighted_interest_rate=self.high_engine_weighted_interest_rate, baseline_primary_expenditure_pct_gdp=self.baseline_primary_expenditure_pct_gdp, baseline_interest_expenditure_pct_gdp=self.baseline_interest_expenditure_pct_gdp, baseline_primary_balance_pct_gdp=self.baseline_primary_balance_pct_gdp, baseline_debt_to_gdp=self.baseline_debt_to_gdp, scenario_nominal_gdp_growth_high=self.scenario_nominal_gdp_growth_high)

    @cached_property
    def high_engine_total_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return self._scan_high_engine_total_expenditure_pct_gdp.high_engine_total_expenditure_pct_gdp

    @cached_property
    def high_engine_primary_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return self._scan_high_engine_total_expenditure_pct_gdp.high_engine_primary_balance_pct_gdp

    @cached_property
    def high_engine_total_expenditure_lcu(self) -> data.Series[float | str | None]:
        return self._scan_high_engine_total_expenditure_pct_gdp.high_engine_total_expenditure_lcu

    @cached_property
    def high_engine_interest_expenditure_lcu(self) -> data.Series[float | str | None]:
        return self._scan_high_engine_total_expenditure_pct_gdp.high_engine_interest_expenditure_lcu

    @cached_property
    def high_engine_gross_debt_lcu(self) -> data.Series[float | str | None]:
        return self._scan_high_engine_total_expenditure_pct_gdp.high_engine_gross_debt_lcu

    @cached_property
    def high_engine_gross_debt_pct_gdp(self) -> data.Series[float | str | None]:
        return self._scan_high_engine_total_expenditure_pct_gdp.high_engine_gross_debt_pct_gdp

    @cached_property
    def scenario_primary_expenditure_pct_gdp_high(self) -> data.ScenarioPrimaryExpenditurePctGdpHigh:
        return self._scan_high_engine_total_expenditure_pct_gdp.scenario_primary_expenditure_pct_gdp_high

    @cached_property
    def scenario_interest_expenditure_pct_gdp_high(self) -> data.ScenarioInterestExpenditurePctGdpHigh:
        return self._scan_high_engine_total_expenditure_pct_gdp.scenario_interest_expenditure_pct_gdp_high

    @cached_property
    def hot_engine_employment_growth(self) -> data.Series[float | str | None]:
        return internals.hot_engine_employment_growth(baseline_employment_growth=self.baseline_employment_growth)

    @cached_property
    def hot_engine_labour_productivity_growth(self) -> data.Series[float | str | None]:
        return internals.hot_engine_labour_productivity_growth(climate_data_labour_productivity_growth_variation_hot=self.climate_data_labour_productivity_growth_variation_hot, baseline_labour_productivity_growth=self.baseline_labour_productivity_growth)

    @cached_property
    def hot_engine_real_gdp_growth(self) -> data.Series[float | str | None]:
        return internals.hot_engine_real_gdp_growth(hot_engine_employment_growth=self.hot_engine_employment_growth, hot_engine_labour_productivity_growth=self.hot_engine_labour_productivity_growth)

    @cached_property
    def hot_engine_gdp_deflator_growth(self) -> data.Series[float | str | None]:
        return internals.hot_engine_gdp_deflator_growth(baseline_gdp_deflator_growth=self.baseline_gdp_deflator_growth)

    @cached_property
    def hot_engine_nominal_gdp_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_engine_nominal_gdp_lcu(baseline_engine_nominal_gdp_lcu=self.baseline_engine_nominal_gdp_lcu, scenario_nominal_gdp_growth_hot=self.scenario_nominal_gdp_growth_hot)

    @cached_property
    def hot_engine_revenue_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_engine_revenue_pct_gdp(hot_engine_discrete_risk_revenue_shock=self.hot_engine_discrete_risk_revenue_shock, baseline_revenue_pct_gdp=self.baseline_revenue_pct_gdp)

    @cached_property
    def hot_engine_overall_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_engine_overall_balance_pct_gdp(hot_engine_revenue_pct_gdp=self.hot_engine_revenue_pct_gdp, hot_engine_total_expenditure_pct_gdp=self.hot_engine_total_expenditure_pct_gdp, baseline_overall_balance_pct_gdp=self.baseline_overall_balance_pct_gdp)

    @cached_property
    def hot_engine_revenue_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_engine_revenue_lcu(baseline_engine_revenue_lcu=self.baseline_engine_revenue_lcu, hot_engine_nominal_gdp_lcu=self.hot_engine_nominal_gdp_lcu, hot_engine_revenue_pct_gdp=self.hot_engine_revenue_pct_gdp)

    @cached_property
    def hot_engine_primary_expenditure_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_engine_primary_expenditure_lcu(expenditure_rigidity=self.expenditure_rigidity, baseline_engine_primary_expenditure_lcu=self.baseline_engine_primary_expenditure_lcu, hot_engine_nominal_gdp_lcu=self.hot_engine_nominal_gdp_lcu, hot_engine_discrete_risk_expenditure_shock=self.hot_engine_discrete_risk_expenditure_shock, hot_engine_recalibration_lcu=self.hot_engine_recalibration_lcu)

    @cached_property
    def hot_engine_primary_balance_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_engine_primary_balance_lcu(baseline_engine_primary_balance_lcu=self.baseline_engine_primary_balance_lcu, hot_engine_revenue_lcu=self.hot_engine_revenue_lcu, hot_engine_primary_expenditure_lcu=self.hot_engine_primary_expenditure_lcu)

    @cached_property
    def hot_engine_overall_balance_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_engine_overall_balance_lcu(baseline_engine_overall_balance_lcu=self.baseline_engine_overall_balance_lcu, hot_engine_revenue_lcu=self.hot_engine_revenue_lcu, hot_engine_total_expenditure_lcu=self.hot_engine_total_expenditure_lcu)

    @cached_property
    def hot_engine_weighted_interest_rate(self) -> data.Series[float | str | None]:
        return internals.hot_engine_weighted_interest_rate(baseline_interest_rate=self.baseline_interest_rate)

    @cached_property
    def hot_engine_interest_expenditure_pct_revenue(self) -> data.Series[float | str | None]:
        return internals.hot_engine_interest_expenditure_pct_revenue(hot_engine_revenue_lcu=self.hot_engine_revenue_lcu, hot_engine_interest_expenditure_lcu=self.hot_engine_interest_expenditure_lcu)

    @cached_property
    def hot_engine_discrete_risk_revenue_shock(self) -> data.Series[float | str | None]:
        return internals.hot_engine_discrete_risk_revenue_shock(discrete_revenue_shocks=self.discrete_revenue_shocks)

    @cached_property
    def hot_engine_discrete_risk_expenditure_shock(self) -> data.Series[float | str | None]:
        return internals.hot_engine_discrete_risk_expenditure_shock(discrete_primary_expenditure_shocks=self.discrete_primary_expenditure_shocks)

    @cached_property
    def hot_engine_memo_interest_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_engine_memo_interest_expenditure_pct_gdp(baseline_interest_expenditure_pct_gdp=self.baseline_interest_expenditure_pct_gdp)

    @cached_property
    def hot_engine_memo_primary_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_engine_memo_primary_expenditure_pct_gdp(baseline_primary_expenditure_pct_gdp=self.baseline_primary_expenditure_pct_gdp)

    @cached_property
    def hot_engine_memo_primary_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_engine_memo_primary_balance_pct_gdp(baseline_primary_balance_pct_gdp=self.baseline_primary_balance_pct_gdp)

    @cached_property
    def hot_engine_memo_overall_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_engine_memo_overall_balance_pct_gdp(baseline_overall_balance_pct_gdp=self.baseline_overall_balance_pct_gdp)

    @cached_property
    def hot_engine_memo_gross_debt_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_engine_memo_gross_debt_pct_gdp(baseline_debt_to_gdp=self.baseline_debt_to_gdp)

    @cached_property
    def hot_engine_baseline_primary_expenditure_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_engine_baseline_primary_expenditure_lcu(baseline_engine_primary_expenditure_lcu=self.baseline_engine_primary_expenditure_lcu)

    @cached_property
    def hot_engine_primary_expenditure_baseline_share_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_engine_primary_expenditure_baseline_share_lcu(hot_engine_nominal_gdp_lcu=self.hot_engine_nominal_gdp_lcu, hot_engine_memo_primary_expenditure_pct_gdp=self.hot_engine_memo_primary_expenditure_pct_gdp)

    @cached_property
    def hot_engine_recalibration_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_engine_recalibration_lcu(hot_engine_baseline_primary_expenditure_lcu=self.hot_engine_baseline_primary_expenditure_lcu, hot_engine_primary_expenditure_baseline_share_lcu=self.hot_engine_primary_expenditure_baseline_share_lcu)

    @cached_property
    def _scan_hot_engine_total_expenditure_pct_gdp(self) -> internals.ScanHotEngineTotalExpenditurePctGdpResult:
        return internals.scan_hot_engine_total_expenditure_pct_gdp(baseline_engine_total_expenditure_pct_gdp=self.baseline_engine_total_expenditure_pct_gdp, baseline_engine_total_expenditure_lcu=self.baseline_engine_total_expenditure_lcu, baseline_engine_interest_expenditure_lcu=self.baseline_engine_interest_expenditure_lcu, baseline_engine_gross_debt_lcu=self.baseline_engine_gross_debt_lcu, hot_engine_nominal_gdp_lcu=self.hot_engine_nominal_gdp_lcu, hot_engine_revenue_pct_gdp=self.hot_engine_revenue_pct_gdp, hot_engine_primary_expenditure_lcu=self.hot_engine_primary_expenditure_lcu, hot_engine_weighted_interest_rate=self.hot_engine_weighted_interest_rate, baseline_primary_expenditure_pct_gdp=self.baseline_primary_expenditure_pct_gdp, baseline_interest_expenditure_pct_gdp=self.baseline_interest_expenditure_pct_gdp, baseline_primary_balance_pct_gdp=self.baseline_primary_balance_pct_gdp, baseline_debt_to_gdp=self.baseline_debt_to_gdp, scenario_nominal_gdp_growth_hot=self.scenario_nominal_gdp_growth_hot)

    @cached_property
    def hot_engine_total_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return self._scan_hot_engine_total_expenditure_pct_gdp.hot_engine_total_expenditure_pct_gdp

    @cached_property
    def hot_engine_primary_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return self._scan_hot_engine_total_expenditure_pct_gdp.hot_engine_primary_balance_pct_gdp

    @cached_property
    def hot_engine_total_expenditure_lcu(self) -> data.Series[float | str | None]:
        return self._scan_hot_engine_total_expenditure_pct_gdp.hot_engine_total_expenditure_lcu

    @cached_property
    def hot_engine_interest_expenditure_lcu(self) -> data.Series[float | str | None]:
        return self._scan_hot_engine_total_expenditure_pct_gdp.hot_engine_interest_expenditure_lcu

    @cached_property
    def hot_engine_gross_debt_lcu(self) -> data.Series[float | str | None]:
        return self._scan_hot_engine_total_expenditure_pct_gdp.hot_engine_gross_debt_lcu

    @cached_property
    def hot_engine_gross_debt_pct_gdp(self) -> data.Series[float | str | None]:
        return self._scan_hot_engine_total_expenditure_pct_gdp.hot_engine_gross_debt_pct_gdp

    @cached_property
    def scenario_primary_expenditure_pct_gdp_hot(self) -> data.ScenarioPrimaryExpenditurePctGdpHot:
        return self._scan_hot_engine_total_expenditure_pct_gdp.scenario_primary_expenditure_pct_gdp_hot

    @cached_property
    def scenario_interest_expenditure_pct_gdp_hot(self) -> data.ScenarioInterestExpenditurePctGdpHot:
        return self._scan_hot_engine_total_expenditure_pct_gdp.scenario_interest_expenditure_pct_gdp_hot

    @cached_property
    def hot_adapted_engine_employment_growth(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_employment_growth(baseline_employment_growth=self.baseline_employment_growth)

    @cached_property
    def hot_adapted_engine_labour_productivity_growth(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_labour_productivity_growth(climate_data_labour_productivity_growth_variation_hot_adapted=self.climate_data_labour_productivity_growth_variation_hot_adapted, baseline_labour_productivity_growth=self.baseline_labour_productivity_growth)

    @cached_property
    def hot_adapted_engine_real_gdp_growth(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_real_gdp_growth(hot_adapted_engine_employment_growth=self.hot_adapted_engine_employment_growth, hot_adapted_engine_labour_productivity_growth=self.hot_adapted_engine_labour_productivity_growth)

    @cached_property
    def hot_adapted_engine_gdp_deflator_growth(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_gdp_deflator_growth(baseline_gdp_deflator_growth=self.baseline_gdp_deflator_growth)

    @cached_property
    def hot_adapted_engine_nominal_gdp_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_nominal_gdp_lcu(baseline_engine_nominal_gdp_lcu=self.baseline_engine_nominal_gdp_lcu, scenario_nominal_gdp_growth_hot_adapted=self.scenario_nominal_gdp_growth_hot_adapted)

    @cached_property
    def hot_adapted_engine_revenue_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_revenue_pct_gdp(hot_adapted_engine_discrete_risk_revenue_shock=self.hot_adapted_engine_discrete_risk_revenue_shock, baseline_revenue_pct_gdp=self.baseline_revenue_pct_gdp)

    @cached_property
    def hot_adapted_engine_overall_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_overall_balance_pct_gdp(hot_adapted_engine_revenue_pct_gdp=self.hot_adapted_engine_revenue_pct_gdp, hot_adapted_engine_total_expenditure_pct_gdp=self.hot_adapted_engine_total_expenditure_pct_gdp, baseline_overall_balance_pct_gdp=self.baseline_overall_balance_pct_gdp)

    @cached_property
    def hot_adapted_engine_revenue_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_revenue_lcu(baseline_engine_revenue_lcu=self.baseline_engine_revenue_lcu, hot_adapted_engine_nominal_gdp_lcu=self.hot_adapted_engine_nominal_gdp_lcu, hot_adapted_engine_revenue_pct_gdp=self.hot_adapted_engine_revenue_pct_gdp)

    @cached_property
    def hot_adapted_engine_primary_expenditure_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_primary_expenditure_lcu(expenditure_rigidity=self.expenditure_rigidity, baseline_engine_primary_expenditure_lcu=self.baseline_engine_primary_expenditure_lcu, hot_adapted_engine_nominal_gdp_lcu=self.hot_adapted_engine_nominal_gdp_lcu, hot_adapted_engine_discrete_risk_expenditure_shock=self.hot_adapted_engine_discrete_risk_expenditure_shock, hot_adapted_engine_recalibration_lcu=self.hot_adapted_engine_recalibration_lcu)

    @cached_property
    def hot_adapted_engine_primary_balance_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_primary_balance_lcu(baseline_engine_primary_balance_lcu=self.baseline_engine_primary_balance_lcu, hot_adapted_engine_revenue_lcu=self.hot_adapted_engine_revenue_lcu, hot_adapted_engine_primary_expenditure_lcu=self.hot_adapted_engine_primary_expenditure_lcu)

    @cached_property
    def hot_adapted_engine_overall_balance_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_overall_balance_lcu(baseline_engine_overall_balance_lcu=self.baseline_engine_overall_balance_lcu, hot_adapted_engine_revenue_lcu=self.hot_adapted_engine_revenue_lcu, hot_adapted_engine_total_expenditure_lcu=self.hot_adapted_engine_total_expenditure_lcu)

    @cached_property
    def hot_adapted_engine_weighted_interest_rate(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_weighted_interest_rate(baseline_interest_rate=self.baseline_interest_rate)

    @cached_property
    def hot_adapted_engine_interest_expenditure_pct_revenue(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_interest_expenditure_pct_revenue(hot_adapted_engine_revenue_lcu=self.hot_adapted_engine_revenue_lcu, hot_adapted_engine_interest_expenditure_lcu=self.hot_adapted_engine_interest_expenditure_lcu)

    @cached_property
    def hot_adapted_engine_discrete_risk_revenue_shock(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_discrete_risk_revenue_shock(discrete_revenue_shocks=self.discrete_revenue_shocks)

    @cached_property
    def hot_adapted_engine_discrete_risk_expenditure_shock(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_discrete_risk_expenditure_shock(discrete_primary_expenditure_shocks=self.discrete_primary_expenditure_shocks)

    @cached_property
    def hot_adapted_engine_memo_interest_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_memo_interest_expenditure_pct_gdp(baseline_interest_expenditure_pct_gdp=self.baseline_interest_expenditure_pct_gdp)

    @cached_property
    def hot_adapted_engine_memo_primary_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_memo_primary_expenditure_pct_gdp(baseline_primary_expenditure_pct_gdp=self.baseline_primary_expenditure_pct_gdp)

    @cached_property
    def hot_adapted_engine_memo_primary_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_memo_primary_balance_pct_gdp(baseline_primary_balance_pct_gdp=self.baseline_primary_balance_pct_gdp)

    @cached_property
    def hot_adapted_engine_memo_overall_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_memo_overall_balance_pct_gdp(baseline_overall_balance_pct_gdp=self.baseline_overall_balance_pct_gdp)

    @cached_property
    def hot_adapted_engine_memo_gross_debt_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_memo_gross_debt_pct_gdp(baseline_debt_to_gdp=self.baseline_debt_to_gdp)

    @cached_property
    def hot_adapted_engine_baseline_primary_expenditure_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_baseline_primary_expenditure_lcu(baseline_engine_primary_expenditure_lcu=self.baseline_engine_primary_expenditure_lcu)

    @cached_property
    def hot_adapted_engine_primary_expenditure_baseline_share_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_primary_expenditure_baseline_share_lcu(hot_adapted_engine_nominal_gdp_lcu=self.hot_adapted_engine_nominal_gdp_lcu, hot_adapted_engine_memo_primary_expenditure_pct_gdp=self.hot_adapted_engine_memo_primary_expenditure_pct_gdp)

    @cached_property
    def hot_adapted_engine_recalibration_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_adapted_engine_recalibration_lcu(hot_adapted_engine_baseline_primary_expenditure_lcu=self.hot_adapted_engine_baseline_primary_expenditure_lcu, hot_adapted_engine_primary_expenditure_baseline_share_lcu=self.hot_adapted_engine_primary_expenditure_baseline_share_lcu)

    @cached_property
    def _scan_hot_adapted_engine_total_expenditure_pct_gdp(self) -> internals.ScanHotAdaptedEngineTotalExpenditurePctGdpResult:
        return internals.scan_hot_adapted_engine_total_expenditure_pct_gdp(baseline_engine_total_expenditure_pct_gdp=self.baseline_engine_total_expenditure_pct_gdp, baseline_engine_total_expenditure_lcu=self.baseline_engine_total_expenditure_lcu, baseline_engine_interest_expenditure_lcu=self.baseline_engine_interest_expenditure_lcu, baseline_engine_gross_debt_lcu=self.baseline_engine_gross_debt_lcu, hot_adapted_engine_nominal_gdp_lcu=self.hot_adapted_engine_nominal_gdp_lcu, hot_adapted_engine_revenue_pct_gdp=self.hot_adapted_engine_revenue_pct_gdp, hot_adapted_engine_primary_expenditure_lcu=self.hot_adapted_engine_primary_expenditure_lcu, hot_adapted_engine_weighted_interest_rate=self.hot_adapted_engine_weighted_interest_rate, baseline_primary_expenditure_pct_gdp=self.baseline_primary_expenditure_pct_gdp, baseline_interest_expenditure_pct_gdp=self.baseline_interest_expenditure_pct_gdp, baseline_primary_balance_pct_gdp=self.baseline_primary_balance_pct_gdp, baseline_debt_to_gdp=self.baseline_debt_to_gdp, scenario_nominal_gdp_growth_hot_adapted=self.scenario_nominal_gdp_growth_hot_adapted)

    @cached_property
    def hot_adapted_engine_total_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return self._scan_hot_adapted_engine_total_expenditure_pct_gdp.hot_adapted_engine_total_expenditure_pct_gdp

    @cached_property
    def hot_adapted_engine_primary_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return self._scan_hot_adapted_engine_total_expenditure_pct_gdp.hot_adapted_engine_primary_balance_pct_gdp

    @cached_property
    def hot_adapted_engine_total_expenditure_lcu(self) -> data.Series[float | str | None]:
        return self._scan_hot_adapted_engine_total_expenditure_pct_gdp.hot_adapted_engine_total_expenditure_lcu

    @cached_property
    def hot_adapted_engine_interest_expenditure_lcu(self) -> data.Series[float | str | None]:
        return self._scan_hot_adapted_engine_total_expenditure_pct_gdp.hot_adapted_engine_interest_expenditure_lcu

    @cached_property
    def hot_adapted_engine_gross_debt_lcu(self) -> data.Series[float | str | None]:
        return self._scan_hot_adapted_engine_total_expenditure_pct_gdp.hot_adapted_engine_gross_debt_lcu

    @cached_property
    def hot_adapted_engine_gross_debt_pct_gdp(self) -> data.Series[float | str | None]:
        return self._scan_hot_adapted_engine_total_expenditure_pct_gdp.hot_adapted_engine_gross_debt_pct_gdp

    @cached_property
    def scenario_primary_expenditure_pct_gdp_hot_adapted(self) -> data.ScenarioPrimaryExpenditurePctGdpHotAdapted:
        return self._scan_hot_adapted_engine_total_expenditure_pct_gdp.scenario_primary_expenditure_pct_gdp_hot_adapted

    @cached_property
    def scenario_interest_expenditure_pct_gdp_hot_adapted(self) -> data.ScenarioInterestExpenditurePctGdpHotAdapted:
        return self._scan_hot_adapted_engine_total_expenditure_pct_gdp.scenario_interest_expenditure_pct_gdp_hot_adapted

    @cached_property
    def hot_unadapted_engine_employment_growth(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_employment_growth(baseline_employment_growth=self.baseline_employment_growth)

    @cached_property
    def hot_unadapted_engine_labour_productivity_growth(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_labour_productivity_growth(climate_data_labour_productivity_growth_variation_hot_unadapted=self.climate_data_labour_productivity_growth_variation_hot_unadapted, baseline_labour_productivity_growth=self.baseline_labour_productivity_growth)

    @cached_property
    def hot_unadapted_engine_real_gdp_growth(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_real_gdp_growth(hot_unadapted_engine_employment_growth=self.hot_unadapted_engine_employment_growth, hot_unadapted_engine_labour_productivity_growth=self.hot_unadapted_engine_labour_productivity_growth)

    @cached_property
    def hot_unadapted_engine_gdp_deflator_growth(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_gdp_deflator_growth(baseline_gdp_deflator_growth=self.baseline_gdp_deflator_growth)

    @cached_property
    def hot_unadapted_engine_nominal_gdp_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_nominal_gdp_lcu(baseline_engine_nominal_gdp_lcu=self.baseline_engine_nominal_gdp_lcu, scenario_nominal_gdp_growth_hot_unadapted=self.scenario_nominal_gdp_growth_hot_unadapted)

    @cached_property
    def hot_unadapted_engine_revenue_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_revenue_pct_gdp(hot_unadapted_engine_discrete_risk_revenue_shock=self.hot_unadapted_engine_discrete_risk_revenue_shock, baseline_revenue_pct_gdp=self.baseline_revenue_pct_gdp)

    @cached_property
    def hot_unadapted_engine_overall_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_overall_balance_pct_gdp(hot_unadapted_engine_revenue_pct_gdp=self.hot_unadapted_engine_revenue_pct_gdp, hot_unadapted_engine_total_expenditure_pct_gdp=self.hot_unadapted_engine_total_expenditure_pct_gdp, baseline_overall_balance_pct_gdp=self.baseline_overall_balance_pct_gdp)

    @cached_property
    def hot_unadapted_engine_revenue_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_revenue_lcu(baseline_engine_revenue_lcu=self.baseline_engine_revenue_lcu, hot_unadapted_engine_nominal_gdp_lcu=self.hot_unadapted_engine_nominal_gdp_lcu, hot_unadapted_engine_revenue_pct_gdp=self.hot_unadapted_engine_revenue_pct_gdp)

    @cached_property
    def hot_unadapted_engine_primary_expenditure_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_primary_expenditure_lcu(expenditure_rigidity=self.expenditure_rigidity, baseline_engine_primary_expenditure_lcu=self.baseline_engine_primary_expenditure_lcu, hot_unadapted_engine_nominal_gdp_lcu=self.hot_unadapted_engine_nominal_gdp_lcu, hot_unadapted_engine_discrete_risk_expenditure_shock=self.hot_unadapted_engine_discrete_risk_expenditure_shock, hot_unadapted_engine_recalibration_lcu=self.hot_unadapted_engine_recalibration_lcu)

    @cached_property
    def hot_unadapted_engine_primary_balance_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_primary_balance_lcu(baseline_engine_primary_balance_lcu=self.baseline_engine_primary_balance_lcu, hot_unadapted_engine_revenue_lcu=self.hot_unadapted_engine_revenue_lcu, hot_unadapted_engine_primary_expenditure_lcu=self.hot_unadapted_engine_primary_expenditure_lcu)

    @cached_property
    def hot_unadapted_engine_overall_balance_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_overall_balance_lcu(baseline_engine_overall_balance_lcu=self.baseline_engine_overall_balance_lcu, hot_unadapted_engine_revenue_lcu=self.hot_unadapted_engine_revenue_lcu, hot_unadapted_engine_total_expenditure_lcu=self.hot_unadapted_engine_total_expenditure_lcu)

    @cached_property
    def hot_unadapted_engine_weighted_interest_rate(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_weighted_interest_rate(baseline_interest_rate=self.baseline_interest_rate)

    @cached_property
    def hot_unadapted_engine_interest_expenditure_pct_revenue(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_interest_expenditure_pct_revenue(hot_unadapted_engine_revenue_lcu=self.hot_unadapted_engine_revenue_lcu, hot_unadapted_engine_interest_expenditure_lcu=self.hot_unadapted_engine_interest_expenditure_lcu)

    @cached_property
    def hot_unadapted_engine_discrete_risk_revenue_shock(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_discrete_risk_revenue_shock(discrete_revenue_shocks=self.discrete_revenue_shocks)

    @cached_property
    def hot_unadapted_engine_discrete_risk_expenditure_shock(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_discrete_risk_expenditure_shock(discrete_primary_expenditure_shocks=self.discrete_primary_expenditure_shocks)

    @cached_property
    def hot_unadapted_engine_memo_interest_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_memo_interest_expenditure_pct_gdp(baseline_interest_expenditure_pct_gdp=self.baseline_interest_expenditure_pct_gdp)

    @cached_property
    def hot_unadapted_engine_memo_primary_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_memo_primary_expenditure_pct_gdp(baseline_primary_expenditure_pct_gdp=self.baseline_primary_expenditure_pct_gdp)

    @cached_property
    def hot_unadapted_engine_memo_primary_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_memo_primary_balance_pct_gdp(baseline_primary_balance_pct_gdp=self.baseline_primary_balance_pct_gdp)

    @cached_property
    def hot_unadapted_engine_memo_overall_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_memo_overall_balance_pct_gdp(baseline_overall_balance_pct_gdp=self.baseline_overall_balance_pct_gdp)

    @cached_property
    def hot_unadapted_engine_memo_gross_debt_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_memo_gross_debt_pct_gdp(baseline_debt_to_gdp=self.baseline_debt_to_gdp)

    @cached_property
    def hot_unadapted_engine_baseline_primary_expenditure_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_baseline_primary_expenditure_lcu(baseline_engine_primary_expenditure_lcu=self.baseline_engine_primary_expenditure_lcu)

    @cached_property
    def hot_unadapted_engine_primary_expenditure_baseline_share_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_primary_expenditure_baseline_share_lcu(hot_unadapted_engine_nominal_gdp_lcu=self.hot_unadapted_engine_nominal_gdp_lcu, hot_unadapted_engine_memo_primary_expenditure_pct_gdp=self.hot_unadapted_engine_memo_primary_expenditure_pct_gdp)

    @cached_property
    def hot_unadapted_engine_recalibration_lcu(self) -> data.Series[float | str | None]:
        return internals.hot_unadapted_engine_recalibration_lcu(hot_unadapted_engine_baseline_primary_expenditure_lcu=self.hot_unadapted_engine_baseline_primary_expenditure_lcu, hot_unadapted_engine_primary_expenditure_baseline_share_lcu=self.hot_unadapted_engine_primary_expenditure_baseline_share_lcu)

    @cached_property
    def _scan_hot_unadapted_engine_total_expenditure_pct_gdp(self) -> internals.ScanHotUnadaptedEngineTotalExpenditurePctGdpResult:
        return internals.scan_hot_unadapted_engine_total_expenditure_pct_gdp(baseline_engine_total_expenditure_pct_gdp=self.baseline_engine_total_expenditure_pct_gdp, baseline_engine_total_expenditure_lcu=self.baseline_engine_total_expenditure_lcu, baseline_engine_interest_expenditure_lcu=self.baseline_engine_interest_expenditure_lcu, baseline_engine_gross_debt_lcu=self.baseline_engine_gross_debt_lcu, hot_unadapted_engine_nominal_gdp_lcu=self.hot_unadapted_engine_nominal_gdp_lcu, hot_unadapted_engine_revenue_pct_gdp=self.hot_unadapted_engine_revenue_pct_gdp, hot_unadapted_engine_primary_expenditure_lcu=self.hot_unadapted_engine_primary_expenditure_lcu, hot_unadapted_engine_weighted_interest_rate=self.hot_unadapted_engine_weighted_interest_rate, baseline_primary_expenditure_pct_gdp=self.baseline_primary_expenditure_pct_gdp, baseline_interest_expenditure_pct_gdp=self.baseline_interest_expenditure_pct_gdp, baseline_primary_balance_pct_gdp=self.baseline_primary_balance_pct_gdp, baseline_debt_to_gdp=self.baseline_debt_to_gdp, scenario_nominal_gdp_growth_hot_unadapted=self.scenario_nominal_gdp_growth_hot_unadapted)

    @cached_property
    def hot_unadapted_engine_total_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return self._scan_hot_unadapted_engine_total_expenditure_pct_gdp.hot_unadapted_engine_total_expenditure_pct_gdp

    @cached_property
    def hot_unadapted_engine_primary_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return self._scan_hot_unadapted_engine_total_expenditure_pct_gdp.hot_unadapted_engine_primary_balance_pct_gdp

    @cached_property
    def hot_unadapted_engine_total_expenditure_lcu(self) -> data.Series[float | str | None]:
        return self._scan_hot_unadapted_engine_total_expenditure_pct_gdp.hot_unadapted_engine_total_expenditure_lcu

    @cached_property
    def hot_unadapted_engine_interest_expenditure_lcu(self) -> data.Series[float | str | None]:
        return self._scan_hot_unadapted_engine_total_expenditure_pct_gdp.hot_unadapted_engine_interest_expenditure_lcu

    @cached_property
    def hot_unadapted_engine_gross_debt_lcu(self) -> data.Series[float | str | None]:
        return self._scan_hot_unadapted_engine_total_expenditure_pct_gdp.hot_unadapted_engine_gross_debt_lcu

    @cached_property
    def hot_unadapted_engine_gross_debt_pct_gdp(self) -> data.Series[float | str | None]:
        return self._scan_hot_unadapted_engine_total_expenditure_pct_gdp.hot_unadapted_engine_gross_debt_pct_gdp

    @cached_property
    def scenario_primary_expenditure_pct_gdp_hot_unadapted(self) -> data.ScenarioPrimaryExpenditurePctGdpHotUnadapted:
        return self._scan_hot_unadapted_engine_total_expenditure_pct_gdp.scenario_primary_expenditure_pct_gdp_hot_unadapted

    @cached_property
    def scenario_interest_expenditure_pct_gdp_hot_unadapted(self) -> data.ScenarioInterestExpenditurePctGdpHotUnadapted:
        return self._scan_hot_unadapted_engine_total_expenditure_pct_gdp.scenario_interest_expenditure_pct_gdp_hot_unadapted

    @cached_property
    def output_baseline_primary_expenditure_pct_gdp_summary(self) -> data.Series[float | str | None]:
        return internals.output_baseline_primary_expenditure_pct_gdp_summary(output_baseline_primary_expenditure_pct_gdp_path=self.output_baseline_primary_expenditure_pct_gdp_path)

    @cached_property
    def output_baseline_interest_expenditure_pct_gdp_summary(self) -> data.Series[float | str | None]:
        return internals.output_baseline_interest_expenditure_pct_gdp_summary(output_baseline_interest_expenditure_pct_gdp_path=self.output_baseline_interest_expenditure_pct_gdp_path)

    @cached_property
    def output_baseline_interest_rate_summary(self) -> data.Series[float | str | None]:
        return internals.output_baseline_interest_rate_summary(output_baseline_interest_rate_path=self.output_baseline_interest_rate_path)

    @cached_property
    def output_baseline_primary_balance_pct_gdp_summary(self) -> data.Series[float | str | None]:
        return internals.output_baseline_primary_balance_pct_gdp_summary(output_baseline_primary_balance_pct_gdp_path=self.output_baseline_primary_balance_pct_gdp_path)

    @cached_property
    def output_baseline_overall_balance_pct_gdp_summary(self) -> data.Series[float | str | None]:
        return internals.output_baseline_overall_balance_pct_gdp_summary(output_baseline_overall_balance_pct_gdp_path=self.output_baseline_overall_balance_pct_gdp_path)

    @cached_property
    def output_baseline_debt_to_gdp_summary(self) -> data.Series[float | str | None]:
        return internals.output_baseline_debt_to_gdp_summary(output_baseline_debt_to_gdp_path=self.output_baseline_debt_to_gdp_path)

    @cached_property
    def output_baseline_dspb_milestones_pb(self) -> data.Series[float | str | None]:
        return internals.output_baseline_dspb_milestones_pb(output_baseline_primary_balance_pct_gdp_summary=self.output_baseline_primary_balance_pct_gdp_summary)

    @cached_property
    def output_baseline_dspb_milestones_pb_star(self) -> data.Series[float | str | None]:
        return internals.output_baseline_dspb_milestones_pb_star(baseline_debt_stabilizing_primary_balance=self.baseline_debt_stabilizing_primary_balance)

    @cached_property
    def output_baseline_dspb_milestones_pb_gap(self) -> data.Series[float | str | None]:
        return internals.output_baseline_dspb_milestones_pb_gap(output_baseline_dspb_milestones_pb=self.output_baseline_dspb_milestones_pb, output_baseline_dspb_milestones_pb_star=self.output_baseline_dspb_milestones_pb_star)

    @cached_property
    def output_baseline_primary_expenditure_pct_gdp_path(self) -> data.Series[float | str | None]:
        return internals.output_baseline_primary_expenditure_pct_gdp_path(baseline_primary_expenditure_pct_gdp=self.baseline_primary_expenditure_pct_gdp)

    @cached_property
    def output_baseline_interest_expenditure_pct_gdp_path(self) -> data.Series[float | str | None]:
        return internals.output_baseline_interest_expenditure_pct_gdp_path(baseline_interest_expenditure_pct_gdp=self.baseline_interest_expenditure_pct_gdp)

    @cached_property
    def output_baseline_interest_rate_path(self) -> data.Series[float | str | None]:
        return internals.output_baseline_interest_rate_path(baseline_interest_rate=self.baseline_interest_rate)

    @cached_property
    def output_baseline_primary_balance_pct_gdp_path(self) -> data.Series[float | str | None]:
        return internals.output_baseline_primary_balance_pct_gdp_path(baseline_primary_balance_pct_gdp=self.baseline_primary_balance_pct_gdp)

    @cached_property
    def output_baseline_overall_balance_pct_gdp_path(self) -> data.Series[float | str | None]:
        return internals.output_baseline_overall_balance_pct_gdp_path(baseline_overall_balance_pct_gdp=self.baseline_overall_balance_pct_gdp)

    @cached_property
    def output_baseline_debt_to_gdp_path(self) -> data.Series[float | str | None]:
        return internals.output_baseline_debt_to_gdp_path(baseline_debt_to_gdp=self.baseline_debt_to_gdp)

    @cached_property
    def output_scenarios_primary_balance_pct_gdp_summary_baseline(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_primary_balance_pct_gdp_summary_baseline(output_scenarios_primary_balance_pct_gdp_baseline_path=self.output_scenarios_primary_balance_pct_gdp_baseline_path)

    @cached_property
    def output_scenarios_primary_balance_pct_gdp_summary_paris(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_primary_balance_pct_gdp_summary_paris(scenario_primary_balance_pct_gdp=self.scenario_primary_balance_pct_gdp)

    @cached_property
    def output_scenarios_primary_balance_pct_gdp_summary_moderate(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_primary_balance_pct_gdp_summary_moderate(scenario_primary_balance_pct_gdp=self.scenario_primary_balance_pct_gdp)

    @cached_property
    def output_scenarios_primary_balance_pct_gdp_summary_high(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_primary_balance_pct_gdp_summary_high(scenario_primary_balance_pct_gdp=self.scenario_primary_balance_pct_gdp)

    @cached_property
    def output_scenarios_primary_balance_pct_gdp_summary_hot(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_primary_balance_pct_gdp_summary_hot(scenario_primary_balance_pct_gdp=self.scenario_primary_balance_pct_gdp)

    @cached_property
    def output_scenarios_primary_balance_pct_gdp_summary_hot_adapted(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_primary_balance_pct_gdp_summary_hot_adapted(scenario_primary_balance_pct_gdp=self.scenario_primary_balance_pct_gdp)

    @cached_property
    def output_scenarios_primary_balance_pct_gdp_summary_hot_unadapted(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_primary_balance_pct_gdp_summary_hot_unadapted(scenario_primary_balance_pct_gdp=self.scenario_primary_balance_pct_gdp)

    @cached_property
    def output_scenarios_debt_to_gdp_summary_baseline(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_debt_to_gdp_summary_baseline(output_scenarios_debt_to_gdp_baseline_path=self.output_scenarios_debt_to_gdp_baseline_path)

    @cached_property
    def output_scenarios_debt_to_gdp_summary_paris(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_debt_to_gdp_summary_paris(scenario_debt_to_gdp=self.scenario_debt_to_gdp)

    @cached_property
    def output_scenarios_debt_to_gdp_summary_moderate(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_debt_to_gdp_summary_moderate(scenario_debt_to_gdp=self.scenario_debt_to_gdp)

    @cached_property
    def output_scenarios_debt_to_gdp_summary_high(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_debt_to_gdp_summary_high(scenario_debt_to_gdp=self.scenario_debt_to_gdp)

    @cached_property
    def output_scenarios_debt_to_gdp_summary_hot(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_debt_to_gdp_summary_hot(scenario_debt_to_gdp=self.scenario_debt_to_gdp)

    @cached_property
    def output_scenarios_debt_to_gdp_summary_hot_adapted(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_debt_to_gdp_summary_hot_adapted(scenario_debt_to_gdp=self.scenario_debt_to_gdp)

    @cached_property
    def output_scenarios_debt_to_gdp_summary_hot_unadapted(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_debt_to_gdp_summary_hot_unadapted(scenario_debt_to_gdp=self.scenario_debt_to_gdp)

    @cached_property
    def output_scenarios_dspb_milestones_baseline_pb(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_dspb_milestones_baseline_pb(output_scenarios_primary_balance_pct_gdp_summary_baseline=self.output_scenarios_primary_balance_pct_gdp_summary_baseline)

    @cached_property
    def output_scenarios_dspb_milestones_baseline_pb_star(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_dspb_milestones_baseline_pb_star(baseline_debt_stabilizing_primary_balance=self.baseline_debt_stabilizing_primary_balance)

    @cached_property
    def output_scenarios_dspb_milestones_baseline_pb_gap(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_dspb_milestones_baseline_pb_gap(output_scenarios_dspb_milestones_baseline_pb=self.output_scenarios_dspb_milestones_baseline_pb, output_scenarios_dspb_milestones_baseline_pb_star=self.output_scenarios_dspb_milestones_baseline_pb_star)

    @cached_property
    def output_scenarios_dspb_milestones_paris_pb(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_dspb_milestones_paris_pb(output_scenarios_primary_balance_pct_gdp_summary_paris=self.output_scenarios_primary_balance_pct_gdp_summary_paris)

    @cached_property
    def output_scenarios_dspb_milestones_paris_pb_star(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_dspb_milestones_paris_pb_star(scenario_debt_stabilizing_primary_balance_paris=self.scenario_debt_stabilizing_primary_balance_paris)

    @cached_property
    def output_scenarios_dspb_milestones_moderate_pb(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_dspb_milestones_moderate_pb(output_scenarios_primary_balance_pct_gdp_summary_moderate=self.output_scenarios_primary_balance_pct_gdp_summary_moderate)

    @cached_property
    def output_scenarios_dspb_milestones_moderate_pb_star(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_dspb_milestones_moderate_pb_star(scenario_debt_stabilizing_primary_balance_moderate=self.scenario_debt_stabilizing_primary_balance_moderate)

    @cached_property
    def output_scenarios_dspb_milestones_high_pb(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_dspb_milestones_high_pb(output_scenarios_primary_balance_pct_gdp_summary_high=self.output_scenarios_primary_balance_pct_gdp_summary_high)

    @cached_property
    def output_scenarios_dspb_milestones_high_pb_star(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_dspb_milestones_high_pb_star(scenario_debt_stabilizing_primary_balance_high=self.scenario_debt_stabilizing_primary_balance_high)

    @cached_property
    def output_scenarios_dspb_milestones_hot_pb(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_dspb_milestones_hot_pb(output_scenarios_primary_balance_pct_gdp_summary_hot=self.output_scenarios_primary_balance_pct_gdp_summary_hot)

    @cached_property
    def output_scenarios_dspb_milestones_hot_pb_star(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_dspb_milestones_hot_pb_star(scenario_debt_stabilizing_primary_balance_hot=self.scenario_debt_stabilizing_primary_balance_hot)

    @cached_property
    def output_scenarios_dspb_milestones_hot_adapted_pb(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_dspb_milestones_hot_adapted_pb(output_scenarios_primary_balance_pct_gdp_summary_hot_adapted=self.output_scenarios_primary_balance_pct_gdp_summary_hot_adapted)

    @cached_property
    def output_scenarios_dspb_milestones_hot_adapted_pb_star(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_dspb_milestones_hot_adapted_pb_star(scenario_debt_stabilizing_primary_balance_hot_adapted=self.scenario_debt_stabilizing_primary_balance_hot_adapted)

    @cached_property
    def output_scenarios_dspb_milestones_hot_unadapted_pb(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_dspb_milestones_hot_unadapted_pb(output_scenarios_primary_balance_pct_gdp_summary_hot_unadapted=self.output_scenarios_primary_balance_pct_gdp_summary_hot_unadapted)

    @cached_property
    def output_scenarios_dspb_milestones_hot_unadapted_pb_star(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_dspb_milestones_hot_unadapted_pb_star(scenario_debt_stabilizing_primary_balance_hot_unadapted=self.scenario_debt_stabilizing_primary_balance_hot_unadapted)

    @cached_property
    def output_scenarios_primary_balance_pct_gdp_baseline_path(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_primary_balance_pct_gdp_baseline_path(baseline_primary_balance_pct_gdp=self.baseline_primary_balance_pct_gdp)

    @cached_property
    def output_scenarios_overall_balance_pct_gdp_baseline_path(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_overall_balance_pct_gdp_baseline_path(baseline_overall_balance_pct_gdp=self.baseline_overall_balance_pct_gdp)

    @cached_property
    def output_scenarios_debt_to_gdp_baseline_path(self) -> data.Series[float | str | None]:
        return internals.output_scenarios_debt_to_gdp_baseline_path(baseline_debt_to_gdp=self.baseline_debt_to_gdp)

    @cached_property
    def macrofiscal_country(self) -> str | int | float | bool:
        return internals.macrofiscal_country(country=self.country)

    @cached_property
    def macrofiscal_real_gdp_lcu(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_real_gdp_lcu(constant_macrofiscal_a67_a264=data.CONSTANT_MACROFISCAL_A67_A264, constant_macrofiscal_ag67_bb264=data.CONSTANT_MACROFISCAL_AG67_BB264, macrofiscal_country=self.macrofiscal_country)

    @cached_property
    def macrofiscal_nominal_gdp_lcu(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_nominal_gdp_lcu(constant_macrofiscal_a268_a465=data.CONSTANT_MACROFISCAL_A268_A465, constant_macrofiscal_ag268_bb465=data.CONSTANT_MACROFISCAL_AG268_BB465, macrofiscal_country=self.macrofiscal_country)

    @cached_property
    def macrofiscal_gdp_deflator(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_gdp_deflator(constant_macrofiscal_a469_a666=data.CONSTANT_MACROFISCAL_A469_A666, constant_macrofiscal_ag469_bb666=data.CONSTANT_MACROFISCAL_AG469_BB666, macrofiscal_country=self.macrofiscal_country)

    @cached_property
    def macrofiscal_revenue_lcu(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_revenue_lcu(constant_macrofiscal_a670_a867=data.CONSTANT_MACROFISCAL_A670_A867, constant_macrofiscal_ah670_bb867=data.CONSTANT_MACROFISCAL_AH670_BB867, macrofiscal_country=self.macrofiscal_country)

    @cached_property
    def macrofiscal_expenditure_lcu(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_expenditure_lcu(constant_macrofiscal_a871_a1068=data.CONSTANT_MACROFISCAL_A871_A1068, constant_macrofiscal_ah871_bb1068=data.CONSTANT_MACROFISCAL_AH871_BB1068, macrofiscal_country=self.macrofiscal_country)

    @cached_property
    def macrofiscal_overall_balance_lcu(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_overall_balance_lcu(constant_macrofiscal_a1072_a1269=data.CONSTANT_MACROFISCAL_A1072_A1269, constant_macrofiscal_ah1072_bb1269=data.CONSTANT_MACROFISCAL_AH1072_BB1269, macrofiscal_country=self.macrofiscal_country)

    @cached_property
    def macrofiscal_primary_balance_lcu(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_primary_balance_lcu(constant_macrofiscal_a1273_a1470=data.CONSTANT_MACROFISCAL_A1273_A1470, constant_macrofiscal_ah1273_bb1470=data.CONSTANT_MACROFISCAL_AH1273_BB1470, macrofiscal_country=self.macrofiscal_country)

    @cached_property
    def macrofiscal_debt_lcu(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_debt_lcu(constant_macrofiscal_a1474_a1671=data.CONSTANT_MACROFISCAL_A1474_A1671, constant_macrofiscal_ah1474_bb1671=data.CONSTANT_MACROFISCAL_AH1474_BB1671, macrofiscal_country=self.macrofiscal_country)

    @cached_property
    def macrofiscal_interest_expenditure_lcu(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_interest_expenditure_lcu(macrofiscal_overall_balance_lcu=self.macrofiscal_overall_balance_lcu, macrofiscal_primary_balance_lcu=self.macrofiscal_primary_balance_lcu)

    @cached_property
    def macrofiscal_primary_expenditure_lcu(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_primary_expenditure_lcu(macrofiscal_expenditure_lcu=self.macrofiscal_expenditure_lcu, macrofiscal_interest_expenditure_lcu=self.macrofiscal_interest_expenditure_lcu)

    @cached_property
    def macrofiscal_real_gdp_growth(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_real_gdp_growth(macrofiscal_real_gdp_lcu=self.macrofiscal_real_gdp_lcu)

    @cached_property
    def macrofiscal_nominal_gdp_growth(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_nominal_gdp_growth(macrofiscal_nominal_gdp_lcu=self.macrofiscal_nominal_gdp_lcu)

    @cached_property
    def macrofiscal_gdp_deflator_growth(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_gdp_deflator_growth(macrofiscal_gdp_deflator=self.macrofiscal_gdp_deflator)

    @cached_property
    def macrofiscal_revenue_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_revenue_pct_gdp(macrofiscal_nominal_gdp_lcu=self.macrofiscal_nominal_gdp_lcu, macrofiscal_revenue_lcu=self.macrofiscal_revenue_lcu)

    @cached_property
    def macrofiscal_primary_expenditure_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_primary_expenditure_pct_gdp(macrofiscal_nominal_gdp_lcu=self.macrofiscal_nominal_gdp_lcu, macrofiscal_primary_expenditure_lcu=self.macrofiscal_primary_expenditure_lcu)

    @cached_property
    def macrofiscal_interest_rate(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_interest_rate(macrofiscal_debt_lcu=self.macrofiscal_debt_lcu, macrofiscal_interest_expenditure_lcu=self.macrofiscal_interest_expenditure_lcu)

    @cached_property
    def macrofiscal_debt_to_gdp(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_debt_to_gdp(macrofiscal_nominal_gdp_lcu=self.macrofiscal_nominal_gdp_lcu, macrofiscal_debt_lcu=self.macrofiscal_debt_lcu)

    @cached_property
    def macrofiscal_overall_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_overall_balance_pct_gdp(macrofiscal_nominal_gdp_lcu=self.macrofiscal_nominal_gdp_lcu, macrofiscal_overall_balance_lcu=self.macrofiscal_overall_balance_lcu)

    @cached_property
    def macrofiscal_primary_balance_pct_gdp(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_primary_balance_pct_gdp(macrofiscal_nominal_gdp_lcu=self.macrofiscal_nominal_gdp_lcu, macrofiscal_primary_balance_lcu=self.macrofiscal_primary_balance_lcu)

    @cached_property
    def macrofiscal_interest_growth_differential(self) -> data.Series[float | str | None]:
        return internals.macrofiscal_interest_growth_differential(macrofiscal_nominal_gdp_growth=self.macrofiscal_nominal_gdp_growth, macrofiscal_interest_rate=self.macrofiscal_interest_rate)

    @cached_property
    def demography_country(self) -> str | int | float | bool:
        return internals.demography_country(country=self.country)

    @cached_property
    def demography_scenario_flag(self) -> str | int | float | bool:
        return internals.demography_scenario_flag(demography_scenario=self.demography_scenario)

    @cached_property
    def demography_working_age_population(self) -> data.Series[float | str | None]:
        return internals.demography_working_age_population(demography_variant_label_medium=data.DEMOGRAPHY_VARIANT_LABEL_MEDIUM, demography_variant_label_high=data.DEMOGRAPHY_VARIANT_LABEL_HIGH, demography_variant_label_low=data.DEMOGRAPHY_VARIANT_LABEL_LOW, demography_scenario_flag=self.demography_scenario_flag, demography_working_age_population_medium=self.demography_working_age_population_medium, demography_working_age_population_high=self.demography_working_age_population_high, demography_working_age_population_low=self.demography_working_age_population_low)

    @cached_property
    def demography_total_population(self) -> data.Series[float | str | None]:
        return internals.demography_total_population(demography_variant_label_medium=data.DEMOGRAPHY_VARIANT_LABEL_MEDIUM, demography_variant_label_high=data.DEMOGRAPHY_VARIANT_LABEL_HIGH, demography_variant_label_low=data.DEMOGRAPHY_VARIANT_LABEL_LOW, demography_scenario_flag=self.demography_scenario_flag, demography_total_population_medium=self.demography_total_population_medium, demography_total_population_high=self.demography_total_population_high, demography_total_population_low=self.demography_total_population_low)

    @cached_property
    def demography_working_age_population_medium(self) -> data.Series[float | str | None]:
        return internals.demography_working_age_population_medium(constant_demography_b120_b317=data.CONSTANT_DEMOGRAPHY_B120_B317, constant_demography_bv120_ev317=data.CONSTANT_DEMOGRAPHY_BV120_EV317, demography_country=self.demography_country)

    @cached_property
    def demography_working_age_population_high(self) -> data.Series[float | str | None]:
        return internals.demography_working_age_population_high(constant_demography_b321_b518=data.CONSTANT_DEMOGRAPHY_B321_B518, constant_demography_bv321_ev518=data.CONSTANT_DEMOGRAPHY_BV321_EV518, demography_country=self.demography_country)

    @cached_property
    def demography_working_age_population_low(self) -> data.Series[float | str | None]:
        return internals.demography_working_age_population_low(constant_demography_b522_b719=data.CONSTANT_DEMOGRAPHY_B522_B719, constant_demography_bv522_ev719=data.CONSTANT_DEMOGRAPHY_BV522_EV719, demography_country=self.demography_country)

    @cached_property
    def demography_total_population_medium(self) -> data.Series[float | str | None]:
        return internals.demography_total_population_medium(constant_demography_b723_b920=data.CONSTANT_DEMOGRAPHY_B723_B920, constant_demography_bi723_ev920=data.CONSTANT_DEMOGRAPHY_BI723_EV920, demography_country=self.demography_country)

    @cached_property
    def demography_total_population_high(self) -> data.Series[float | str | None]:
        return internals.demography_total_population_high(constant_demography_b924_b1121=data.CONSTANT_DEMOGRAPHY_B924_B1121, constant_demography_bi924_ev1121=data.CONSTANT_DEMOGRAPHY_BI924_EV1121, demography_country=self.demography_country)

    @cached_property
    def demography_total_population_low(self) -> data.Series[float | str | None]:
        return internals.demography_total_population_low(constant_demography_b1125_b1322=data.CONSTANT_DEMOGRAPHY_B1125_B1322, constant_demography_bi1125_ev1322=data.CONSTANT_DEMOGRAPHY_BI1125_EV1322, demography_country=self.demography_country)

    @cached_property
    def productivity_country(self) -> str | int | float | bool:
        return internals.productivity_country(country=self.country)

    @cached_property
    def productivity_start_flag(self) -> float | str:
        return internals.productivity_start_flag(productivity_start=self.productivity_start)

    @cached_property
    def productivity_end_flag(self) -> float | str:
        return internals.productivity_end_flag(productivity_end=self.productivity_end)

    @cached_property
    def productivity_level(self) -> data.Series[float | str | None]:
        return internals.productivity_level(constant_productivity_a63_a260=data.CONSTANT_PRODUCTIVITY_A63_A260, constant_productivity_s63_ag260=data.CONSTANT_PRODUCTIVITY_S63_AG260, productivity_country=self.productivity_country, productivity_start_flag=self.productivity_start_flag, productivity_convergence_trajectory=self.productivity_convergence_trajectory)

    @cached_property
    def productivity_growth(self) -> data.Series[float | str | None]:
        return internals.productivity_growth(productivity_level=self.productivity_level)

    @cached_property
    def productivity_convergence_trajectory(self) -> data.Series[float | str | None]:
        return internals.productivity_convergence_trajectory(productivity_convergence_logistic_steepness=data.PRODUCTIVITY_CONVERGENCE_LOGISTIC_STEEPNESS, productivity_convergence_logistic_midpoint=data.PRODUCTIVITY_CONVERGENCE_LOGISTIC_MIDPOINT, productivity_convergence_period_index=data.PRODUCTIVITY_CONVERGENCE_PERIOD_INDEX, productivity_start_flag=self.productivity_start_flag, productivity_end_flag=self.productivity_end_flag)

    @cached_property
    def inflation_start_flag(self) -> float | str:
        return internals.inflation_start_flag(inflation_start=self.inflation_start)

    @cached_property
    def inflation_end_flag(self) -> float | str:
        return internals.inflation_end_flag(inflation_end=self.inflation_end)

    @cached_property
    def inflation_path(self) -> data.Series[float | str | None]:
        return internals.inflation_path(macrofiscal_gdp_deflator_growth=self.macrofiscal_gdp_deflator_growth, inflation_convergence_trajectory=self.inflation_convergence_trajectory)

    @cached_property
    def inflation_convergence_trajectory(self) -> data.Series[float | str | None]:
        return internals.inflation_convergence_trajectory(inflation_convergence_logistic_steepness=data.INFLATION_CONVERGENCE_LOGISTIC_STEEPNESS, inflation_convergence_logistic_midpoint=data.INFLATION_CONVERGENCE_LOGISTIC_MIDPOINT, inflation_convergence_period_index=data.INFLATION_CONVERGENCE_PERIOD_INDEX, inflation_start_flag=self.inflation_start_flag, inflation_end_flag=self.inflation_end_flag)

    @cached_property
    def interest_rate_mode_flag(self) -> str | int | float | bool:
        return internals.interest_rate_mode_flag(interest_rate_mode=self.interest_rate_mode)

    @cached_property
    def interest_rate_end_of_mtff(self) -> float | str:
        return internals.interest_rate_end_of_mtff(macrofiscal_interest_rate=self.macrofiscal_interest_rate)

    @cached_property
    def interest_growth_differential_end_of_mtff(self) -> float | str:
        return internals.interest_growth_differential_end_of_mtff(macrofiscal_interest_growth_differential=self.macrofiscal_interest_growth_differential)

    @cached_property
    def interest_rate_long_run_real_rate(self) -> float | str:
        return internals.interest_rate_long_run_real_rate(real_interest_rate=self.real_interest_rate)

    @cached_property
    def interest_rate_nominal_interest_rate(self) -> data.Series[float | str | None]:
        return internals.interest_rate_nominal_interest_rate(macrofiscal_interest_rate=self.macrofiscal_interest_rate, interest_rate_long_run_assumption=self.interest_rate_long_run_assumption)

    @cached_property
    def interest_rate_nominal_gdp_growth_baseline(self) -> data.Series[float | str | None]:
        return internals.interest_rate_nominal_gdp_growth_baseline(macrofiscal_nominal_gdp_growth=self.macrofiscal_nominal_gdp_growth, baseline_nominal_gdp_growth=self.baseline_nominal_gdp_growth)

    @cached_property
    def interest_rate_inflation_baseline(self) -> data.Series[float | str | None]:
        return internals.interest_rate_inflation_baseline(macrofiscal_gdp_deflator_growth=self.macrofiscal_gdp_deflator_growth, baseline_gdp_deflator_growth=self.baseline_gdp_deflator_growth)

    @cached_property
    def interest_rate_long_run_assumption(self) -> data.Series[float | str | None]:
        return internals.interest_rate_long_run_assumption(interest_rate_assumption_label_nominal=data.INTEREST_RATE_ASSUMPTION_LABEL_NOMINAL, interest_rate_assumption_label_differential=data.INTEREST_RATE_ASSUMPTION_LABEL_DIFFERENTIAL, interest_rate_assumption_label_real=data.INTEREST_RATE_ASSUMPTION_LABEL_REAL, interest_rate_mode_flag=self.interest_rate_mode_flag, interest_rate_long_run_nominal_interest_rate=self.interest_rate_long_run_nominal_interest_rate, interest_rate_long_run_interest_growth_differential=self.interest_rate_long_run_interest_growth_differential, interest_rate_long_run_real_interest_rate=self.interest_rate_long_run_real_interest_rate)

    @cached_property
    def interest_rate_long_run_nominal_interest_rate(self) -> data.Series[float | str | None]:
        return internals.interest_rate_long_run_nominal_interest_rate(interest_rate_end_of_mtff=self.interest_rate_end_of_mtff)

    @cached_property
    def interest_rate_long_run_interest_growth_differential(self) -> data.Series[float | str | None]:
        return internals.interest_rate_long_run_interest_growth_differential(interest_growth_differential_end_of_mtff=self.interest_growth_differential_end_of_mtff, interest_rate_nominal_gdp_growth_baseline=self.interest_rate_nominal_gdp_growth_baseline)

    @cached_property
    def interest_rate_long_run_real_interest_rate(self) -> data.Series[float | str | None]:
        return internals.interest_rate_long_run_real_interest_rate(interest_rate_long_run_real_rate=self.interest_rate_long_run_real_rate, interest_rate_inflation_baseline=self.interest_rate_inflation_baseline)

    @cached_property
    def climate_database_country(self) -> str | int | float | bool:
        return internals.climate_database_country(country=self.country)

    @cached_property
    def climate_database_gdp_loss_pct_paris(self) -> data.Series[float | str | None]:
        return internals.climate_database_gdp_loss_pct_paris(constant_climate_database_b26_b223=data.CONSTANT_CLIMATE_DATABASE_B26_B223, constant_climate_database_q26_ci223=data.CONSTANT_CLIMATE_DATABASE_Q26_CI223, climate_database_country=self.climate_database_country)

    @cached_property
    def climate_database_gdp_loss_pct_moderate(self) -> data.Series[float | str | None]:
        return internals.climate_database_gdp_loss_pct_moderate(constant_climate_database_b226_b423=data.CONSTANT_CLIMATE_DATABASE_B226_B423, constant_climate_database_q226_ci423=data.CONSTANT_CLIMATE_DATABASE_Q226_CI423, climate_database_country=self.climate_database_country)

    @cached_property
    def climate_database_gdp_loss_pct_high(self) -> data.Series[float | str | None]:
        return internals.climate_database_gdp_loss_pct_high(constant_climate_database_b426_b623=data.CONSTANT_CLIMATE_DATABASE_B426_B623, constant_climate_database_q426_ci623=data.CONSTANT_CLIMATE_DATABASE_Q426_CI623, climate_database_country=self.climate_database_country)

    @cached_property
    def climate_database_gdp_loss_pct_hot(self) -> data.Series[float | str | None]:
        return internals.climate_database_gdp_loss_pct_hot(constant_climate_database_b626_b823=data.CONSTANT_CLIMATE_DATABASE_B626_B823, constant_climate_database_q626_ci823=data.CONSTANT_CLIMATE_DATABASE_Q626_CI823, climate_database_country=self.climate_database_country)

    @cached_property
    def climate_database_gdp_loss_pct_hot_adapted(self) -> data.Series[float | str | None]:
        return internals.climate_database_gdp_loss_pct_hot_adapted(constant_climate_database_b826_b1023=data.CONSTANT_CLIMATE_DATABASE_B826_B1023, constant_climate_database_q826_ci1023=data.CONSTANT_CLIMATE_DATABASE_Q826_CI1023, climate_database_country=self.climate_database_country)

    @cached_property
    def climate_database_gdp_loss_pct_hot_unadapted(self) -> data.Series[float | str | None]:
        return internals.climate_database_gdp_loss_pct_hot_unadapted(constant_climate_database_b1026_b1223=data.CONSTANT_CLIMATE_DATABASE_B1026_B1223, constant_climate_database_q1026_ci1223=data.CONSTANT_CLIMATE_DATABASE_Q1026_CI1223, climate_database_country=self.climate_database_country)

    @cached_property
    def climate_database_gdp_index_paris(self) -> data.Series[float | str | None]:
        return internals.climate_database_gdp_index_paris(climate_database_gdp_loss_pct_paris=self.climate_database_gdp_loss_pct_paris)

    @cached_property
    def climate_database_gdp_index_moderate(self) -> data.Series[float | str | None]:
        return internals.climate_database_gdp_index_moderate(climate_database_gdp_loss_pct_moderate=self.climate_database_gdp_loss_pct_moderate)

    @cached_property
    def climate_database_gdp_index_high(self) -> data.Series[float | str | None]:
        return internals.climate_database_gdp_index_high(climate_database_gdp_loss_pct_high=self.climate_database_gdp_loss_pct_high)

    @cached_property
    def climate_database_gdp_index_hot(self) -> data.Series[float | str | None]:
        return internals.climate_database_gdp_index_hot(climate_database_gdp_loss_pct_hot=self.climate_database_gdp_loss_pct_hot)

    @cached_property
    def climate_database_gdp_index_hot_adapted(self) -> data.Series[float | str | None]:
        return internals.climate_database_gdp_index_hot_adapted(climate_database_gdp_loss_pct_hot_adapted=self.climate_database_gdp_loss_pct_hot_adapted)

    @cached_property
    def climate_database_gdp_index_hot_unadapted(self) -> data.Series[float | str | None]:
        return internals.climate_database_gdp_index_hot_unadapted(climate_database_gdp_loss_pct_hot_unadapted=self.climate_database_gdp_loss_pct_hot_unadapted)

    @cached_property
    def climate_database_labour_productivity_growth_variation_paris(self) -> data.Series[float | str | None]:
        return internals.climate_database_labour_productivity_growth_variation_paris(climate_database_gdp_index_paris=self.climate_database_gdp_index_paris)

    @cached_property
    def climate_database_labour_productivity_growth_variation_moderate(self) -> data.Series[float | str | None]:
        return internals.climate_database_labour_productivity_growth_variation_moderate(climate_database_gdp_index_moderate=self.climate_database_gdp_index_moderate)

    @cached_property
    def climate_database_labour_productivity_growth_variation_high(self) -> data.Series[float | str | None]:
        return internals.climate_database_labour_productivity_growth_variation_high(climate_database_gdp_index_high=self.climate_database_gdp_index_high)

    @cached_property
    def climate_database_labour_productivity_growth_variation_hot(self) -> data.Series[float | str | None]:
        return internals.climate_database_labour_productivity_growth_variation_hot(climate_database_gdp_index_hot=self.climate_database_gdp_index_hot)

    @cached_property
    def climate_database_labour_productivity_growth_variation_hot_adapted(self) -> data.Series[float | str | None]:
        return internals.climate_database_labour_productivity_growth_variation_hot_adapted(climate_database_gdp_index_hot_adapted=self.climate_database_gdp_index_hot_adapted)

    @cached_property
    def climate_database_labour_productivity_growth_variation_hot_unadapted(self) -> data.Series[float | str | None]:
        return internals.climate_database_labour_productivity_growth_variation_hot_unadapted(climate_database_gdp_index_hot_unadapted=self.climate_database_gdp_index_hot_unadapted)

    @cached_property
    def climate_data_labour_productivity_growth_variation_paris(self) -> data.Series[float | str | None]:
        return internals.climate_data_labour_productivity_growth_variation_paris(climate_database_labour_productivity_growth_variation_paris=self.climate_database_labour_productivity_growth_variation_paris)

    @cached_property
    def climate_data_labour_productivity_growth_variation_moderate(self) -> data.Series[float | str | None]:
        return internals.climate_data_labour_productivity_growth_variation_moderate(climate_database_labour_productivity_growth_variation_moderate=self.climate_database_labour_productivity_growth_variation_moderate)

    @cached_property
    def climate_data_labour_productivity_growth_variation_high(self) -> data.Series[float | str | None]:
        return internals.climate_data_labour_productivity_growth_variation_high(climate_database_labour_productivity_growth_variation_high=self.climate_database_labour_productivity_growth_variation_high)

    @cached_property
    def climate_data_labour_productivity_growth_variation_hot(self) -> data.Series[float | str | None]:
        return internals.climate_data_labour_productivity_growth_variation_hot(climate_database_labour_productivity_growth_variation_hot=self.climate_database_labour_productivity_growth_variation_hot)

    @cached_property
    def climate_data_labour_productivity_growth_variation_hot_adapted(self) -> data.Series[float | str | None]:
        return internals.climate_data_labour_productivity_growth_variation_hot_adapted(climate_database_labour_productivity_growth_variation_hot_adapted=self.climate_database_labour_productivity_growth_variation_hot_adapted)

    @cached_property
    def climate_data_labour_productivity_growth_variation_hot_unadapted(self) -> data.Series[float | str | None]:
        return internals.climate_data_labour_productivity_growth_variation_hot_unadapted(climate_database_labour_productivity_growth_variation_hot_unadapted=self.climate_database_labour_productivity_growth_variation_hot_unadapted)

    @cached_property
    def baseline_interest_rate(self) -> data.BaselineInterestRate:
        return internals.baseline_interest_rate(interest_rate_nominal_interest_rate=self.interest_rate_nominal_interest_rate)

    @cached_property
    def baseline_overall_balance_pct_gdp(self) -> data.BaselineOverallBalancePctGdp:
        return internals.baseline_overall_balance_pct_gdp(baseline_engine_total_expenditure_pct_gdp=self.baseline_engine_total_expenditure_pct_gdp, macrofiscal_overall_balance_pct_gdp=self.macrofiscal_overall_balance_pct_gdp, baseline_revenue_pct_gdp=self.baseline_revenue_pct_gdp)

    @cached_property
    def baseline_nominal_gdp_growth(self) -> data.BaselineNominalGdpGrowth:
        return internals.baseline_nominal_gdp_growth(baseline_engine_nominal_gdp_lcu=self.baseline_engine_nominal_gdp_lcu, macrofiscal_nominal_gdp_growth=self.macrofiscal_nominal_gdp_growth)

    @cached_property
    def baseline_revenue_pct_gdp(self) -> data.BaselineRevenuePctGdp:
        return internals.baseline_revenue_pct_gdp(baseline_engine_nominal_gdp_lcu=self.baseline_engine_nominal_gdp_lcu, baseline_engine_revenue_lcu=self.baseline_engine_revenue_lcu, macrofiscal_revenue_pct_gdp=self.macrofiscal_revenue_pct_gdp)

    @cached_property
    def baseline_gdp_deflator_growth(self) -> data.BaselineGdpDeflatorGrowth:
        return internals.baseline_gdp_deflator_growth(macrofiscal_gdp_deflator_growth=self.macrofiscal_gdp_deflator_growth, inflation_path=self.inflation_path)

    @cached_property
    def baseline_population_growth(self) -> data.BaselinePopulationGrowth:
        return internals.baseline_population_growth(baseline_engine_total_population=self.baseline_engine_total_population, demography_total_population=self.demography_total_population)

    @cached_property
    def scenario_primary_balance_pct_gdp(self) -> data.ScenarioPrimaryBalancePctGdp:
        return internals.scenario_primary_balance_pct_gdp(paris_engine_primary_balance_pct_gdp=self.paris_engine_primary_balance_pct_gdp, moderate_engine_primary_balance_pct_gdp=self.moderate_engine_primary_balance_pct_gdp, high_engine_primary_balance_pct_gdp=self.high_engine_primary_balance_pct_gdp, hot_engine_primary_balance_pct_gdp=self.hot_engine_primary_balance_pct_gdp, hot_adapted_engine_primary_balance_pct_gdp=self.hot_adapted_engine_primary_balance_pct_gdp, hot_unadapted_engine_primary_balance_pct_gdp=self.hot_unadapted_engine_primary_balance_pct_gdp)

    @cached_property
    def scenario_overall_balance_pct_gdp(self) -> data.ScenarioOverallBalancePctGdp:
        return internals.scenario_overall_balance_pct_gdp(paris_engine_overall_balance_pct_gdp=self.paris_engine_overall_balance_pct_gdp, moderate_engine_overall_balance_pct_gdp=self.moderate_engine_overall_balance_pct_gdp, high_engine_overall_balance_pct_gdp=self.high_engine_overall_balance_pct_gdp, hot_engine_overall_balance_pct_gdp=self.hot_engine_overall_balance_pct_gdp, hot_adapted_engine_overall_balance_pct_gdp=self.hot_adapted_engine_overall_balance_pct_gdp, hot_unadapted_engine_overall_balance_pct_gdp=self.hot_unadapted_engine_overall_balance_pct_gdp)

    @cached_property
    def scenario_debt_to_gdp(self) -> data.ScenarioDebtToGdp:
        return internals.scenario_debt_to_gdp(paris_engine_gross_debt_pct_gdp=self.paris_engine_gross_debt_pct_gdp, moderate_engine_gross_debt_pct_gdp=self.moderate_engine_gross_debt_pct_gdp, high_engine_gross_debt_pct_gdp=self.high_engine_gross_debt_pct_gdp, hot_engine_gross_debt_pct_gdp=self.hot_engine_gross_debt_pct_gdp, hot_adapted_engine_gross_debt_pct_gdp=self.hot_adapted_engine_gross_debt_pct_gdp, hot_unadapted_engine_gross_debt_pct_gdp=self.hot_unadapted_engine_gross_debt_pct_gdp)

    @cached_property
    def scenario_debt_stabilizing_primary_balance_paris(self) -> data.ScenarioDebtStabilizingPrimaryBalanceParis:
        return internals.scenario_debt_stabilizing_primary_balance_paris(paris_engine_weighted_interest_rate=self.paris_engine_weighted_interest_rate, paris_engine_gross_debt_pct_gdp=self.paris_engine_gross_debt_pct_gdp, scenario_nominal_gdp_growth_paris=self.scenario_nominal_gdp_growth_paris)

    @cached_property
    def scenario_debt_stabilizing_primary_balance_moderate(self) -> data.ScenarioDebtStabilizingPrimaryBalanceModerate:
        return internals.scenario_debt_stabilizing_primary_balance_moderate(moderate_engine_weighted_interest_rate=self.moderate_engine_weighted_interest_rate, moderate_engine_gross_debt_pct_gdp=self.moderate_engine_gross_debt_pct_gdp, scenario_nominal_gdp_growth_moderate=self.scenario_nominal_gdp_growth_moderate)

    @cached_property
    def scenario_debt_stabilizing_primary_balance_high(self) -> data.ScenarioDebtStabilizingPrimaryBalanceHigh:
        return internals.scenario_debt_stabilizing_primary_balance_high(high_engine_weighted_interest_rate=self.high_engine_weighted_interest_rate, high_engine_gross_debt_pct_gdp=self.high_engine_gross_debt_pct_gdp, scenario_nominal_gdp_growth_high=self.scenario_nominal_gdp_growth_high)

    @cached_property
    def scenario_debt_stabilizing_primary_balance_hot(self) -> data.ScenarioDebtStabilizingPrimaryBalanceHot:
        return internals.scenario_debt_stabilizing_primary_balance_hot(hot_engine_weighted_interest_rate=self.hot_engine_weighted_interest_rate, hot_engine_gross_debt_pct_gdp=self.hot_engine_gross_debt_pct_gdp, scenario_nominal_gdp_growth_hot=self.scenario_nominal_gdp_growth_hot)

    @cached_property
    def scenario_debt_stabilizing_primary_balance_hot_adapted(self) -> data.ScenarioDebtStabilizingPrimaryBalanceHotAdapted:
        return internals.scenario_debt_stabilizing_primary_balance_hot_adapted(hot_adapted_engine_weighted_interest_rate=self.hot_adapted_engine_weighted_interest_rate, hot_adapted_engine_gross_debt_pct_gdp=self.hot_adapted_engine_gross_debt_pct_gdp, scenario_nominal_gdp_growth_hot_adapted=self.scenario_nominal_gdp_growth_hot_adapted)

    @cached_property
    def scenario_debt_stabilizing_primary_balance_hot_unadapted(self) -> data.ScenarioDebtStabilizingPrimaryBalanceHotUnadapted:
        return internals.scenario_debt_stabilizing_primary_balance_hot_unadapted(hot_unadapted_engine_weighted_interest_rate=self.hot_unadapted_engine_weighted_interest_rate, hot_unadapted_engine_gross_debt_pct_gdp=self.hot_unadapted_engine_gross_debt_pct_gdp, scenario_nominal_gdp_growth_hot_unadapted=self.scenario_nominal_gdp_growth_hot_unadapted)

    @cached_property
    def scenario_nominal_gdp_growth_paris(self) -> data.ScenarioNominalGdpGrowthParis:
        return internals.scenario_nominal_gdp_growth_paris(paris_engine_real_gdp_growth=self.paris_engine_real_gdp_growth, paris_engine_gdp_deflator_growth=self.paris_engine_gdp_deflator_growth, baseline_nominal_gdp_growth=self.baseline_nominal_gdp_growth)

    @cached_property
    def scenario_nominal_gdp_growth_moderate(self) -> data.ScenarioNominalGdpGrowthModerate:
        return internals.scenario_nominal_gdp_growth_moderate(moderate_engine_real_gdp_growth=self.moderate_engine_real_gdp_growth, moderate_engine_gdp_deflator_growth=self.moderate_engine_gdp_deflator_growth, baseline_nominal_gdp_growth=self.baseline_nominal_gdp_growth)

    @cached_property
    def scenario_nominal_gdp_growth_high(self) -> data.ScenarioNominalGdpGrowthHigh:
        return internals.scenario_nominal_gdp_growth_high(high_engine_real_gdp_growth=self.high_engine_real_gdp_growth, high_engine_gdp_deflator_growth=self.high_engine_gdp_deflator_growth, baseline_nominal_gdp_growth=self.baseline_nominal_gdp_growth)

    @cached_property
    def scenario_nominal_gdp_growth_hot(self) -> data.ScenarioNominalGdpGrowthHot:
        return internals.scenario_nominal_gdp_growth_hot(hot_engine_real_gdp_growth=self.hot_engine_real_gdp_growth, hot_engine_gdp_deflator_growth=self.hot_engine_gdp_deflator_growth, baseline_nominal_gdp_growth=self.baseline_nominal_gdp_growth)

    @cached_property
    def scenario_nominal_gdp_growth_hot_adapted(self) -> data.ScenarioNominalGdpGrowthHotAdapted:
        return internals.scenario_nominal_gdp_growth_hot_adapted(hot_adapted_engine_real_gdp_growth=self.hot_adapted_engine_real_gdp_growth, hot_adapted_engine_gdp_deflator_growth=self.hot_adapted_engine_gdp_deflator_growth, baseline_nominal_gdp_growth=self.baseline_nominal_gdp_growth)

    @cached_property
    def scenario_nominal_gdp_growth_hot_unadapted(self) -> data.ScenarioNominalGdpGrowthHotUnadapted:
        return internals.scenario_nominal_gdp_growth_hot_unadapted(hot_unadapted_engine_real_gdp_growth=self.hot_unadapted_engine_real_gdp_growth, hot_unadapted_engine_gdp_deflator_growth=self.hot_unadapted_engine_gdp_deflator_growth, baseline_nominal_gdp_growth=self.baseline_nominal_gdp_growth)

    @cached_property
    def scenario_real_gdp_level_index_paris(self) -> data.ScenarioRealGdpLevelIndexParis:
        return internals.scenario_real_gdp_level_index_paris(baseline_engine_real_gdp_lcu=self.baseline_engine_real_gdp_lcu, paris_engine_real_gdp_growth=self.paris_engine_real_gdp_growth)

    @cached_property
    def scenario_real_gdp_level_index_moderate(self) -> data.ScenarioRealGdpLevelIndexModerate:
        return internals.scenario_real_gdp_level_index_moderate(baseline_engine_real_gdp_lcu=self.baseline_engine_real_gdp_lcu, moderate_engine_real_gdp_growth=self.moderate_engine_real_gdp_growth)

    @cached_property
    def scenario_real_gdp_level_index_high(self) -> data.ScenarioRealGdpLevelIndexHigh:
        return internals.scenario_real_gdp_level_index_high(baseline_engine_real_gdp_lcu=self.baseline_engine_real_gdp_lcu, high_engine_real_gdp_growth=self.high_engine_real_gdp_growth)

    @cached_property
    def scenario_real_gdp_level_index_hot(self) -> data.ScenarioRealGdpLevelIndexHot:
        return internals.scenario_real_gdp_level_index_hot(baseline_engine_real_gdp_lcu=self.baseline_engine_real_gdp_lcu, hot_engine_real_gdp_growth=self.hot_engine_real_gdp_growth)

    @cached_property
    def scenario_real_gdp_level_index_hot_adapted(self) -> data.ScenarioRealGdpLevelIndexHotAdapted:
        return internals.scenario_real_gdp_level_index_hot_adapted(baseline_engine_real_gdp_lcu=self.baseline_engine_real_gdp_lcu, hot_adapted_engine_real_gdp_growth=self.hot_adapted_engine_real_gdp_growth)

    @cached_property
    def scenario_real_gdp_level_index_hot_unadapted(self) -> data.ScenarioRealGdpLevelIndexHotUnadapted:
        return internals.scenario_real_gdp_level_index_hot_unadapted(baseline_engine_real_gdp_lcu=self.baseline_engine_real_gdp_lcu, hot_unadapted_engine_real_gdp_growth=self.hot_unadapted_engine_real_gdp_growth)

    @cached_property
    def scenario_fiscal_consolidation_gap_milestones_2050(self) -> data.ScenarioFiscalConsolidationGapMilestones2050:
        return internals.scenario_fiscal_consolidation_gap_milestones_2050(output_scenarios_dspb_milestones_paris_pb=self.output_scenarios_dspb_milestones_paris_pb, output_scenarios_dspb_milestones_paris_pb_star=self.output_scenarios_dspb_milestones_paris_pb_star, output_scenarios_dspb_milestones_moderate_pb=self.output_scenarios_dspb_milestones_moderate_pb, output_scenarios_dspb_milestones_moderate_pb_star=self.output_scenarios_dspb_milestones_moderate_pb_star, output_scenarios_dspb_milestones_high_pb=self.output_scenarios_dspb_milestones_high_pb, output_scenarios_dspb_milestones_high_pb_star=self.output_scenarios_dspb_milestones_high_pb_star, output_scenarios_dspb_milestones_hot_pb=self.output_scenarios_dspb_milestones_hot_pb, output_scenarios_dspb_milestones_hot_pb_star=self.output_scenarios_dspb_milestones_hot_pb_star, output_scenarios_dspb_milestones_hot_adapted_pb=self.output_scenarios_dspb_milestones_hot_adapted_pb, output_scenarios_dspb_milestones_hot_adapted_pb_star=self.output_scenarios_dspb_milestones_hot_adapted_pb_star, output_scenarios_dspb_milestones_hot_unadapted_pb=self.output_scenarios_dspb_milestones_hot_unadapted_pb, output_scenarios_dspb_milestones_hot_unadapted_pb_star=self.output_scenarios_dspb_milestones_hot_unadapted_pb_star)

    @cached_property
    def scenario_fiscal_consolidation_gap_milestones_2075(self) -> data.ScenarioFiscalConsolidationGapMilestones2075:
        return internals.scenario_fiscal_consolidation_gap_milestones_2075(output_scenarios_dspb_milestones_paris_pb=self.output_scenarios_dspb_milestones_paris_pb, output_scenarios_dspb_milestones_paris_pb_star=self.output_scenarios_dspb_milestones_paris_pb_star, output_scenarios_dspb_milestones_moderate_pb=self.output_scenarios_dspb_milestones_moderate_pb, output_scenarios_dspb_milestones_moderate_pb_star=self.output_scenarios_dspb_milestones_moderate_pb_star, output_scenarios_dspb_milestones_high_pb=self.output_scenarios_dspb_milestones_high_pb, output_scenarios_dspb_milestones_high_pb_star=self.output_scenarios_dspb_milestones_high_pb_star, output_scenarios_dspb_milestones_hot_pb=self.output_scenarios_dspb_milestones_hot_pb, output_scenarios_dspb_milestones_hot_pb_star=self.output_scenarios_dspb_milestones_hot_pb_star, output_scenarios_dspb_milestones_hot_adapted_pb=self.output_scenarios_dspb_milestones_hot_adapted_pb, output_scenarios_dspb_milestones_hot_adapted_pb_star=self.output_scenarios_dspb_milestones_hot_adapted_pb_star, output_scenarios_dspb_milestones_hot_unadapted_pb=self.output_scenarios_dspb_milestones_hot_unadapted_pb, output_scenarios_dspb_milestones_hot_unadapted_pb_star=self.output_scenarios_dspb_milestones_hot_unadapted_pb_star)

    @cached_property
    def scenario_fiscal_consolidation_gap_milestones_2099(self) -> data.ScenarioFiscalConsolidationGapMilestones2099:
        return internals.scenario_fiscal_consolidation_gap_milestones_2099(output_scenarios_dspb_milestones_paris_pb=self.output_scenarios_dspb_milestones_paris_pb, output_scenarios_dspb_milestones_paris_pb_star=self.output_scenarios_dspb_milestones_paris_pb_star, output_scenarios_dspb_milestones_moderate_pb=self.output_scenarios_dspb_milestones_moderate_pb, output_scenarios_dspb_milestones_moderate_pb_star=self.output_scenarios_dspb_milestones_moderate_pb_star, output_scenarios_dspb_milestones_high_pb=self.output_scenarios_dspb_milestones_high_pb, output_scenarios_dspb_milestones_high_pb_star=self.output_scenarios_dspb_milestones_high_pb_star, output_scenarios_dspb_milestones_hot_pb=self.output_scenarios_dspb_milestones_hot_pb, output_scenarios_dspb_milestones_hot_pb_star=self.output_scenarios_dspb_milestones_hot_pb_star, output_scenarios_dspb_milestones_hot_adapted_pb=self.output_scenarios_dspb_milestones_hot_adapted_pb, output_scenarios_dspb_milestones_hot_adapted_pb_star=self.output_scenarios_dspb_milestones_hot_adapted_pb_star, output_scenarios_dspb_milestones_hot_unadapted_pb=self.output_scenarios_dspb_milestones_hot_unadapted_pb, output_scenarios_dspb_milestones_hot_unadapted_pb_star=self.output_scenarios_dspb_milestones_hot_unadapted_pb_star)


@dataclass(frozen=True, kw_only=True)
class BaselinePrimaryExpenditurePctGdpInputs(_SnapshotInputs):
    """Bound input leaves for `compute_baseline_primary_expenditure_pct_gdp`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class BaselineInterestExpenditurePctGdpInputs(_SnapshotInputs):
    """Bound input leaves for `compute_baseline_interest_expenditure_pct_gdp`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class BaselineInterestRateInputs(_SnapshotInputs):
    """Bound input leaves for `compute_baseline_interest_rate`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class BaselinePrimaryBalancePctGdpInputs(_SnapshotInputs):
    """Bound input leaves for `compute_baseline_primary_balance_pct_gdp`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class BaselineOverallBalancePctGdpInputs(_SnapshotInputs):
    """Bound input leaves for `compute_baseline_overall_balance_pct_gdp`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class BaselineDebtToGdpInputs(_SnapshotInputs):
    """Bound input leaves for `compute_baseline_debt_to_gdp`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class BaselineDebtStabilizingPrimaryBalanceInputs(_SnapshotInputs):
    """Bound input leaves for `compute_baseline_debt_stabilizing_primary_balance`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class BaselineFiscalConsolidationGapInputs(_SnapshotInputs):
    """Bound input leaves for `compute_baseline_fiscal_consolidation_gap`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class BaselineNominalGdpGrowthInputs(_SnapshotInputs):
    """Bound input leaves for `compute_baseline_nominal_gdp_growth`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class BaselineRealGdpGrowthInputs(_SnapshotInputs):
    """Bound input leaves for `compute_baseline_real_gdp_growth`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class BaselineRevenuePctGdpInputs(_SnapshotInputs):
    """Bound input leaves for `compute_baseline_revenue_pct_gdp`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class BaselineEmploymentGrowthInputs(_SnapshotInputs):
    """Bound input leaves for `compute_baseline_employment_growth`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class BaselineLabourProductivityGrowthInputs(_SnapshotInputs):
    """Bound input leaves for `compute_baseline_labour_productivity_growth`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class BaselineGdpDeflatorGrowthInputs(_SnapshotInputs):
    """Bound input leaves for `compute_baseline_gdp_deflator_growth`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class BaselinePopulationGrowthInputs(_SnapshotInputs):
    """Bound input leaves for `compute_baseline_population_growth`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioPrimaryBalancePctGdpInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_primary_balance_pct_gdp`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioOverallBalancePctGdpInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_overall_balance_pct_gdp`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioDebtToGdpInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_debt_to_gdp`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioDebtStabilizingPrimaryBalanceParisInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_debt_stabilizing_primary_balance_paris`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioDebtStabilizingPrimaryBalanceModerateInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_debt_stabilizing_primary_balance_moderate`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioDebtStabilizingPrimaryBalanceHighInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_debt_stabilizing_primary_balance_high`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioDebtStabilizingPrimaryBalanceHotInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_debt_stabilizing_primary_balance_hot`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioDebtStabilizingPrimaryBalanceHotAdaptedInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_debt_stabilizing_primary_balance_hot_adapted`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioDebtStabilizingPrimaryBalanceHotUnadaptedInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_debt_stabilizing_primary_balance_hot_unadapted`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioNominalGdpGrowthParisInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_nominal_gdp_growth_paris`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioNominalGdpGrowthModerateInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_nominal_gdp_growth_moderate`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioNominalGdpGrowthHighInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_nominal_gdp_growth_high`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioNominalGdpGrowthHotInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_nominal_gdp_growth_hot`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioNominalGdpGrowthHotAdaptedInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_nominal_gdp_growth_hot_adapted`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioNominalGdpGrowthHotUnadaptedInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_nominal_gdp_growth_hot_unadapted`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioPrimaryExpenditurePctGdpParisInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_primary_expenditure_pct_gdp_paris`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioPrimaryExpenditurePctGdpModerateInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_primary_expenditure_pct_gdp_moderate`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioPrimaryExpenditurePctGdpHighInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_primary_expenditure_pct_gdp_high`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioPrimaryExpenditurePctGdpHotInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_primary_expenditure_pct_gdp_hot`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioPrimaryExpenditurePctGdpHotAdaptedInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_primary_expenditure_pct_gdp_hot_adapted`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioPrimaryExpenditurePctGdpHotUnadaptedInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_primary_expenditure_pct_gdp_hot_unadapted`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioInterestExpenditurePctGdpParisInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_interest_expenditure_pct_gdp_paris`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioInterestExpenditurePctGdpModerateInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_interest_expenditure_pct_gdp_moderate`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioInterestExpenditurePctGdpHighInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_interest_expenditure_pct_gdp_high`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioInterestExpenditurePctGdpHotInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_interest_expenditure_pct_gdp_hot`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioInterestExpenditurePctGdpHotAdaptedInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_interest_expenditure_pct_gdp_hot_adapted`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioInterestExpenditurePctGdpHotUnadaptedInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_interest_expenditure_pct_gdp_hot_unadapted`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioRealGdpLevelIndexParisInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_real_gdp_level_index_paris`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioRealGdpLevelIndexModerateInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_real_gdp_level_index_moderate`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioRealGdpLevelIndexHighInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_real_gdp_level_index_high`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioRealGdpLevelIndexHotInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_real_gdp_level_index_hot`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioRealGdpLevelIndexHotAdaptedInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_real_gdp_level_index_hot_adapted`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioRealGdpLevelIndexHotUnadaptedInputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_real_gdp_level_index_hot_unadapted`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioFiscalConsolidationGapMilestones2050Inputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_fiscal_consolidation_gap_milestones_2050`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioFiscalConsolidationGapMilestones2075Inputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_fiscal_consolidation_gap_milestones_2075`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


@dataclass(frozen=True, kw_only=True)
class ScenarioFiscalConsolidationGapMilestones2099Inputs(_SnapshotInputs):
    """Bound input leaves for `compute_scenario_fiscal_consolidation_gap_milestones_2099`."""

    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"] = _field(
        metadata={"default": data.COUNTRY_DEFAULT, "cells": data.COUNTRY_CELLS},
    )
    demography_scenario: Literal["High", "Low", "Medium"] = _field(
        metadata={"default": data.DEMOGRAPHY_SCENARIO_DEFAULT, "cells": data.DEMOGRAPHY_SCENARIO_CELLS},
    )
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_START_DEFAULT, "cells": data.PRODUCTIVITY_START_CELLS},
    )
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.PRODUCTIVITY_END_DEFAULT, "cells": data.PRODUCTIVITY_END_CELLS},
    )
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_START_DEFAULT, "cells": data.INFLATION_START_CELLS},
    )
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)] = _field(
        metadata={"default": data.INFLATION_END_DEFAULT, "cells": data.INFLATION_END_CELLS},
    )
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"] = _field(
        metadata={"default": data.INTEREST_RATE_MODE_DEFAULT, "cells": data.INTEREST_RATE_MODE_CELLS},
    )
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)] = _field(
        metadata={"default": data.REAL_INTEREST_RATE_DEFAULT, "cells": data.REAL_INTEREST_RATE_CELLS},
    )
    fiscal_rule_enabled: Literal["No", "Yes"] = _field(
        metadata={"default": data.FISCAL_RULE_ENABLED_DEFAULT, "cells": data.FISCAL_RULE_ENABLED_CELLS},
    )
    debt_target: Annotated[float, RealBetween(0.0, 300.0)] = _field(
        metadata={"default": data.DEBT_TARGET_DEFAULT, "cells": data.DEBT_TARGET_CELLS},
    )
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)] = _field(
        metadata={"default": data.EXPENDITURE_RIGIDITY_DEFAULT, "cells": data.EXPENDITURE_RIGIDITY_CELLS},
    )
    discrete_revenue_shocks: data.DiscreteRevenueShocks = _field(
        metadata={"default": data.DISCRETE_REVENUE_SHOCKS_DEFAULT, "cells": data.DISCRETE_REVENUE_SHOCKS.cells},
    )
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks = _field(
        metadata={"default": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS_DEFAULT, "cells": data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.cells},
    )


__all__ = [
    "Model",
    "BaselinePrimaryExpenditurePctGdpInputs",
    "BaselineInterestExpenditurePctGdpInputs",
    "BaselineInterestRateInputs",
    "BaselinePrimaryBalancePctGdpInputs",
    "BaselineOverallBalancePctGdpInputs",
    "BaselineDebtToGdpInputs",
    "BaselineDebtStabilizingPrimaryBalanceInputs",
    "BaselineFiscalConsolidationGapInputs",
    "BaselineNominalGdpGrowthInputs",
    "BaselineRealGdpGrowthInputs",
    "BaselineRevenuePctGdpInputs",
    "BaselineEmploymentGrowthInputs",
    "BaselineLabourProductivityGrowthInputs",
    "BaselineGdpDeflatorGrowthInputs",
    "BaselinePopulationGrowthInputs",
    "ScenarioPrimaryBalancePctGdpInputs",
    "ScenarioOverallBalancePctGdpInputs",
    "ScenarioDebtToGdpInputs",
    "ScenarioDebtStabilizingPrimaryBalanceParisInputs",
    "ScenarioDebtStabilizingPrimaryBalanceModerateInputs",
    "ScenarioDebtStabilizingPrimaryBalanceHighInputs",
    "ScenarioDebtStabilizingPrimaryBalanceHotInputs",
    "ScenarioDebtStabilizingPrimaryBalanceHotAdaptedInputs",
    "ScenarioDebtStabilizingPrimaryBalanceHotUnadaptedInputs",
    "ScenarioNominalGdpGrowthParisInputs",
    "ScenarioNominalGdpGrowthModerateInputs",
    "ScenarioNominalGdpGrowthHighInputs",
    "ScenarioNominalGdpGrowthHotInputs",
    "ScenarioNominalGdpGrowthHotAdaptedInputs",
    "ScenarioNominalGdpGrowthHotUnadaptedInputs",
    "ScenarioPrimaryExpenditurePctGdpParisInputs",
    "ScenarioPrimaryExpenditurePctGdpModerateInputs",
    "ScenarioPrimaryExpenditurePctGdpHighInputs",
    "ScenarioPrimaryExpenditurePctGdpHotInputs",
    "ScenarioPrimaryExpenditurePctGdpHotAdaptedInputs",
    "ScenarioPrimaryExpenditurePctGdpHotUnadaptedInputs",
    "ScenarioInterestExpenditurePctGdpParisInputs",
    "ScenarioInterestExpenditurePctGdpModerateInputs",
    "ScenarioInterestExpenditurePctGdpHighInputs",
    "ScenarioInterestExpenditurePctGdpHotInputs",
    "ScenarioInterestExpenditurePctGdpHotAdaptedInputs",
    "ScenarioInterestExpenditurePctGdpHotUnadaptedInputs",
    "ScenarioRealGdpLevelIndexParisInputs",
    "ScenarioRealGdpLevelIndexModerateInputs",
    "ScenarioRealGdpLevelIndexHighInputs",
    "ScenarioRealGdpLevelIndexHotInputs",
    "ScenarioRealGdpLevelIndexHotAdaptedInputs",
    "ScenarioRealGdpLevelIndexHotUnadaptedInputs",
    "ScenarioFiscalConsolidationGapMilestones2050Inputs",
    "ScenarioFiscalConsolidationGapMilestones2075Inputs",
    "ScenarioFiscalConsolidationGapMilestones2099Inputs",
]
