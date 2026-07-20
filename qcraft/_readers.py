from __future__ import annotations

from .runtime import CellValue, EvalContext, xl_cell, xl_range

# --- Series binding readers ---

_LEAF_INDEX_COUNTRY = {
    (): 'Dashboard!C12',
}

def read_country(ctx: EvalContext) -> CellValue:
    """Read the selected country from the Dashboard worksheet.

    Returns the country name currently selected on the Dashboard.
    The OBS_VALUE field maps directly to the Dashboard cell C12, returning the country name as a string.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - OBS_VALUE: Name of the country selected for the baseline and climate scenarios.

    Source binding:
        Workbook range: Dashboard!C12
        Layout: scalar
        Value type: string

    Examples:
        read_country(ctx=ctx)
    """
    return xl_cell(ctx, 'Dashboard!C12')

_LEAF_INDEX_DEMOGRAPHY_SCENARIO = {
    (): 'Dashboard!C17',
}

def read_demography_scenario(ctx: EvalContext) -> CellValue:
    """Read the selected demographic scenario from the dashboard.

    Returns the demography scenario currently configured in the workbook.
    Each record maps to the single dashboard cell that holds the scenario identifier.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - OBS_VALUE: The chosen demographic scenario (e.g., Medium, High, or Low).

    Source binding:
        Workbook range: Dashboard!C17
        Layout: scalar
        Value type: string

    Examples:
        read_demography_scenario(ctx=ctx)
    """
    return xl_cell(ctx, 'Dashboard!C17')

_LEAF_INDEX_PRODUCTIVITY_START = {
    (): 'Dashboard!C20',
}

def read_productivity_start(ctx: EvalContext) -> CellValue:
    """Read the start productivity growth rate from the Q-CRAFT Dashboard.

    Returns the scalar productivity growth rate at the start of the projection period, set in cell C20 of the Dashboard.
    The OBS_VALUE field is read from a single cell in the Dashboard worksheet and corresponds to the scalar productivity_start parameter.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - OBS_VALUE: The productivity growth rate (in percent) at the beginning of the Q-CRAFT projection period (2029), used to initialize the long-term productivity trajectory.

    Source binding:
        Workbook range: Dashboard!C20
        Layout: scalar
        Value type: float

    Examples:
        read_productivity_start(ctx=ctx)
    """
    return xl_cell(ctx, 'Dashboard!C20')

_LEAF_INDEX_PRODUCTIVITY_END = {
    (): 'Dashboard!C21',
}

def read_productivity_end(ctx: EvalContext) -> CellValue:
    """Read the end-period structural labour productivity growth assumption from the Dashboard.

    Returns the long-run productivity growth rate (percent per year) set by the user in the Dashboard.
    The single record's `OBS_VALUE` maps to the scalar value in cell C21 of the Dashboard worksheet.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - OBS_VALUE: The assumed structural labour productivity growth rate for the end period (2090–2100), expressed as a percent per year.

    Source binding:
        Workbook range: Dashboard!C21
        Layout: scalar
        Value type: float

    Examples:
        read_productivity_end(ctx=ctx)
    """
    return xl_cell(ctx, 'Dashboard!C21')

_LEAF_INDEX_INFLATION_START = {
    (): 'Dashboard!C24',
}

def read_inflation_start(ctx: EvalContext) -> CellValue:
    """Read the start inflation rate used in the baseline scenario.

    Returns the start inflation assumption from the Dashboard.
    Each record corresponds to the scalar inflation start value in cell Dashboard!C24.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - OBS_VALUE: The assumed start year inflation rate (percent).

    Source binding:
        Workbook range: Dashboard!C24
        Layout: scalar
        Value type: float

    Examples:
        read_inflation_start(ctx=ctx)
    """
    return xl_cell(ctx, 'Dashboard!C24')

_LEAF_INDEX_INFLATION_END = {
    (): 'Dashboard!C25',
}

def read_inflation_end(ctx: EvalContext) -> CellValue:
    """Read the end-period inflation assumption from the Dashboard.

    Returns the long-run inflation rate entered in the Dashboard.
    Each record corresponds to the scalar value in cell Dashboard!C25.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - OBS_VALUE: The long-run inflation rate used after the WEO projection horizon.

    Source binding:
        Workbook range: Dashboard!C25
        Layout: scalar
        Value type: float

    Examples:
        read_inflation_end(ctx=ctx)
    """
    return xl_cell(ctx, 'Dashboard!C25')

_LEAF_INDEX_INTEREST_RATE_MODE = {
    (): 'Dashboard!C28',
}

def read_interest_rate_mode(ctx: EvalContext) -> CellValue:
    """Read the interest rate mode parameter used for long-term fiscal projections.

    Returns the interest rate mode setting from the Dashboard worksheet.
    The single record returned corresponds to the value in cell C28 of the Dashboard sheet.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - OBS_VALUE: The interest rate assumption mode selected in the Dashboard (e.g., constant nominal rate, constant interest–growth differential, or constant real rate).

    Source binding:
        Workbook range: Dashboard!C28
        Layout: scalar
        Value type: string

    Examples:
        read_interest_rate_mode(ctx=ctx)
    """
    return xl_cell(ctx, 'Dashboard!C28')

_LEAF_INDEX_REAL_INTEREST_RATE = {
    (): 'Dashboard!C29',
}

def read_real_interest_rate(ctx: EvalContext) -> CellValue:
    """Read the real interest rate assumption from the Dashboard.

    Returns the user-selected long-term real interest rate.
    The record corresponds to the value in the Dashboard cell for real interest rate.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - OBS_VALUE: The real interest rate value.

    Source binding:
        Workbook range: Dashboard!C29
        Layout: scalar
        Value type: float

    Examples:
        read_real_interest_rate(ctx=ctx)
    """
    return xl_cell(ctx, 'Dashboard!C29')

_LEAF_INDEX_FISCAL_RULE_ENABLED = {
    (): 'Dashboard!C33',
}

def read_fiscal_rule_enabled(ctx: EvalContext) -> CellValue:
    """Read whether a fiscal rule debt target is enabled in the dashboard.

    Returns a single record indicating if the fiscal rule assumption is set to "Yes" or "No".
    Each record corresponds to the fiscal rule enabled setting in cell C33 of the Dashboard worksheet.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - OBS_VALUE: Indicates whether the user has opted to apply a fiscal rule debt target.

    Source binding:
        Workbook range: Dashboard!C33
        Layout: scalar
        Value type: string

    Examples:
        read_fiscal_rule_enabled(ctx=ctx)
    """
    return xl_cell(ctx, 'Dashboard!C33')

