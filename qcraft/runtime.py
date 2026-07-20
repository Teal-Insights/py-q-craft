"""Standalone runtime for generated Excel formula code."""

from __future__ import annotations

import warnings
from collections.abc import Callable, Hashable, Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from typing import NoReturn, TypeAlias, cast

import fastpyxl.utils.cell
import math

class CircularReferenceWarning(RuntimeWarning):
    """Warning emitted when a circular reference is encountered (default Excel mode)."""

HelperCacheKey: TypeAlias = tuple[Hashable, tuple[tuple[str, Hashable], ...]]

@dataclass(slots=True)
class EvalContextBase:
    """Per-run evaluation state without dependency-tracking fields."""

    inputs: dict[str, CellValue]
    resolver: Callable[[str], Callable[[EvalContext], CellValue] | None]
    cache: dict[str, CellValue] = field(default_factory=dict)
    computing: set[str] = field(default_factory=set)
    circular_warning_roots: set[str] = field(default_factory=set)
    helper_cache: dict[HelperCacheKey, CellValue] = field(default_factory=dict)
    helper_computing: set[HelperCacheKey] = field(default_factory=set)
    iterative_enabled: bool = False
    iterate_count: int = 100
    iterate_delta: float = 0.001
    iteration_values: dict[str, CellValue] = field(default_factory=dict)

@dataclass(slots=True)
class EvalContext(EvalContextBase):
    """Per-run evaluation state with dependency tracking for input invalidation."""

    deps: dict[str, set[str]] = field(default_factory=dict)
    reverse_deps: dict[str, set[str]] = field(default_factory=dict)
    stack: list[str] = field(default_factory=list)

    def _record_dependency(self, parent: str, child: str) -> None:
        if parent == child:
            return
        self.deps.setdefault(parent, set()).add(child)
        self.reverse_deps.setdefault(child, set()).add(parent)

    def invalidate(self, addresses: Iterable[str]) -> None:
        """Invalidate cached values for the given addresses and their dependents.

        Helper memos are not address-dep-tracked, so any address invalidation
        clears `helper_cache` and `helper_computing` entirely.
        """
        self.helper_cache.clear()
        self.helper_computing.clear()

        to_visit = list(addresses)
        seen: set[str] = set()
        while to_visit:
            addr = to_visit.pop()
            if addr in seen:
                continue
            seen.add(addr)

            self.cache.pop(addr, None)
            self.circular_warning_roots.discard(addr)
            self.computing.discard(addr)

            dependents = list(self.reverse_deps.get(addr, set()))
            to_visit.extend(dependents)

            for dep in self.deps.get(addr, set()):
                parents = self.reverse_deps.get(dep)
                if parents is not None:
                    parents.discard(addr)
                    if not parents:
                        self.reverse_deps.pop(dep, None)

            self.deps.pop(addr, None)
            self.reverse_deps.pop(addr, None)

    def set_inputs(self, inputs: dict[str, CellValue]) -> None:
        """Update input values and invalidate dependent cached results."""
        changed = [k for k, v in inputs.items() if self.inputs.get(k) != v]
        self.inputs.update(inputs)
        if changed:
            self.invalidate(changed)

NormalizedAddress: TypeAlias = str

class XlError(StrEnum):
    VALUE = "#VALUE!"
    REF = "#REF!"
    DIV = "#DIV/0!"
    NA = "#N/A"
    NAME = "#NAME?"
    NUM = "#NUM!"
    NULL = "#NULL!"

    @classmethod
    def from_text(cls, value: str) -> XlError | None:
        upper = value.strip().upper()
        for err in cls:
            if err.value == upper:
                return err
        return None

Scalar: TypeAlias = float | int | str | bool | XlError | None

class XlErrorException(Exception):
    """Exception form of an Excel error code.

    The exported runtime raises Excel errors as exceptions; the evaluator keeps
    `XlError` sentinel values and never raises this type.
    """

    code: XlError

    def __init__(self, code: XlError) -> None:
        """Initialize the exception with an Excel error code."""
        if not isinstance(code, XlError):
            raise TypeError(f"Expected XlError, got {type(code).__name__}")
        self.code = code
        super().__init__(code.value)

_EXCEL_EPOCH = datetime(1899, 12, 30)

def _escape_sheet_for_formula(sheet: str) -> str:
    """Escape apostrophes for use inside quoted sheet names."""
    return sheet.replace("'", "''")

def _format_general_number(value: float | int) -> str:
    f = float(value)
    if f.is_integer():
        return str(int(f))
    return str(f)

def _raise_error(code: XlError) -> XlErrorException:
    """Build the exception for an Excel error code (callers raise the result)."""
    return XlErrorException(code)

def _raise_if_error_value(value: CellValue) -> CellValue:
    """Surface Excel error values as raised exceptions at the cell boundary."""
    if isinstance(value, XlError):
        raise XlErrorException(value)
    return value

def datetime_to_excel_serial(value: datetime) -> float:
    """Convert a naive datetime to an Excel day serial (1900 date system)."""
    naive = value.replace(tzinfo=None) if value.tzinfo is not None else value
    delta = naive - _EXCEL_EPOCH
    return delta.days + (delta.seconds + delta.microseconds / 1_000_000) / 86_400.0

