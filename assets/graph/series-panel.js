/**
 * Side-panel helpers for the series graph: input editors keyed on series.id,
 * per-node hints, and compact list summaries.
 *
 * Editors pick their control from the series kind: `enum` / `enum_int` get a
 * select over `options`, `int` and scalar numeric inputs get a number input,
 * and keyed series get comma-separated text (one value per key). `domain` is
 * optional; when present, parseEdit enforces it.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.SeriesGraphPanel = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  /** Lists longer than this show only their first and last items. */
  const SUMMARY_LIMIT = 5;

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function isScalar(series) {
    return series.keys.length === 1 && series.keys[0] == null;
  }

  function optionLabel(series, option) {
    const labels = series.optionLabels || {};
    return labels[option] ?? labels[String(option)] ?? String(option);
  }

  function keyValue(current, key) {
    return current[key] ?? current[String(key)];
  }

  /** `first … last (N noun)` for long lists, else the items joined by commas. */
  function summarize(items, noun) {
    if (items.length <= SUMMARY_LIMIT) return items.join(", ");
    return `${items[0]} … ${items[items.length - 1]} (${items.length} ${noun})`;
  }

  function domainText(series) {
    return series.domain ? ` ${series.domain.min}–${series.domain.max}` : "";
  }

  function domainAttrs(series) {
    return series.domain
      ? ` min="${series.domain.min}" max="${series.domain.max}"`
      : "";
  }

  function selectHtml(series, isCurrent) {
    const options = series.options
      .map(
        (o) =>
          `<option value="${escapeHtml(o)}"${isCurrent(o) ? " selected" : ""}>${escapeHtml(
            optionLabel(series, o)
          )}</option>`
      )
      .join("");
    return `<label for="edit-value">Value</label><select id="edit-value">${options}</select>`;
  }

  /**
   * @param {any} series node object from GET /api/graph
   * @param {any} current the series' current input value (inputs[series.id])
   * @returns {string} label + control with id `edit-value`
   */
  function editorHtml(series, current) {
    if (series.kind === "enum") {
      return selectHtml(series, (o) => o === current);
    }
    if (series.kind === "enum_int") {
      return selectHtml(series, (o) => Number(o) === Number(current));
    }
    if (series.kind === "int") {
      return (
        `<label for="edit-value">Value (integer${domainText(series)})</label>` +
        `<input id="edit-value" type="number" step="1"${domainAttrs(series)} value="${escapeHtml(current)}" />`
      );
    }
    if (isScalar(series)) {
      return (
        `<label for="edit-value">Value${domainText(series)}</label>` +
        `<input id="edit-value" type="number" step="any"${domainAttrs(series)} value="${escapeHtml(current)}" />`
      );
    }
    const text = series.keys.map((key) => keyValue(current, key)).join(", ");
    return (
      `<label for="edit-value">Values (comma-separated · ${escapeHtml(
        summarize(series.keys, "keys")
      )})</label>` + `<input id="edit-value" type="text" value="${escapeHtml(text)}" />`
    );
  }

  function inDomain(series, n) {
    return !series.domain || (n >= series.domain.min && n <= series.domain.max);
  }

  /**
   * Parse the editor's raw value into the series' input value.
   * @throws {Error} with a user-facing message when the value is invalid.
   */
  function parseEdit(series, raw) {
    if (series.kind === "enum") {
      if (!series.options.includes(raw)) throw new Error("Invalid option");
      return raw;
    }
    if (series.kind === "enum_int") {
      const n = Number(raw);
      if (!series.options.map(Number).includes(n)) throw new Error("Invalid option");
      return n;
    }
    if (series.kind === "int") {
      const n = Number(raw);
      if (String(raw).trim() === "" || !Number.isInteger(n) || !inDomain(series, n)) {
        throw new Error("Out of range");
      }
      return n;
    }
    if (isScalar(series)) {
      const n = Number(raw);
      if (String(raw).trim() === "" || !Number.isFinite(n)) {
        throw new Error("Invalid number");
      }
      if (!inDomain(series, n)) throw new Error("Out of range");
      return n;
    }
    const parts = String(raw)
      .split(",")
      .map((part) => part.trim())
      .filter((part) => part.length > 0);
    if (parts.length !== series.keys.length) {
      throw new Error(`Expected ${series.keys.length} values`);
    }
    const next = {};
    series.keys.forEach((key, index) => {
      const n = Number(parts[index]);
      if (!Number.isFinite(n) || !inDomain(series, n)) {
        throw new Error(`Out of range at ${key}`);
      }
      next[key] = n;
    });
    return next;
  }

  /** Optional per-node `hint` from graph_schema.NODES, as a side-panel paragraph. */
  function hintHtml(series) {
    return series.hint ? `<p class="series-hint">${escapeHtml(series.hint)}</p>` : "";
  }

  return { editorHtml, escapeHtml, hintHtml, parseEdit, summarize };
});