_LEAF_INDEX_DEBT_TARGET = {
    (): 'Dashboard!C34',
}

def read_debt_target(ctx: EvalContext) -> CellValue:
    """Read the debt-to-GDP ratio target for the fiscal rule from the Dashboard sheet.

    Returns a scalar float representing the debt-to-GDP ratio target set by the user for the fiscal rule.
    The function reads a single cell, mapping its value to the OBS_VALUE field of the returned record.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - OBS_VALUE: The debt-to-GDP ratio target (in percent of GDP) selected for the fiscal rule assumption.

    Source binding:
        Workbook range: Dashboard!C34
        Layout: scalar
        Value type: float

    Examples:
        read_debt_target(ctx=ctx)
    """
    return xl_cell(ctx, 'Dashboard!C34')

_LEAF_INDEX_EXPENDITURE_RIGIDITY = {
    (): 'Dashboard!C38',
}

def read_expenditure_rigidity(ctx: EvalContext) -> CellValue:
    """Read the expenditure rigidity parameter from the Dashboard worksheet.

    Returns the current value of the expenditure rigidity parameter.
    Each record contains one observation value that maps to cell C38 in the Dashboard worksheet.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - OBS_VALUE: The expenditure rigidity parameter value, ranging from 0 (fully flexible primary expenditure) to 1 (completely rigid primary expenditure).

    Source binding:
        Workbook range: Dashboard!C38
        Layout: scalar
        Value type: float

    Examples:
        read_expenditure_rigidity(ctx=ctx)
    """
    return xl_cell(ctx, 'Dashboard!C38')