def _try_parse_iso_date_serial(text: str) -> float | None:
    stripped = text.strip()
    if not stripped:
        return None
    try:
        if "T" in stripped or " " in stripped:
            parsed = datetime.fromisoformat(stripped.replace("Z", "+00:00"))
            if parsed.tzinfo is not None:
                parsed = parsed.replace(tzinfo=None)
        else:
            parsed = datetime.combine(date.fromisoformat(stripped), datetime.min.time())
        return datetime_to_excel_serial(parsed)
    except ValueError:
        return None

def excel_casefold(value: str) -> str:
    return value.casefold()

def needs_quoting(sheet: str) -> bool:
    """Return True if a sheet name must be wrapped in single quotes in a formula."""
    return " " in sheet or "-" in sheet or "'" in sheet

def parse_address(address: str) -> tuple[str, str]:
    """Parse a sheet-qualified address into `(sheet, cell_coord)`.

    The returned sheet name has any surrounding single quotes stripped and any
    escaped apostrophes (`''`) unescaped to a single apostrophe.

    Examples:
        >>> parse_address("Sheet1!A1")
        ('Sheet1', 'A1')
        >>> parse_address("'My Sheet'!B2")
        ('My Sheet', 'B2')
        >>> parse_address("'It''s Data'!C3")
        ("It's Data", 'C3')
    """
    if address.startswith("'"):
        i = 1
        while i < len(address):
            if address[i] == "'":
                if i + 1 < len(address) and address[i + 1] == "'":
                    i += 2
                    continue
                break
            i += 1
        sheet = address[1:i].replace("''", "'")
        rest = address[i + 1 :]
        if rest.startswith("!"):
            return sheet, rest[1:]
        raise ValueError(f"Invalid address format: {address}")

    if "!" in address:
        sheet, cell = address.rsplit("!", 1)
        return sheet, cell

    raise ValueError(f"Address must be sheet-qualified: {address}")

def quote_sheet_if_needed(sheet: str) -> str:
    """Return a sheet name quoted for formulas when quoting is required."""
    if not needs_quoting(sheet):
        return sheet
    return "'" + _escape_sheet_for_formula(sheet) + "'"

def format_cell_key(sheet: str, column: str, row: int) -> NormalizedAddress:
    """Format a (sheet, column_letters, row) triple into a canonical address."""
    return f"{quote_sheet_if_needed(sheet)}!{column}{row}"

@dataclass(frozen=True, slots=True)
class Range:
    """Rectangular lazy range with consumer-driven cell access.

    Coordinates passed to `cell`, `row`, `column`, and `view` are 1-based and
    relative to this range, matching Excel function arguments.
    """

    sheet: str
    start_row: int
    start_col: int
    end_row: int
    end_col: int
    # Resolvers may come from evaluation contexts with their own value
    # vocabulary; values are validated/coerced at consumption time.
    _resolver: Callable[[str], FormulaValue] = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        """Validate the rectangular bounds."""
        if self.start_row < 1 or self.start_col < 1:
            raise ValueError("Range coordinates must be positive")
        if self.end_row < self.start_row or self.end_col < self.start_col:
            raise ValueError("Range end must be greater than or equal to start")

    @property
    def shape(self) -> tuple[int, int]:
        """The range shape as `(rows, columns)`."""
        return (self.end_row - self.start_row + 1, self.end_col - self.start_col + 1)

    def cell_addresses(self) -> Iterator[str]:
        """Yield row-major addresses without evaluating cells."""
        for row in range(self.start_row, self.end_row + 1):
            for col in range(self.start_col, self.end_col + 1):
                yield self._address(row, col)

    def cell(self, row: int, col: int) -> FormulaValue:
        """Return a single relative cell value without evaluating siblings.

        Args:
            row: 1-based row within the range.
            col: 1-based column within the range.

        Raises:
            IndexError: If `row` or `col` is outside the range.
            XlErrorException: If the resolved cell is an Excel error.
        """
        self._validate_relative_cell(row, col)
        value = self._resolver(self._address(self.start_row + row - 1, self.start_col + col - 1))
        return self._raise_if_error(value)

    def row(self, row: int) -> Range:
        """Return a lazy view for one relative row."""
        nrows, _ = self.shape
        if row < 1 or row > nrows:
            raise IndexError("Range row is out of bounds")
        absolute_row = self.start_row + row - 1
        return Range(
            self.sheet,
            absolute_row,
            self.start_col,
            absolute_row,
            self.end_col,
            self._resolver,
        )

    def column(self, col: int) -> Range:
        """Return a lazy view for one relative column."""
        _, ncols = self.shape
        if col < 1 or col > ncols:
            raise IndexError("Range column is out of bounds")
        absolute_col = self.start_col + col - 1
        return Range(
            self.sheet,
            self.start_row,
            absolute_col,
            self.end_row,
            absolute_col,
            self._resolver,
        )

    def view(
        self,
        row_start: int = 1,
        row_end: int | None = None,
        col_start: int = 1,
        col_end: int | None = None,
    ) -> Range:
        """Return a lazy rectangular subrange view using relative coordinates."""
        nrows, ncols = self.shape
        row_end = nrows if row_end is None else row_end
        col_end = ncols if col_end is None else col_end
        self._validate_relative_cell(row_start, col_start)
        self._validate_relative_cell(row_end, col_end)
        if row_end < row_start or col_end < col_start:
            raise ValueError("Range view end must be greater than or equal to start")
        return Range(
            self.sheet,
            self.start_row + row_start - 1,
            self.start_col + col_start - 1,
            self.start_row + row_end - 1,
            self.start_col + col_end - 1,
            self._resolver,
        )

    def value_at(self, row: int, col: int) -> FormulaValue:
        """Return a single relative cell value with errors as sentinels.

        Unlike `cell`, Excel errors surface as `XlError` sentinel values (raised
        `XlErrorException`s from the resolver are caught and converted). Range
        consumers that implement Excel skip semantics (lookup scans, criteria
        matching) use this accessor; `cell`/iteration raise instead.
        """
        self._validate_relative_cell(row, col)
        address = self._address(self.start_row + row - 1, self.start_col + col - 1)
        try:
            return self._resolver(address)
        except XlErrorException as exc:
            return exc.code

    def iter_raw(self) -> Iterator[FormulaValue]:
        """Yield raw values (error sentinels included) in row-major order."""
        nrows, ncols = self.shape
        for row in range(1, nrows + 1):
            for col in range(1, ncols + 1):
                yield self.value_at(row, col)

    def rows_raw(self) -> list[list[FormulaValue]]:
        """Materialize the range as nested row lists of raw values."""
        nrows, ncols = self.shape
        return [[self.value_at(r, c) for c in range(1, ncols + 1)] for r in range(1, nrows + 1)]

    def iter_values(self) -> Iterator[FormulaValue]:
        """Yield values in deterministic row-major order."""
        nrows, ncols = self.shape
        for row in range(1, nrows + 1):
            for col in range(1, ncols + 1):
                yield self.cell(row, col)

    def __iter__(self) -> Iterator[FormulaValue]:
        """Yield values in deterministic row-major order."""
        return self.iter_values()

    def _address(self, row: int, col: int) -> str:
        col_letter = fastpyxl.utils.cell.get_column_letter(col)
        return format_cell_key(self.sheet, col_letter, row)

    def _validate_relative_cell(self, row: int, col: int) -> None:
        nrows, ncols = self.shape
        if row < 1 or row > nrows or col < 1 or col > ncols:
            raise IndexError("Range cell is out of bounds")

    @staticmethod
    def _raise_if_error(value: FormulaValue) -> FormulaValue:
        if isinstance(value, XlError):
            raise XlErrorException(value)
        return value