_LEAF_INDEX_DISCRETE_REVENUE_SHOCKS = {
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2030)): "'Discrete Risks'!C2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2031)): "'Discrete Risks'!D2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2032)): "'Discrete Risks'!E2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2033)): "'Discrete Risks'!F2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2034)): "'Discrete Risks'!G2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2035)): "'Discrete Risks'!H2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2036)): "'Discrete Risks'!I2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2037)): "'Discrete Risks'!J2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2038)): "'Discrete Risks'!K2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2039)): "'Discrete Risks'!L2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2040)): "'Discrete Risks'!M2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2041)): "'Discrete Risks'!N2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2042)): "'Discrete Risks'!O2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2043)): "'Discrete Risks'!P2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2044)): "'Discrete Risks'!Q2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2045)): "'Discrete Risks'!R2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2046)): "'Discrete Risks'!S2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2047)): "'Discrete Risks'!T2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2048)): "'Discrete Risks'!U2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2049)): "'Discrete Risks'!V2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2050)): "'Discrete Risks'!W2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2051)): "'Discrete Risks'!X2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2052)): "'Discrete Risks'!Y2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2053)): "'Discrete Risks'!Z2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2054)): "'Discrete Risks'!AA2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2055)): "'Discrete Risks'!AB2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2056)): "'Discrete Risks'!AC2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2057)): "'Discrete Risks'!AD2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2058)): "'Discrete Risks'!AE2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2059)): "'Discrete Risks'!AF2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2060)): "'Discrete Risks'!AG2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2061)): "'Discrete Risks'!AH2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2062)): "'Discrete Risks'!AI2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2063)): "'Discrete Risks'!AJ2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2064)): "'Discrete Risks'!AK2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2065)): "'Discrete Risks'!AL2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2066)): "'Discrete Risks'!AM2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2067)): "'Discrete Risks'!AN2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2068)): "'Discrete Risks'!AO2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2069)): "'Discrete Risks'!AP2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2070)): "'Discrete Risks'!AQ2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2071)): "'Discrete Risks'!AR2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2072)): "'Discrete Risks'!AS2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2073)): "'Discrete Risks'!AT2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2074)): "'Discrete Risks'!AU2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2075)): "'Discrete Risks'!AV2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2076)): "'Discrete Risks'!AW2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2077)): "'Discrete Risks'!AX2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2078)): "'Discrete Risks'!AY2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2079)): "'Discrete Risks'!AZ2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2080)): "'Discrete Risks'!BA2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2081)): "'Discrete Risks'!BB2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2082)): "'Discrete Risks'!BC2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2083)): "'Discrete Risks'!BD2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2084)): "'Discrete Risks'!BE2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2085)): "'Discrete Risks'!BF2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2086)): "'Discrete Risks'!BG2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2087)): "'Discrete Risks'!BH2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2088)): "'Discrete Risks'!BI2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2089)): "'Discrete Risks'!BJ2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2090)): "'Discrete Risks'!BK2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2091)): "'Discrete Risks'!BL2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2092)): "'Discrete Risks'!BM2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2093)): "'Discrete Risks'!BN2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2094)): "'Discrete Risks'!BO2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2095)): "'Discrete Risks'!BP2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2096)): "'Discrete Risks'!BQ2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2097)): "'Discrete Risks'!BR2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2098)): "'Discrete Risks'!BS2",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2099)): "'Discrete Risks'!BT2",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2030)): "'Discrete Risks'!C4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2031)): "'Discrete Risks'!D4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2032)): "'Discrete Risks'!E4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2033)): "'Discrete Risks'!F4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2034)): "'Discrete Risks'!G4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2035)): "'Discrete Risks'!H4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2036)): "'Discrete Risks'!I4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2037)): "'Discrete Risks'!J4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2038)): "'Discrete Risks'!K4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2039)): "'Discrete Risks'!L4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2040)): "'Discrete Risks'!M4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2041)): "'Discrete Risks'!N4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2042)): "'Discrete Risks'!O4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2043)): "'Discrete Risks'!P4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2044)): "'Discrete Risks'!Q4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2045)): "'Discrete Risks'!R4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2046)): "'Discrete Risks'!S4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2047)): "'Discrete Risks'!T4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2048)): "'Discrete Risks'!U4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2049)): "'Discrete Risks'!V4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2050)): "'Discrete Risks'!W4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2051)): "'Discrete Risks'!X4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2052)): "'Discrete Risks'!Y4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2053)): "'Discrete Risks'!Z4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2054)): "'Discrete Risks'!AA4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2055)): "'Discrete Risks'!AB4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2056)): "'Discrete Risks'!AC4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2057)): "'Discrete Risks'!AD4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2058)): "'Discrete Risks'!AE4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2059)): "'Discrete Risks'!AF4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2060)): "'Discrete Risks'!AG4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2061)): "'Discrete Risks'!AH4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2062)): "'Discrete Risks'!AI4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2063)): "'Discrete Risks'!AJ4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2064)): "'Discrete Risks'!AK4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2065)): "'Discrete Risks'!AL4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2066)): "'Discrete Risks'!AM4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2067)): "'Discrete Risks'!AN4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2068)): "'Discrete Risks'!AO4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2069)): "'Discrete Risks'!AP4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2070)): "'Discrete Risks'!AQ4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2071)): "'Discrete Risks'!AR4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2072)): "'Discrete Risks'!AS4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2073)): "'Discrete Risks'!AT4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2074)): "'Discrete Risks'!AU4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2075)): "'Discrete Risks'!AV4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2076)): "'Discrete Risks'!AW4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2077)): "'Discrete Risks'!AX4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2078)): "'Discrete Risks'!AY4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2079)): "'Discrete Risks'!AZ4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2080)): "'Discrete Risks'!BA4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2081)): "'Discrete Risks'!BB4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2082)): "'Discrete Risks'!BC4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2083)): "'Discrete Risks'!BD4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2084)): "'Discrete Risks'!BE4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2085)): "'Discrete Risks'!BF4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2086)): "'Discrete Risks'!BG4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2087)): "'Discrete Risks'!BH4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2088)): "'Discrete Risks'!BI4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2089)): "'Discrete Risks'!BJ4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2090)): "'Discrete Risks'!BK4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2091)): "'Discrete Risks'!BL4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2092)): "'Discrete Risks'!BM4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2093)): "'Discrete Risks'!BN4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2094)): "'Discrete Risks'!BO4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2095)): "'Discrete Risks'!BP4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2096)): "'Discrete Risks'!BQ4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2097)): "'Discrete Risks'!BR4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2098)): "'Discrete Risks'!BS4",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2099)): "'Discrete Risks'!BT4",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2030)): "'Discrete Risks'!C6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2031)): "'Discrete Risks'!D6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2032)): "'Discrete Risks'!E6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2033)): "'Discrete Risks'!F6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2034)): "'Discrete Risks'!G6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2035)): "'Discrete Risks'!H6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2036)): "'Discrete Risks'!I6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2037)): "'Discrete Risks'!J6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2038)): "'Discrete Risks'!K6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2039)): "'Discrete Risks'!L6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2040)): "'Discrete Risks'!M6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2041)): "'Discrete Risks'!N6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2042)): "'Discrete Risks'!O6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2043)): "'Discrete Risks'!P6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2044)): "'Discrete Risks'!Q6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2045)): "'Discrete Risks'!R6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2046)): "'Discrete Risks'!S6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2047)): "'Discrete Risks'!T6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2048)): "'Discrete Risks'!U6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2049)): "'Discrete Risks'!V6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2050)): "'Discrete Risks'!W6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2051)): "'Discrete Risks'!X6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2052)): "'Discrete Risks'!Y6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2053)): "'Discrete Risks'!Z6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2054)): "'Discrete Risks'!AA6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2055)): "'Discrete Risks'!AB6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2056)): "'Discrete Risks'!AC6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2057)): "'Discrete Risks'!AD6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2058)): "'Discrete Risks'!AE6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2059)): "'Discrete Risks'!AF6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2060)): "'Discrete Risks'!AG6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2061)): "'Discrete Risks'!AH6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2062)): "'Discrete Risks'!AI6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2063)): "'Discrete Risks'!AJ6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2064)): "'Discrete Risks'!AK6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2065)): "'Discrete Risks'!AL6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2066)): "'Discrete Risks'!AM6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2067)): "'Discrete Risks'!AN6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2068)): "'Discrete Risks'!AO6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2069)): "'Discrete Risks'!AP6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2070)): "'Discrete Risks'!AQ6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2071)): "'Discrete Risks'!AR6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2072)): "'Discrete Risks'!AS6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2073)): "'Discrete Risks'!AT6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2074)): "'Discrete Risks'!AU6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2075)): "'Discrete Risks'!AV6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2076)): "'Discrete Risks'!AW6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2077)): "'Discrete Risks'!AX6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2078)): "'Discrete Risks'!AY6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2079)): "'Discrete Risks'!AZ6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2080)): "'Discrete Risks'!BA6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2081)): "'Discrete Risks'!BB6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2082)): "'Discrete Risks'!BC6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2083)): "'Discrete Risks'!BD6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2084)): "'Discrete Risks'!BE6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2085)): "'Discrete Risks'!BF6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2086)): "'Discrete Risks'!BG6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2087)): "'Discrete Risks'!BH6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2088)): "'Discrete Risks'!BI6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2089)): "'Discrete Risks'!BJ6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2090)): "'Discrete Risks'!BK6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2091)): "'Discrete Risks'!BL6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2092)): "'Discrete Risks'!BM6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2093)): "'Discrete Risks'!BN6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2094)): "'Discrete Risks'!BO6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2095)): "'Discrete Risks'!BP6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2096)): "'Discrete Risks'!BQ6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2097)): "'Discrete Risks'!BR6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2098)): "'Discrete Risks'!BS6",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2099)): "'Discrete Risks'!BT6",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2030)): "'Discrete Risks'!C8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2031)): "'Discrete Risks'!D8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2032)): "'Discrete Risks'!E8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2033)): "'Discrete Risks'!F8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2034)): "'Discrete Risks'!G8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2035)): "'Discrete Risks'!H8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2036)): "'Discrete Risks'!I8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2037)): "'Discrete Risks'!J8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2038)): "'Discrete Risks'!K8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2039)): "'Discrete Risks'!L8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2040)): "'Discrete Risks'!M8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2041)): "'Discrete Risks'!N8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2042)): "'Discrete Risks'!O8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2043)): "'Discrete Risks'!P8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2044)): "'Discrete Risks'!Q8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2045)): "'Discrete Risks'!R8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2046)): "'Discrete Risks'!S8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2047)): "'Discrete Risks'!T8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2048)): "'Discrete Risks'!U8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2049)): "'Discrete Risks'!V8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2050)): "'Discrete Risks'!W8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2051)): "'Discrete Risks'!X8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2052)): "'Discrete Risks'!Y8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2053)): "'Discrete Risks'!Z8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2054)): "'Discrete Risks'!AA8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2055)): "'Discrete Risks'!AB8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2056)): "'Discrete Risks'!AC8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2057)): "'Discrete Risks'!AD8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2058)): "'Discrete Risks'!AE8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2059)): "'Discrete Risks'!AF8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2060)): "'Discrete Risks'!AG8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2061)): "'Discrete Risks'!AH8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2062)): "'Discrete Risks'!AI8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2063)): "'Discrete Risks'!AJ8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2064)): "'Discrete Risks'!AK8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2065)): "'Discrete Risks'!AL8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2066)): "'Discrete Risks'!AM8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2067)): "'Discrete Risks'!AN8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2068)): "'Discrete Risks'!AO8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2069)): "'Discrete Risks'!AP8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2070)): "'Discrete Risks'!AQ8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2071)): "'Discrete Risks'!AR8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2072)): "'Discrete Risks'!AS8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2073)): "'Discrete Risks'!AT8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2074)): "'Discrete Risks'!AU8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2075)): "'Discrete Risks'!AV8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2076)): "'Discrete Risks'!AW8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2077)): "'Discrete Risks'!AX8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2078)): "'Discrete Risks'!AY8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2079)): "'Discrete Risks'!AZ8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2080)): "'Discrete Risks'!BA8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2081)): "'Discrete Risks'!BB8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2082)): "'Discrete Risks'!BC8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2083)): "'Discrete Risks'!BD8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2084)): "'Discrete Risks'!BE8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2085)): "'Discrete Risks'!BF8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2086)): "'Discrete Risks'!BG8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2087)): "'Discrete Risks'!BH8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2088)): "'Discrete Risks'!BI8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2089)): "'Discrete Risks'!BJ8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2090)): "'Discrete Risks'!BK8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2091)): "'Discrete Risks'!BL8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2092)): "'Discrete Risks'!BM8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2093)): "'Discrete Risks'!BN8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2094)): "'Discrete Risks'!BO8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2095)): "'Discrete Risks'!BP8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2096)): "'Discrete Risks'!BQ8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2097)): "'Discrete Risks'!BR8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2098)): "'Discrete Risks'!BS8",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2099)): "'Discrete Risks'!BT8",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2030)): "'Discrete Risks'!C10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2031)): "'Discrete Risks'!D10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2032)): "'Discrete Risks'!E10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2033)): "'Discrete Risks'!F10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2034)): "'Discrete Risks'!G10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2035)): "'Discrete Risks'!H10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2036)): "'Discrete Risks'!I10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2037)): "'Discrete Risks'!J10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2038)): "'Discrete Risks'!K10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2039)): "'Discrete Risks'!L10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2040)): "'Discrete Risks'!M10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2041)): "'Discrete Risks'!N10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2042)): "'Discrete Risks'!O10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2043)): "'Discrete Risks'!P10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2044)): "'Discrete Risks'!Q10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2045)): "'Discrete Risks'!R10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2046)): "'Discrete Risks'!S10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2047)): "'Discrete Risks'!T10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2048)): "'Discrete Risks'!U10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2049)): "'Discrete Risks'!V10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2050)): "'Discrete Risks'!W10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2051)): "'Discrete Risks'!X10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2052)): "'Discrete Risks'!Y10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2053)): "'Discrete Risks'!Z10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2054)): "'Discrete Risks'!AA10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2055)): "'Discrete Risks'!AB10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2056)): "'Discrete Risks'!AC10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2057)): "'Discrete Risks'!AD10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2058)): "'Discrete Risks'!AE10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2059)): "'Discrete Risks'!AF10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2060)): "'Discrete Risks'!AG10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2061)): "'Discrete Risks'!AH10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2062)): "'Discrete Risks'!AI10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2063)): "'Discrete Risks'!AJ10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2064)): "'Discrete Risks'!AK10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2065)): "'Discrete Risks'!AL10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2066)): "'Discrete Risks'!AM10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2067)): "'Discrete Risks'!AN10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2068)): "'Discrete Risks'!AO10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2069)): "'Discrete Risks'!AP10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2070)): "'Discrete Risks'!AQ10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2071)): "'Discrete Risks'!AR10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2072)): "'Discrete Risks'!AS10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2073)): "'Discrete Risks'!AT10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2074)): "'Discrete Risks'!AU10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2075)): "'Discrete Risks'!AV10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2076)): "'Discrete Risks'!AW10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2077)): "'Discrete Risks'!AX10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2078)): "'Discrete Risks'!AY10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2079)): "'Discrete Risks'!AZ10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2080)): "'Discrete Risks'!BA10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2081)): "'Discrete Risks'!BB10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2082)): "'Discrete Risks'!BC10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2083)): "'Discrete Risks'!BD10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2084)): "'Discrete Risks'!BE10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2085)): "'Discrete Risks'!BF10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2086)): "'Discrete Risks'!BG10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2087)): "'Discrete Risks'!BH10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2088)): "'Discrete Risks'!BI10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2089)): "'Discrete Risks'!BJ10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2090)): "'Discrete Risks'!BK10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2091)): "'Discrete Risks'!BL10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2092)): "'Discrete Risks'!BM10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2093)): "'Discrete Risks'!BN10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2094)): "'Discrete Risks'!BO10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2095)): "'Discrete Risks'!BP10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2096)): "'Discrete Risks'!BQ10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2097)): "'Discrete Risks'!BR10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2098)): "'Discrete Risks'!BS10",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2099)): "'Discrete Risks'!BT10",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2030)): "'Discrete Risks'!C12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2031)): "'Discrete Risks'!D12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2032)): "'Discrete Risks'!E12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2033)): "'Discrete Risks'!F12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2034)): "'Discrete Risks'!G12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2035)): "'Discrete Risks'!H12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2036)): "'Discrete Risks'!I12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2037)): "'Discrete Risks'!J12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2038)): "'Discrete Risks'!K12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2039)): "'Discrete Risks'!L12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2040)): "'Discrete Risks'!M12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2041)): "'Discrete Risks'!N12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2042)): "'Discrete Risks'!O12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2043)): "'Discrete Risks'!P12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2044)): "'Discrete Risks'!Q12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2045)): "'Discrete Risks'!R12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2046)): "'Discrete Risks'!S12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2047)): "'Discrete Risks'!T12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2048)): "'Discrete Risks'!U12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2049)): "'Discrete Risks'!V12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2050)): "'Discrete Risks'!W12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2051)): "'Discrete Risks'!X12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2052)): "'Discrete Risks'!Y12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2053)): "'Discrete Risks'!Z12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2054)): "'Discrete Risks'!AA12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2055)): "'Discrete Risks'!AB12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2056)): "'Discrete Risks'!AC12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2057)): "'Discrete Risks'!AD12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2058)): "'Discrete Risks'!AE12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2059)): "'Discrete Risks'!AF12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2060)): "'Discrete Risks'!AG12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2061)): "'Discrete Risks'!AH12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2062)): "'Discrete Risks'!AI12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2063)): "'Discrete Risks'!AJ12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2064)): "'Discrete Risks'!AK12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2065)): "'Discrete Risks'!AL12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2066)): "'Discrete Risks'!AM12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2067)): "'Discrete Risks'!AN12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2068)): "'Discrete Risks'!AO12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2069)): "'Discrete Risks'!AP12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2070)): "'Discrete Risks'!AQ12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2071)): "'Discrete Risks'!AR12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2072)): "'Discrete Risks'!AS12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2073)): "'Discrete Risks'!AT12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2074)): "'Discrete Risks'!AU12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2075)): "'Discrete Risks'!AV12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2076)): "'Discrete Risks'!AW12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2077)): "'Discrete Risks'!AX12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2078)): "'Discrete Risks'!AY12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2079)): "'Discrete Risks'!AZ12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2080)): "'Discrete Risks'!BA12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2081)): "'Discrete Risks'!BB12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2082)): "'Discrete Risks'!BC12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2083)): "'Discrete Risks'!BD12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2084)): "'Discrete Risks'!BE12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2085)): "'Discrete Risks'!BF12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2086)): "'Discrete Risks'!BG12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2087)): "'Discrete Risks'!BH12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2088)): "'Discrete Risks'!BI12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2089)): "'Discrete Risks'!BJ12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2090)): "'Discrete Risks'!BK12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2091)): "'Discrete Risks'!BL12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2092)): "'Discrete Risks'!BM12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2093)): "'Discrete Risks'!BN12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2094)): "'Discrete Risks'!BO12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2095)): "'Discrete Risks'!BP12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2096)): "'Discrete Risks'!BQ12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2097)): "'Discrete Risks'!BR12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2098)): "'Discrete Risks'!BS12",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2099)): "'Discrete Risks'!BT12",
}

def read_discrete_revenue_shocks(
    ctx: EvalContext,
    *,
    scenario: str,
    time_period: int,
) -> CellValue:
    """Reads discrete revenue shock projections across climate scenarios and time periods.

    Returns a sequence of records containing manually entered revenue shocks, expressed as a percentage of GDP, for each scenario–year pair defined in the Discrete Risks worksheet.
    Each record matches a cell in the revenue-shock section of the Discrete Risks matrix, with scenario labels filled down from column A and column headers providing time periods.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - SCENARIO: Climate scenario label for the discrete revenue shock.
                - TIME_PERIOD: Year when the revenue shock materializes.
                - OBS_VALUE: Revenue loss as a percentage of GDP for the given scenario and year.

    Source binding:
        Workbook range: Discrete Risks!C2:BT13
        Layout: matrix
        Value type: float

    Examples:
        read_discrete_revenue_shocks(ctx=ctx)
    """
    key_tuple = (('SCENARIO', scenario), ('TIME_PERIOD', time_period))
    address = _LEAF_INDEX_DISCRETE_REVENUE_SHOCKS.get(key_tuple)
    if address is None:
        raise ValueError(f"no leaf matches key {dict(key_tuple)!r}")
    return xl_cell(ctx, address)

def read_discrete_revenue_shocks_range(ctx: EvalContext) -> CellValue:
    """Read the discrete climate‑shock revenue loss paths from the Discrete Risks worksheet.

    Returns a list of records, each linking a climate scenario and year to the corresponding revenue shock as a percentage of GDP.
    Each record corresponds to a revenue-shock cell in the interleaved scenario bands in the Discrete Risks worksheet, with scenario labels filled downwards and years taken from the column headers.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - SCENARIO: Climate scenario to which the revenue shock belongs.
                - TIME_PERIOD: Year of the revenue shock.
                - OBS_VALUE: Revenue shock expressed as a percentage of GDP.

    Source binding:
        Workbook range: Discrete Risks!C2:BT13
        Layout: matrix
        Value type: float

    Examples:
        read_discrete_revenue_shocks_range(ctx=ctx)
    """
    return xl_range(ctx, 'Discrete Risks!C2:BT13')