def _format_address(sheet: str, row: int, col: int) -> str:
    return format_cell_key(sheet, fastpyxl.utils.cell.get_column_letter(col), row)

def format_key(sheet: str, cell: str) -> NormalizedAddress:
    """Format a sheet and A1 cell coordinate into a canonical address string."""
    return f"{quote_sheet_if_needed(sheet)}!{cell}"

@dataclass(frozen=True, slots=True)
class ExcelRange:
    """Rectangular worksheet reference geometry for evaluator and export."""

    sheet: str
    start_row: int
    start_col: int
    end_row: int
    end_col: int

    @property
    def shape(self) -> tuple[int, int]:
        """The reference shape as `(rows, columns)`."""
        return (self.end_row - self.start_row + 1, self.end_col - self.start_col + 1)

    def cell_addresses(self) -> Iterator[str]:
        """Yield row-major sheet-qualified addresses without evaluating cells."""
        for r in range(self.start_row, self.end_row + 1):
            for c in range(self.start_col, self.end_col + 1):
                col = fastpyxl.utils.cell.get_column_letter(c)
                yield format_key(self.sheet, f"{col}{r}")

CellValue: TypeAlias = Scalar | ExcelRange | Range | list["CellValue"]

NestedGrid: TypeAlias = list[list[CellValue]]

FormulaValue: TypeAlias = CellValue | NestedGrid

def _as_nested_rows_from_ndarray(value: object) -> list[list[CellValue]] | None:
    """Convert an ndarray-like value to nested lists without importing NumPy.

    Duck-types via ``ndim`` / ``tolist`` so the grid module stays import-light
    for standalone exports that must remain NumPy-free.
    """
    ndim = getattr(value, "ndim", None)
    tolist = getattr(value, "tolist", None)
    if not isinstance(ndim, int) or not callable(tolist):
        return None
    if ndim == 0:
        return None
    raw = tolist()
    if ndim == 1:
        return [[cast(CellValue, cell)] for cell in raw]
    return cast("list[list[CellValue]]", raw)

class Grid:
    """Positional raw-value access over a lazy `Range` or nested-list array."""

    __slots__ = ("nrows", "ncols", "_range", "_rows")

    def __init__(
        self,
        nrows: int,
        ncols: int,
        rng: Range | None,
        rows: list[list[CellValue]] | None,
    ) -> None:
        self.nrows = nrows
        self.ncols = ncols
        self._range = rng
        self._rows = rows

    @staticmethod
    def wrap(value: object) -> Grid | None:
        """Wrap a range/array value; return `None` for scalar values."""
        if isinstance(value, Range):
            nrows, ncols = value.shape
            return Grid(nrows, ncols, value, None)
        ndarray_rows = _as_nested_rows_from_ndarray(value)
        if ndarray_rows is not None:
            if not ndarray_rows:
                ndarray_rows = [[None]]
            return Grid(len(ndarray_rows), len(ndarray_rows[0]), None, ndarray_rows)
        if isinstance(value, (list, tuple)):
            rows = [
                list(row) if isinstance(row, (list, tuple)) else [row]
                for row in cast("list[CellValue]", value)
            ]
            if not rows:
                rows = [[None]]
            return Grid(len(rows), len(rows[0]), None, cast("list[list[CellValue]]", rows))
        return None

    def at(self, row0: int, col0: int) -> Scalar:
        """Return the raw value at a 0-based position (error sentinels included)."""
        if self._range is not None:
            return cast(Scalar, self._range.value_at(row0 + 1, col0 + 1))
        assert self._rows is not None
        return cast(Scalar, self._rows[row0][col0])

    def at_flat(self, index0: int) -> Scalar:
        """Return the raw value at a 0-based row-major flat index."""
        row0, col0 = divmod(index0, self.ncols)
        return self.at(row0, col0)

    @property
    def size(self) -> int:
        """Total cell count."""
        return self.nrows * self.ncols

    def iter_raw(self) -> Iterator[Scalar]:
        """Yield raw values (error sentinels included) in row-major order."""
        for row0 in range(self.nrows):
            for col0 in range(self.ncols):
                yield self.at(row0, col0)

    def row_slice(self, row0: int) -> Range | list[list[CellValue]]:
        """Return one row as a lazy view (`Range` input) or nested list."""
        if self._range is not None:
            return self._range.row(row0 + 1)
        assert self._rows is not None
        return [list(self._rows[row0])]

    def col_slice(self, col0: int) -> Range | list[list[CellValue]]:
        """Return one column as a lazy view (`Range` input) or nested list."""
        if self._range is not None:
            return self._range.column(col0 + 1)
        assert self._rows is not None
        return [[row[col0]] for row in self._rows]

def _as_scalar(value: object) -> Scalar:
    if isinstance(value, (Range, list, tuple)):
        return XlError.VALUE
    if Grid.wrap(value) is not None:
        return XlError.VALUE
    return cast(Scalar, value)

def _raise_if_error(value: object) -> CellValue:
    if isinstance(value, XlError):
        raise _raise_error(value)
    return cast(CellValue, value)

def _range_from_ref_info(ref: ExcelRange | OffsetRefInfo) -> ExcelRange:
    """Normalize generated reference metadata into an `ExcelRange`."""
    if isinstance(ref, ExcelRange):
        return ref
    match ref:
        case (sheet, base_row, base_col):
            return ExcelRange(
                sheet=sheet,
                start_row=base_row,
                start_col=base_col,
                end_row=base_row,
                end_col=base_col,
            )
        case (sheet, base_row, base_col, base_end_row, base_end_col):
            return ExcelRange(
                sheet=sheet,
                start_row=base_row,
                start_col=base_col,
                end_row=base_end_row,
                end_col=base_end_col,
            )
        case _:
            raise XlErrorException(XlError.VALUE)

def as_scalar(value: CellValue) -> Scalar:
    """Collapse range/array values to `#VALUE!` for scalar coercion contexts.

    Keep behavior aligned with `excel_grapher.core.coercions.as_scalar`. This
    module is embedded into standalone exports and cannot import library code.
    """
    if isinstance(value, (Range, ExcelRange, list, tuple)):
        return XlError.VALUE
    return value

def _as_addressing_scalar(value: CellValue | None) -> Scalar | None:
    """Collapse export-runtime values to scalars for shared addressing helpers."""
    if value is None:
        return None
    return as_scalar(value)

def coerce_inputs_dict(values: Mapping[str, object]) -> dict[str, CellValue]:
    """Widen inferred default-input dicts to `dict[str, CellValue]` for `EvalContext`."""
    return cast(dict[str, CellValue], dict(values))

def raise_if_sentinel_float(value: float | XlError) -> float:
    """Return a float result or raise ``XlErrorException`` for an error sentinel."""
    if isinstance(value, XlError):
        raise XlErrorException(value)
    return value

def split_sheet_qualified_address(address: str) -> tuple[str, str] | None:
    """Split `sheet!coord` into `(sheet_name, coord)`.

    Handles quoted sheet names, including Excel's doubled-single-quote escape
    (`'O''Neil'!A1` -> sheet `O'Neil`).

    Returns `None` when *address* has no sheet qualifier (plain `A1`).
    """
    if "!" not in address:
        return None
    try:
        return parse_address(address)
    except ValueError:
        return None

def _parse_sheet_address(address: str) -> tuple[str, str] | None:
    return split_sheet_qualified_address(address)

def _parse_range_address(address: str) -> tuple[str, str, str] | XlError:
    if ":" not in address:
        return XlError.VALUE
    start_text, end_text = address.split(":", 1)
    start = _parse_sheet_address(start_text)
    if start is None:
        return XlError.VALUE
    sheet, start_cell = start
    if "!" in end_text:
        end = _parse_sheet_address(end_text)
        if end is None:
            return XlError.VALUE
        end_sheet, end_cell = end
        if end_sheet != sheet:
            return XlError.VALUE
    else:
        end_cell = end_text
    return sheet, start_cell, end_cell