_LEAF_INDEX_DISCRETE_PRIMARY_EXPENDITURE_SHOCKS = {
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2030)): "'Discrete Risks'!C3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2031)): "'Discrete Risks'!D3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2032)): "'Discrete Risks'!E3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2033)): "'Discrete Risks'!F3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2034)): "'Discrete Risks'!G3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2035)): "'Discrete Risks'!H3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2036)): "'Discrete Risks'!I3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2037)): "'Discrete Risks'!J3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2038)): "'Discrete Risks'!K3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2039)): "'Discrete Risks'!L3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2040)): "'Discrete Risks'!M3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2041)): "'Discrete Risks'!N3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2042)): "'Discrete Risks'!O3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2043)): "'Discrete Risks'!P3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2044)): "'Discrete Risks'!Q3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2045)): "'Discrete Risks'!R3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2046)): "'Discrete Risks'!S3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2047)): "'Discrete Risks'!T3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2048)): "'Discrete Risks'!U3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2049)): "'Discrete Risks'!V3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2050)): "'Discrete Risks'!W3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2051)): "'Discrete Risks'!X3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2052)): "'Discrete Risks'!Y3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2053)): "'Discrete Risks'!Z3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2054)): "'Discrete Risks'!AA3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2055)): "'Discrete Risks'!AB3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2056)): "'Discrete Risks'!AC3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2057)): "'Discrete Risks'!AD3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2058)): "'Discrete Risks'!AE3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2059)): "'Discrete Risks'!AF3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2060)): "'Discrete Risks'!AG3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2061)): "'Discrete Risks'!AH3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2062)): "'Discrete Risks'!AI3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2063)): "'Discrete Risks'!AJ3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2064)): "'Discrete Risks'!AK3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2065)): "'Discrete Risks'!AL3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2066)): "'Discrete Risks'!AM3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2067)): "'Discrete Risks'!AN3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2068)): "'Discrete Risks'!AO3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2069)): "'Discrete Risks'!AP3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2070)): "'Discrete Risks'!AQ3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2071)): "'Discrete Risks'!AR3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2072)): "'Discrete Risks'!AS3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2073)): "'Discrete Risks'!AT3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2074)): "'Discrete Risks'!AU3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2075)): "'Discrete Risks'!AV3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2076)): "'Discrete Risks'!AW3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2077)): "'Discrete Risks'!AX3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2078)): "'Discrete Risks'!AY3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2079)): "'Discrete Risks'!AZ3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2080)): "'Discrete Risks'!BA3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2081)): "'Discrete Risks'!BB3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2082)): "'Discrete Risks'!BC3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2083)): "'Discrete Risks'!BD3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2084)): "'Discrete Risks'!BE3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2085)): "'Discrete Risks'!BF3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2086)): "'Discrete Risks'!BG3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2087)): "'Discrete Risks'!BH3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2088)): "'Discrete Risks'!BI3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2089)): "'Discrete Risks'!BJ3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2090)): "'Discrete Risks'!BK3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2091)): "'Discrete Risks'!BL3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2092)): "'Discrete Risks'!BM3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2093)): "'Discrete Risks'!BN3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2094)): "'Discrete Risks'!BO3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2095)): "'Discrete Risks'!BP3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2096)): "'Discrete Risks'!BQ3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2097)): "'Discrete Risks'!BR3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2098)): "'Discrete Risks'!BS3",
    (('SCENARIO', 'Paris'), ('TIME_PERIOD', 2099)): "'Discrete Risks'!BT3",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2030)): "'Discrete Risks'!C5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2031)): "'Discrete Risks'!D5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2032)): "'Discrete Risks'!E5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2033)): "'Discrete Risks'!F5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2034)): "'Discrete Risks'!G5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2035)): "'Discrete Risks'!H5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2036)): "'Discrete Risks'!I5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2037)): "'Discrete Risks'!J5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2038)): "'Discrete Risks'!K5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2039)): "'Discrete Risks'!L5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2040)): "'Discrete Risks'!M5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2041)): "'Discrete Risks'!N5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2042)): "'Discrete Risks'!O5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2043)): "'Discrete Risks'!P5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2044)): "'Discrete Risks'!Q5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2045)): "'Discrete Risks'!R5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2046)): "'Discrete Risks'!S5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2047)): "'Discrete Risks'!T5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2048)): "'Discrete Risks'!U5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2049)): "'Discrete Risks'!V5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2050)): "'Discrete Risks'!W5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2051)): "'Discrete Risks'!X5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2052)): "'Discrete Risks'!Y5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2053)): "'Discrete Risks'!Z5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2054)): "'Discrete Risks'!AA5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2055)): "'Discrete Risks'!AB5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2056)): "'Discrete Risks'!AC5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2057)): "'Discrete Risks'!AD5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2058)): "'Discrete Risks'!AE5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2059)): "'Discrete Risks'!AF5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2060)): "'Discrete Risks'!AG5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2061)): "'Discrete Risks'!AH5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2062)): "'Discrete Risks'!AI5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2063)): "'Discrete Risks'!AJ5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2064)): "'Discrete Risks'!AK5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2065)): "'Discrete Risks'!AL5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2066)): "'Discrete Risks'!AM5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2067)): "'Discrete Risks'!AN5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2068)): "'Discrete Risks'!AO5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2069)): "'Discrete Risks'!AP5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2070)): "'Discrete Risks'!AQ5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2071)): "'Discrete Risks'!AR5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2072)): "'Discrete Risks'!AS5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2073)): "'Discrete Risks'!AT5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2074)): "'Discrete Risks'!AU5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2075)): "'Discrete Risks'!AV5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2076)): "'Discrete Risks'!AW5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2077)): "'Discrete Risks'!AX5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2078)): "'Discrete Risks'!AY5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2079)): "'Discrete Risks'!AZ5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2080)): "'Discrete Risks'!BA5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2081)): "'Discrete Risks'!BB5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2082)): "'Discrete Risks'!BC5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2083)): "'Discrete Risks'!BD5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2084)): "'Discrete Risks'!BE5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2085)): "'Discrete Risks'!BF5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2086)): "'Discrete Risks'!BG5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2087)): "'Discrete Risks'!BH5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2088)): "'Discrete Risks'!BI5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2089)): "'Discrete Risks'!BJ5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2090)): "'Discrete Risks'!BK5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2091)): "'Discrete Risks'!BL5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2092)): "'Discrete Risks'!BM5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2093)): "'Discrete Risks'!BN5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2094)): "'Discrete Risks'!BO5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2095)): "'Discrete Risks'!BP5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2096)): "'Discrete Risks'!BQ5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2097)): "'Discrete Risks'!BR5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2098)): "'Discrete Risks'!BS5",
    (('SCENARIO', 'Moderate'), ('TIME_PERIOD', 2099)): "'Discrete Risks'!BT5",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2030)): "'Discrete Risks'!C7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2031)): "'Discrete Risks'!D7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2032)): "'Discrete Risks'!E7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2033)): "'Discrete Risks'!F7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2034)): "'Discrete Risks'!G7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2035)): "'Discrete Risks'!H7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2036)): "'Discrete Risks'!I7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2037)): "'Discrete Risks'!J7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2038)): "'Discrete Risks'!K7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2039)): "'Discrete Risks'!L7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2040)): "'Discrete Risks'!M7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2041)): "'Discrete Risks'!N7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2042)): "'Discrete Risks'!O7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2043)): "'Discrete Risks'!P7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2044)): "'Discrete Risks'!Q7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2045)): "'Discrete Risks'!R7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2046)): "'Discrete Risks'!S7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2047)): "'Discrete Risks'!T7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2048)): "'Discrete Risks'!U7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2049)): "'Discrete Risks'!V7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2050)): "'Discrete Risks'!W7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2051)): "'Discrete Risks'!X7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2052)): "'Discrete Risks'!Y7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2053)): "'Discrete Risks'!Z7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2054)): "'Discrete Risks'!AA7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2055)): "'Discrete Risks'!AB7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2056)): "'Discrete Risks'!AC7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2057)): "'Discrete Risks'!AD7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2058)): "'Discrete Risks'!AE7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2059)): "'Discrete Risks'!AF7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2060)): "'Discrete Risks'!AG7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2061)): "'Discrete Risks'!AH7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2062)): "'Discrete Risks'!AI7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2063)): "'Discrete Risks'!AJ7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2064)): "'Discrete Risks'!AK7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2065)): "'Discrete Risks'!AL7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2066)): "'Discrete Risks'!AM7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2067)): "'Discrete Risks'!AN7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2068)): "'Discrete Risks'!AO7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2069)): "'Discrete Risks'!AP7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2070)): "'Discrete Risks'!AQ7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2071)): "'Discrete Risks'!AR7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2072)): "'Discrete Risks'!AS7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2073)): "'Discrete Risks'!AT7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2074)): "'Discrete Risks'!AU7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2075)): "'Discrete Risks'!AV7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2076)): "'Discrete Risks'!AW7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2077)): "'Discrete Risks'!AX7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2078)): "'Discrete Risks'!AY7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2079)): "'Discrete Risks'!AZ7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2080)): "'Discrete Risks'!BA7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2081)): "'Discrete Risks'!BB7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2082)): "'Discrete Risks'!BC7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2083)): "'Discrete Risks'!BD7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2084)): "'Discrete Risks'!BE7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2085)): "'Discrete Risks'!BF7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2086)): "'Discrete Risks'!BG7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2087)): "'Discrete Risks'!BH7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2088)): "'Discrete Risks'!BI7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2089)): "'Discrete Risks'!BJ7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2090)): "'Discrete Risks'!BK7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2091)): "'Discrete Risks'!BL7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2092)): "'Discrete Risks'!BM7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2093)): "'Discrete Risks'!BN7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2094)): "'Discrete Risks'!BO7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2095)): "'Discrete Risks'!BP7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2096)): "'Discrete Risks'!BQ7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2097)): "'Discrete Risks'!BR7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2098)): "'Discrete Risks'!BS7",
    (('SCENARIO', 'High'), ('TIME_PERIOD', 2099)): "'Discrete Risks'!BT7",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2030)): "'Discrete Risks'!C9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2031)): "'Discrete Risks'!D9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2032)): "'Discrete Risks'!E9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2033)): "'Discrete Risks'!F9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2034)): "'Discrete Risks'!G9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2035)): "'Discrete Risks'!H9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2036)): "'Discrete Risks'!I9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2037)): "'Discrete Risks'!J9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2038)): "'Discrete Risks'!K9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2039)): "'Discrete Risks'!L9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2040)): "'Discrete Risks'!M9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2041)): "'Discrete Risks'!N9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2042)): "'Discrete Risks'!O9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2043)): "'Discrete Risks'!P9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2044)): "'Discrete Risks'!Q9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2045)): "'Discrete Risks'!R9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2046)): "'Discrete Risks'!S9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2047)): "'Discrete Risks'!T9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2048)): "'Discrete Risks'!U9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2049)): "'Discrete Risks'!V9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2050)): "'Discrete Risks'!W9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2051)): "'Discrete Risks'!X9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2052)): "'Discrete Risks'!Y9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2053)): "'Discrete Risks'!Z9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2054)): "'Discrete Risks'!AA9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2055)): "'Discrete Risks'!AB9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2056)): "'Discrete Risks'!AC9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2057)): "'Discrete Risks'!AD9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2058)): "'Discrete Risks'!AE9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2059)): "'Discrete Risks'!AF9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2060)): "'Discrete Risks'!AG9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2061)): "'Discrete Risks'!AH9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2062)): "'Discrete Risks'!AI9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2063)): "'Discrete Risks'!AJ9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2064)): "'Discrete Risks'!AK9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2065)): "'Discrete Risks'!AL9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2066)): "'Discrete Risks'!AM9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2067)): "'Discrete Risks'!AN9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2068)): "'Discrete Risks'!AO9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2069)): "'Discrete Risks'!AP9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2070)): "'Discrete Risks'!AQ9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2071)): "'Discrete Risks'!AR9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2072)): "'Discrete Risks'!AS9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2073)): "'Discrete Risks'!AT9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2074)): "'Discrete Risks'!AU9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2075)): "'Discrete Risks'!AV9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2076)): "'Discrete Risks'!AW9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2077)): "'Discrete Risks'!AX9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2078)): "'Discrete Risks'!AY9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2079)): "'Discrete Risks'!AZ9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2080)): "'Discrete Risks'!BA9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2081)): "'Discrete Risks'!BB9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2082)): "'Discrete Risks'!BC9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2083)): "'Discrete Risks'!BD9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2084)): "'Discrete Risks'!BE9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2085)): "'Discrete Risks'!BF9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2086)): "'Discrete Risks'!BG9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2087)): "'Discrete Risks'!BH9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2088)): "'Discrete Risks'!BI9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2089)): "'Discrete Risks'!BJ9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2090)): "'Discrete Risks'!BK9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2091)): "'Discrete Risks'!BL9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2092)): "'Discrete Risks'!BM9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2093)): "'Discrete Risks'!BN9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2094)): "'Discrete Risks'!BO9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2095)): "'Discrete Risks'!BP9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2096)): "'Discrete Risks'!BQ9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2097)): "'Discrete Risks'!BR9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2098)): "'Discrete Risks'!BS9",
    (('SCENARIO', 'Hot'), ('TIME_PERIOD', 2099)): "'Discrete Risks'!BT9",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2030)): "'Discrete Risks'!C11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2031)): "'Discrete Risks'!D11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2032)): "'Discrete Risks'!E11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2033)): "'Discrete Risks'!F11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2034)): "'Discrete Risks'!G11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2035)): "'Discrete Risks'!H11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2036)): "'Discrete Risks'!I11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2037)): "'Discrete Risks'!J11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2038)): "'Discrete Risks'!K11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2039)): "'Discrete Risks'!L11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2040)): "'Discrete Risks'!M11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2041)): "'Discrete Risks'!N11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2042)): "'Discrete Risks'!O11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2043)): "'Discrete Risks'!P11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2044)): "'Discrete Risks'!Q11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2045)): "'Discrete Risks'!R11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2046)): "'Discrete Risks'!S11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2047)): "'Discrete Risks'!T11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2048)): "'Discrete Risks'!U11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2049)): "'Discrete Risks'!V11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2050)): "'Discrete Risks'!W11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2051)): "'Discrete Risks'!X11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2052)): "'Discrete Risks'!Y11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2053)): "'Discrete Risks'!Z11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2054)): "'Discrete Risks'!AA11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2055)): "'Discrete Risks'!AB11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2056)): "'Discrete Risks'!AC11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2057)): "'Discrete Risks'!AD11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2058)): "'Discrete Risks'!AE11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2059)): "'Discrete Risks'!AF11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2060)): "'Discrete Risks'!AG11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2061)): "'Discrete Risks'!AH11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2062)): "'Discrete Risks'!AI11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2063)): "'Discrete Risks'!AJ11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2064)): "'Discrete Risks'!AK11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2065)): "'Discrete Risks'!AL11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2066)): "'Discrete Risks'!AM11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2067)): "'Discrete Risks'!AN11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2068)): "'Discrete Risks'!AO11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2069)): "'Discrete Risks'!AP11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2070)): "'Discrete Risks'!AQ11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2071)): "'Discrete Risks'!AR11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2072)): "'Discrete Risks'!AS11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2073)): "'Discrete Risks'!AT11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2074)): "'Discrete Risks'!AU11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2075)): "'Discrete Risks'!AV11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2076)): "'Discrete Risks'!AW11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2077)): "'Discrete Risks'!AX11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2078)): "'Discrete Risks'!AY11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2079)): "'Discrete Risks'!AZ11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2080)): "'Discrete Risks'!BA11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2081)): "'Discrete Risks'!BB11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2082)): "'Discrete Risks'!BC11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2083)): "'Discrete Risks'!BD11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2084)): "'Discrete Risks'!BE11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2085)): "'Discrete Risks'!BF11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2086)): "'Discrete Risks'!BG11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2087)): "'Discrete Risks'!BH11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2088)): "'Discrete Risks'!BI11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2089)): "'Discrete Risks'!BJ11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2090)): "'Discrete Risks'!BK11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2091)): "'Discrete Risks'!BL11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2092)): "'Discrete Risks'!BM11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2093)): "'Discrete Risks'!BN11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2094)): "'Discrete Risks'!BO11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2095)): "'Discrete Risks'!BP11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2096)): "'Discrete Risks'!BQ11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2097)): "'Discrete Risks'!BR11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2098)): "'Discrete Risks'!BS11",
    (('SCENARIO', 'Hot adapted'), ('TIME_PERIOD', 2099)): "'Discrete Risks'!BT11",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2030)): "'Discrete Risks'!C13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2031)): "'Discrete Risks'!D13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2032)): "'Discrete Risks'!E13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2033)): "'Discrete Risks'!F13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2034)): "'Discrete Risks'!G13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2035)): "'Discrete Risks'!H13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2036)): "'Discrete Risks'!I13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2037)): "'Discrete Risks'!J13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2038)): "'Discrete Risks'!K13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2039)): "'Discrete Risks'!L13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2040)): "'Discrete Risks'!M13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2041)): "'Discrete Risks'!N13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2042)): "'Discrete Risks'!O13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2043)): "'Discrete Risks'!P13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2044)): "'Discrete Risks'!Q13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2045)): "'Discrete Risks'!R13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2046)): "'Discrete Risks'!S13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2047)): "'Discrete Risks'!T13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2048)): "'Discrete Risks'!U13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2049)): "'Discrete Risks'!V13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2050)): "'Discrete Risks'!W13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2051)): "'Discrete Risks'!X13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2052)): "'Discrete Risks'!Y13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2053)): "'Discrete Risks'!Z13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2054)): "'Discrete Risks'!AA13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2055)): "'Discrete Risks'!AB13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2056)): "'Discrete Risks'!AC13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2057)): "'Discrete Risks'!AD13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2058)): "'Discrete Risks'!AE13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2059)): "'Discrete Risks'!AF13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2060)): "'Discrete Risks'!AG13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2061)): "'Discrete Risks'!AH13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2062)): "'Discrete Risks'!AI13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2063)): "'Discrete Risks'!AJ13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2064)): "'Discrete Risks'!AK13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2065)): "'Discrete Risks'!AL13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2066)): "'Discrete Risks'!AM13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2067)): "'Discrete Risks'!AN13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2068)): "'Discrete Risks'!AO13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2069)): "'Discrete Risks'!AP13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2070)): "'Discrete Risks'!AQ13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2071)): "'Discrete Risks'!AR13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2072)): "'Discrete Risks'!AS13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2073)): "'Discrete Risks'!AT13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2074)): "'Discrete Risks'!AU13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2075)): "'Discrete Risks'!AV13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2076)): "'Discrete Risks'!AW13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2077)): "'Discrete Risks'!AX13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2078)): "'Discrete Risks'!AY13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2079)): "'Discrete Risks'!AZ13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2080)): "'Discrete Risks'!BA13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2081)): "'Discrete Risks'!BB13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2082)): "'Discrete Risks'!BC13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2083)): "'Discrete Risks'!BD13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2084)): "'Discrete Risks'!BE13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2085)): "'Discrete Risks'!BF13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2086)): "'Discrete Risks'!BG13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2087)): "'Discrete Risks'!BH13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2088)): "'Discrete Risks'!BI13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2089)): "'Discrete Risks'!BJ13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2090)): "'Discrete Risks'!BK13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2091)): "'Discrete Risks'!BL13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2092)): "'Discrete Risks'!BM13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2093)): "'Discrete Risks'!BN13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2094)): "'Discrete Risks'!BO13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2095)): "'Discrete Risks'!BP13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2096)): "'Discrete Risks'!BQ13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2097)): "'Discrete Risks'!BR13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2098)): "'Discrete Risks'!BS13",
    (('SCENARIO', 'Hot unadapted'), ('TIME_PERIOD', 2099)): "'Discrete Risks'!BT13",
}