def to_bool(value: FormulaValue) -> bool | XlError:
    scalar = as_scalar(value)
    if isinstance(scalar, XlError):
        return scalar
    value = cast(CellValue, scalar)
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return float(value) != 0.0
    if isinstance(value, str):
        s = value.strip().upper()
        if s == "":
            return False
        if s == "TRUE":
            return True
        if s == "FALSE":
            return False
        return XlError.VALUE
    return XlError.VALUE

def to_string(value: FormulaValue) -> str:
    scalar = as_scalar(value)
    if isinstance(scalar, XlError):
        return scalar.value
    value = cast(CellValue, scalar)
    if value is None:
        return ""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return _format_general_number(float(value))
    if isinstance(value, str):
        return value
    return str(value)

def try_coerce_string_to_float(text: str) -> float | None:
    """Parse one Excel numeric string; empty/whitespace text fails (`None`)."""
    stripped = text.strip()
    if stripped == "":
        return None
    try:
        return float(stripped)
    except ValueError:
        return _try_parse_iso_date_serial(stripped)

def to_number(value: FormulaValue) -> float | XlError:
    scalar = as_scalar(value)
    if isinstance(scalar, XlError):
        return scalar
    value = cast(CellValue, scalar)
    if value is None:
        return 0.0
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        number = try_coerce_string_to_float(value)
        if number is None:
            return XlError.VALUE
        return number
    return XlError.VALUE

def _compare_values(a: object, b: object) -> int:
    a = _as_scalar(a)
    b = _as_scalar(b)
    an = to_number(a)
    bn = to_number(b)
    if not isinstance(an, XlError) and not isinstance(bn, XlError):
        return -1 if an < bn else 1 if an > bn else 0
    if isinstance(a, str) and isinstance(b, str):
        af = excel_casefold(a)
        bf = excel_casefold(b)
        return -1 if af < bf else 1 if af > bf else 0
    return 0

def _number_or_raise(value: CellValue) -> float:
    """Coerce a scalar argument to a number, raising on Excel coercion errors."""
    number = to_number(as_scalar(value))
    if isinstance(number, XlError):
        raise XlErrorException(number)
    return number

def _values_match(a: object, b: object) -> bool:
    a = _as_scalar(a)
    b = _as_scalar(b)
    if isinstance(a, str) and isinstance(b, str):
        return excel_casefold(a) == excel_casefold(b)
    an = to_number(a)
    bn = to_number(b)
    if not isinstance(an, XlError) and not isinstance(bn, XlError):
        return an == bn
    return a == b

def compare_scalars(op: str, left: FormulaValue, right: FormulaValue) -> bool | XlError:
    """Compare two scalar cell values using Excel coercion rules."""
    if isinstance(left, XlError):
        return left
    if isinstance(right, XlError):
        return right

    def _cmp_str(a: str, b: str) -> bool:
        if op == "=":
            return a == b
        if op == "<>":
            return a != b
        if op == "<":
            return a < b
        if op == ">":
            return a > b
        if op == "<=":
            return a <= b
        if op == ">=":
            return a >= b
        raise ValueError(f"Unknown comparison operator: {op}")

    def _cmp_float(a: float, b: float) -> bool:
        if op == "=":
            return a == b
        if op == "<>":
            return a != b
        if op == "<":
            return a < b
        if op == ">":
            return a > b
        if op == "<=":
            return a <= b
        if op == ">=":
            return a >= b
        raise ValueError(f"Unknown comparison operator: {op}")

    if isinstance(left, str) and isinstance(right, str):
        return _cmp_str(excel_casefold(left), excel_casefold(right))

    # Exact empty text compares as 0 (Excel); whitespace-only does not coerce.
    if isinstance(left, str) and left == "":
        left = 0.0
    if isinstance(right, str) and right == "":
        right = 0.0

    ln = to_number(left)
    rn = to_number(right)
    if isinstance(ln, XlError) or isinstance(rn, XlError):
        return _cmp_str(excel_casefold(to_string(left)), excel_casefold(to_string(right)))

    return _cmp_float(float(ln), float(rn))

def exp_number(*args: CellValue) -> float | XlError:
    """Return e raised to the power of a number (Excel ``EXP``)."""
    if len(args) != 1:
        return XlError.VALUE
    n = to_number(args[0])
    if isinstance(n, XlError):
        return n
    try:
        return float(math.exp(n))
    except OverflowError:
        return XlError.NUM

def index_excel_range(
    base: ExcelRangeGeometry,
    row_num: FormulaValue | None,
    col_num: FormulaValue | None,
) -> ExcelRange | XlError:
    """Map INDEX(row,col) over *base* to an absolute range (single cell or slice).

    Mirrors `excel_grapher.runtime.lookup.xl_index` geometry
    so OFFSET(INDEX(...), ...) receives a true cell reference.
    """
    nrows = base.end_row - base.start_row + 1
    ncols = base.end_col - base.start_col + 1
    row_omitted = row_num is None
    col_omitted = col_num is None

    def abs_cell(r0: int, c0: int) -> ExcelRange:
        r = base.start_row + r0
        c = base.start_col + c0
        return ExcelRange(base.sheet, r, c, r, c)

    if row_omitted and col_omitted:
        if nrows == 1 and ncols == 1:
            return abs_cell(0, 0)
        if nrows == 1:
            return abs_cell(0, ncols - 1)
        if ncols == 1:
            return abs_cell(nrows - 1, 0)
        return XlError.VALUE

    if row_omitted:
        cn = to_number(col_num)
        if isinstance(cn, XlError):
            return cn
        col = int(cn)
        if col < 1 or col > ncols:
            return XlError.REF
        if nrows == 1:
            return abs_cell(0, col - 1)
        c0 = base.start_col + col - 1
        return ExcelRange(base.sheet, base.start_row, c0, base.end_row, c0)

    rn = to_number(row_num)
    if isinstance(rn, XlError):
        return rn
    row = int(rn)

    if col_omitted:
        if nrows == 1:
            if row < 1 or row > ncols:
                return XlError.REF
            return abs_cell(0, row - 1)
        if ncols == 1:
            if row < 1 or row > nrows:
                return XlError.REF
            return abs_cell(row - 1, 0)
        if row < 1 or row > nrows:
            return XlError.REF
        r0 = base.start_row + row - 1
        return ExcelRange(base.sheet, r0, base.start_col, r0, base.end_col)

    cn = to_number(col_num)
    if isinstance(cn, XlError):
        return cn
    col = int(cn)
    if nrows == 1:
        if row < 1 or row > ncols:
            return XlError.REF
        return abs_cell(0, row - 1)
    if ncols == 1:
        if row < 1 or row > nrows:
            return XlError.REF
        return abs_cell(row - 1, 0)
    if row < 1 or row > nrows:
        return XlError.REF
    if col < 1 or col > ncols:
        return XlError.REF
    return abs_cell(row - 1, col - 1)

def match_cells(
    lookup_value: object,
    lookup_array: object,
    match_type: object = 1,
) -> int | XlError:
    """Excel MATCH over a lazy grid or nested-list array."""
    mt = to_number(cast(CellValue, match_type))
    if isinstance(mt, XlError):
        return mt
    match_type_int = int(mt)
    if isinstance(lookup_array, XlError):
        return lookup_array
    grid = Grid.wrap(lookup_array)
    if grid is None:
        grid_wrapped = Grid.wrap([[lookup_array]])
        assert grid_wrapped is not None
        grid = grid_wrapped
    if match_type_int == 0:
        for i in range(grid.size):
            if _values_match(lookup_value, grid.at_flat(i)):
                return i + 1
        return XlError.NA
    if match_type_int == 1:
        last_match = None
        for i in range(grid.size):
            if _compare_values(grid.at_flat(i), lookup_value) <= 0:
                last_match = i + 1
            else:
                break
        return XlError.NA if last_match is None else last_match
    if match_type_int == -1:
        last_match = None
        for i in range(grid.size):
            if _compare_values(grid.at_flat(i), lookup_value) >= 0:
                last_match = i + 1
            else:
                break
        return XlError.NA if last_match is None else last_match
    return XlError.VALUE

def warn_circular_reference(*, stacklevel: int = 2) -> None:
    """Emit the standard circular-reference warning."""
    warnings.warn(
        "Circular reference detected; returning 0 (iterative calculation is disabled).",
        CircularReferenceWarning,
        stacklevel=stacklevel,
    )

def xl_bool(value: CellValue) -> bool:
    """Coerce a scalar cell value to a boolean, raising on Excel errors."""
    scalar = as_scalar(value)
    if isinstance(scalar, XlError):
        raise _raise_error(scalar)
    boolean = to_bool(scalar)
    if isinstance(boolean, XlError):
        raise _raise_error(boolean)
    return boolean

def xl_circular_reference() -> CellValue:
    """Excel default behavior for circular references (non-iterative calculation)."""
    warn_circular_reference(stacklevel=2)
    return 0

def _evaluate_address(
    ctx: EvalContext,
    address: str,
    obtain_fn: Callable[[], Callable[[EvalContext], CellValue]],
    *,
    preserve_structural_blank: bool = False,
) -> CellValue:
    """Shared evaluation path for ``xl_cell`` and ``xl_eval``.

    Excel error values raise `XlErrorException`; the raising cell's error code
    is cached so re-reads raise without re-evaluating.
    """
    if ctx.stack:
        ctx._record_dependency(ctx.stack[-1], address)

    if address in ctx.cache:
        if address in ctx.circular_warning_roots:
            warn_circular_reference(stacklevel=3)
        return _raise_if_error_value(ctx.cache[address])

    if address in ctx.computing:
        if ctx.iterative_enabled:
            return ctx.iteration_values.get(address, 0)
        root = ctx.stack[0] if ctx.stack else address
        ctx.circular_warning_roots.add(root)
        return xl_circular_reference()

    if address in ctx.inputs:
        v = ctx.inputs[address]
        ctx.cache[address] = v
        return _raise_if_error_value(v)

    fn = obtain_fn()

    ctx.computing.add(address)
    ctx.stack.append(address)
    try:
        try:
            v = fn(ctx)
        except XlErrorException as exc:
            ctx.cache[address] = exc.code
            raise
        if v is None and not (
            preserve_structural_blank and getattr(fn, "__structural_blank__", False)
        ):
            v = 0
        ctx.cache[address] = v
        return _raise_if_error_value(v)
    finally:
        ctx.computing.discard(address)
        if ctx.stack and ctx.stack[-1] == address:
            ctx.stack.pop()