def read_discrete_primary_expenditure_shocks(
    ctx: EvalContext,
    *,
    scenario: str,
    time_period: int,
) -> CellValue:
    """Read the user-specified discrete primary expenditure shock paths across climate scenarios and years.

    Return the manual primary expenditure shock entries, as a percentage of GDP, for each climate scenario and year defined in the Discrete Risks worksheet.
    Each record corresponds to a scenario–year pair; the primary expenditure shock is extracted from the interleaved grouped-row matrix.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - SCENARIO: Climate scenario label for the discrete primary expenditure shock.
                - TIME_PERIOD: Year of the discrete primary expenditure shock.
                - OBS_VALUE: Primary expenditure shock, expressed as a percentage of GDP.

    Source binding:
        Workbook range: Discrete Risks!C2:BT13
        Layout: matrix
        Value type: float

    Examples:
        read_discrete_primary_expenditure_shocks(ctx=ctx)
    """
    key_tuple = (('SCENARIO', scenario), ('TIME_PERIOD', time_period))
    address = _LEAF_INDEX_DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.get(key_tuple)
    if address is None:
        raise ValueError(f"no leaf matches key {dict(key_tuple)!r}")
    return xl_cell(ctx, address)

def read_discrete_primary_expenditure_shocks_range(ctx: EvalContext) -> CellValue:
    """Reads user-registered primary-expenditure shock paths from the Discrete Risks worksheet.

    Returns records that capture hypothetical fiscal impacts of discrete risks as primary-expenditure additions or reductions under each climate scenario.
    Each record corresponds to one data cell in the primary-expenditure rows of the Discrete Risks matrix, with SCENARIO derived from the row band label and TIME_PERIOD from the column header.

    Args:
        ctx (EvalContext | None): Existing evaluation context, if available.
        inputs (dict[str, object] | None): Optional input map when ctx is omitted.

    Returns:
        Records: Computed output records.
            Required record fields:
                - SCENARIO: Climate scenario to which the shock path belongs.
                - TIME_PERIOD: Year in which the shock occurs.
                - OBS_VALUE: Magnitude of the shock expressed as a percentage of GDP.

    Source binding:
        Workbook range: Discrete Risks!C2:BT13
        Layout: matrix
        Value type: float

    Examples:
        read_discrete_primary_expenditure_shocks_range(ctx=ctx)
    """
    return xl_range(ctx, 'Discrete Risks!C2:BT13')