def xl_cell(ctx: EvalContext, address: str) -> CellValue:
    """Evaluate a single cell address under the given context.

    Resolution order:
    - cached value (per ctx)
    - user-provided inputs
    - exported formula implementation (via resolver)
    - missing cell raises KeyError
    """

    def obtain_fn() -> Callable[[EvalContext], CellValue]:
        fn = ctx.resolver(address)
        if fn is None:
            raise KeyError(f"Cell {address} not found in graph")
        return fn

    return _evaluate_address(ctx, address, obtain_fn, preserve_structural_blank=True)

def _ctx_range(ctx: EvalContext, sheet: str, r1: int, c1: int, r2: int, c2: int) -> Range:
    # Leave the resolver unannotated: embed strips `excel_grapher.core` imports, so
    # aliases like `CellValue as CoreCellValue` never appear in generated runtime.py.
    def resolve(address: str):
        return xl_cell(ctx, address)

    return Range(sheet, r1, c1, r2, c2, resolve)

def xl_compare(op: str, left: CellValue, right: CellValue) -> bool:
    """Compare two scalar operands with Excel ordering rules."""
    result = compare_scalars(op, as_scalar(left), as_scalar(right))
    if isinstance(result, XlError):
        raise _raise_error(result)
    return result

def xl_eval(
    ctx: EvalContext,
    address: str,
    fn: Callable[[EvalContext], CellValue],
) -> CellValue:
    """Evaluate a known formula implementation under the given context."""
    return _evaluate_address(ctx, address, lambda: fn, preserve_structural_blank=False)

def xl_exp(*args: CellValue) -> float:
    """Return e raised to a power, raising on Excel errors."""
    return raise_if_sentinel_float(exp_number(*args))

def xl_index_ref(
    ref: ExcelRange | OffsetRefInfo,
    row_num: CellValue | None,
    col_num: CellValue | None,
) -> OffsetRefInfo:
    """Return INDEX address metadata for OFFSET, not a cell value.

    Pass the result to `xl_offset` (or `xl_offset_ref`). Scalar INDEX reads are
    emitted as `xl_offset(ctx, xl_index_ref(...), 0, 0)`.

    Raises:
        XlErrorException: On Excel reference errors such as `#REF!`.
    """
    out = index_excel_range(
        _range_from_ref_info(ref),
        _as_addressing_scalar(row_num),
        _as_addressing_scalar(col_num),
    )
    if isinstance(out, XlError):
        raise XlErrorException(out)
    if out.start_row == out.end_row and out.start_col == out.end_col:
        return (out.sheet, out.start_row, out.start_col)
    return (out.sheet, out.start_row, out.start_col, out.end_row, out.end_col)

def xl_match(lookup_value: CellValue, lookup_array: CellValue, match_type: CellValue = 1) -> int:
    result = _raise_if_error(match_cells(lookup_value, lookup_array, match_type))
    return cast(int, result)

def xl_number(value: CellValue) -> float:
    """Coerce a scalar cell value to a number, raising on Excel errors."""
    scalar = as_scalar(value)
    if isinstance(scalar, XlError):
        raise _raise_error(scalar)
    number = to_number(scalar)
    if isinstance(number, XlError):
        raise _raise_error(number)
    return number

def xl_offset(
    ctx: EvalContext,
    ref_info: OffsetRefInfo,
    rows: CellValue,
    cols: CellValue,
    height: CellValue | None = None,
    width: CellValue | None = None,
) -> CellValue:
    """Evaluate OFFSET from `ref_info`, returning a cell value or range.

    `ref_info` is typically produced by `xl_index_ref`. For a scalar INDEX
    result use `rows=0`, `cols=0`.

    Raises:
        XlErrorException: On Excel reference or coercion errors.
    """
    rr = _number_or_raise(rows)
    cc = _number_or_raise(cols)

    match ref_info:
        case (sheet, base_row, base_col):
            base_end_row, base_end_col = base_row, base_col
        case (sheet, base_row, base_col, base_end_row, base_end_col):
            pass
        case _:
            raise XlErrorException(XlError.VALUE)

    base_h = int(base_end_row - base_row + 1)
    base_w = int(base_end_col - base_col + 1)

    h = base_h if height is None else int(_number_or_raise(height))
    w = base_w if width is None else int(_number_or_raise(width))

    target_row = int(base_row + int(rr))
    target_col = int(base_col + int(cc))

    if target_row < 1 or target_col < 1:
        raise XlErrorException(XlError.REF)
    if h <= 0 or w <= 0:
        raise XlErrorException(XlError.VALUE)

    if h == 1 and w == 1:
        addr = _format_address(sheet, target_row, target_col)
        # Scalar OFFSET results are CellValue; multi-cell returns a lazy Range.
        return cast("CellValue", xl_cell(ctx, addr))

    return _ctx_range(ctx, sheet, target_row, target_col, target_row + h - 1, target_col + w - 1)

def xl_pow_numbers(left: float, right: float) -> float:
    """Apply Excel exponentiation to coerced numbers."""
    try:
        value = left**right
    except (ValueError, OverflowError):
        raise _raise_error(XlError.NUM) from None
    if isinstance(value, complex):
        raise _raise_error(XlError.NUM)
    return value

def xl_raise(code: XlError) -> NoReturn:
    """Raise an Excel error code from an expression position."""
    raise XlErrorException(code)

def xl_range(ctx: EvalContext, address: str) -> CellValue:
    """Evaluate a sheet-qualified range address into a lazy `Range` value."""
    parsed = _parse_range_address(address)
    if isinstance(parsed, XlError):
        raise XlErrorException(parsed)
    sheet, start_cell, end_cell = parsed
    try:
        start_col, start_row = fastpyxl.utils.cell.coordinate_from_string(start_cell)
        end_col, end_row = fastpyxl.utils.cell.coordinate_from_string(end_cell)
        start_col_idx = fastpyxl.utils.cell.column_index_from_string(start_col)
        end_col_idx = fastpyxl.utils.cell.column_index_from_string(end_col)
    except ValueError:
        raise XlErrorException(XlError.VALUE) from None

    if start_row > end_row:
        start_row, end_row = end_row, start_row
    if start_col_idx > end_col_idx:
        start_col_idx, end_col_idx = end_col_idx, start_col_idx

    return _ctx_range(ctx, sheet, start_row, start_col_idx, end_row, end_col_idx)

def xl_range_rows(ctx: EvalContext, address: str) -> CellValue:
    """Evaluate a sheet-qualified range eagerly into nested row lists.

    Public boundary handler for range targets: results returned from
    `compute_all` are materialized values, not lazy range views.
    """
    rng = xl_range(ctx, address)
    if isinstance(rng, Range):
        return rng.rows_raw()
    return rng

# --- parameterized helper memoization (qcraft #86) ---

def _qcraft_freeze_helper_kwargs(kwargs):
    frozen = []
    for name in sorted(kwargs):
        value = kwargs[name]
        try:
            hash(value)
        except TypeError as error:
            raise TypeError(
                f"xl_helper kwargs must be hashable for memoization; "
                f"got {name}={value!r} of type {type(value).__name__}"
            ) from error
        frozen.append((name, value))
    return tuple(frozen)


_QCRAFT_SIDE_HELPER_CACHES = {}
_QCRAFT_SIDE_HELPER_COMPUTING = {}


def _qcraft_helper_maps(ctx):
    helper_cache = getattr(ctx, "helper_cache", None)
    helper_computing = getattr(ctx, "helper_computing", None)
    if isinstance(helper_cache, dict) and isinstance(helper_computing, set):
        return helper_cache, helper_computing
    ctx_id = id(ctx)
    return (
        _QCRAFT_SIDE_HELPER_CACHES.setdefault(ctx_id, {}),
        _QCRAFT_SIDE_HELPER_COMPUTING.setdefault(ctx_id, set()),
    )


def xl_helper(ctx, fn, /, **kwargs):
    """Evaluate a parameterized helper, memoized by ``(fn, kwargs)`` on ``ctx``."""
    key = (fn, _qcraft_freeze_helper_kwargs(kwargs))
    cache, computing = _qcraft_helper_maps(ctx)
    if key in cache:
        value = cache[key]
        if isinstance(value, XlError):
            raise XlErrorException(value)
        return value
    if key in computing:
        return xl_circular_reference()
    computing.add(key)
    try:
        try:
            value = fn(ctx, **kwargs)
        except XlErrorException as exc:
            cache[key] = exc.code
            raise
        cache[key] = value
        if isinstance(value, XlError):
            raise XlErrorException(value)
        return value
    finally:
        computing.discard(key)


def xl_memoize(fn):
    """Decorator routing a ``(ctx, **params)`` helper through :func:`xl_helper`."""
    import functools as _functools
    import inspect as _inspect

    @_functools.wraps(fn)
    def wrapper(ctx, /, *args, **kwargs):
        if args:
            bound = _inspect.signature(fn).bind(ctx, *args, **kwargs)
            bound.apply_defaults()
            param_kwargs = {
                name: value
                for name, value in bound.arguments.items()
                if name != "ctx"
            }
            return xl_helper(ctx, fn, **param_kwargs)
        return xl_helper(ctx, fn, **kwargs)

    wrapper.__wrapped__ = fn
    return wrapper


def _qcraft_patch_eval_context_invalidate():
    original = EvalContext.invalidate

    def invalidate(self, addresses):
        _QCRAFT_SIDE_HELPER_CACHES.pop(id(self), None)
        _QCRAFT_SIDE_HELPER_COMPUTING.pop(id(self), None)
        helper_cache = getattr(self, "helper_cache", None)
        helper_computing = getattr(self, "helper_computing", None)
        if isinstance(helper_cache, dict):
            helper_cache.clear()
        if isinstance(helper_computing, set):
            helper_computing.clear()
        return original(self, addresses)

    EvalContext.invalidate = invalidate


_qcraft_patch_eval_context_invalidate()
