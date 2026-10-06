/**
 * Interactive series dependency graph.
 * Loads series topology from GET /api/graph and recomputes via
 * POST /api/evaluate with backend=formula_evaluator (excel-grapher).
 * Fall back: ./bootstrap.json for static docs preview when the API is offline.
 */
(function () {
  "use strict";

  const BACKEND = "formula_evaluator";
  const DEFAULT_TITLE = "Dependency graph";
  const FORCE_GAP_X = 40;
  const FORCE_GAP_Y = 18;

  const PREVIEW =
    typeof document !== "undefined" &&
    (document.body.classList.contains("preview") ||
      new URLSearchParams(window.location.search).get("preview") === "1" ||
      new URLSearchParams(window.location.search).get("preview") === "true");

  /** @type {any[]} */
  let SERIES = [];
  /** @type {string[][]} */
  let SERIES_EDGES = [];
  /** @type {Record<string, any>} */
  let SERIES_BY_ID = {};
  /** @type {Record<string, any>} */
  let DEFAULTS = {};
  /** @type {Record<string, any>} */
  let inputs = {};
  /** @type {Record<string, any>} */
  let values = {};
  let selectedId = null;
  let cy = null;
  const positionUndo = [];
  let dragOrigin = null;
  let apiBase = "";
  /** Precomputed force layout from layout.json. */
  let STARTER_LAYOUT = null;
  const Panel = globalThis.SeriesGraphPanel;

  function trimSlash(url) {
    return String(url || "").replace(/\/+$/, "");
  }

  /**
   * Resolve remote FormulaEvaluator API base (e.g. Railway).
   * Order: ?api=… → meta[name=series-graph-api] → window.SERIES_GRAPH_API
   * → config.js SERIES_GRAPH_API. Same-origin /api is tried next by loadBootstrap.
   */
  function configuredApiBase() {
    const params = new URLSearchParams(window.location.search);
    const fromQuery = params.get("api");
    if (fromQuery) return trimSlash(fromQuery);
    const meta = document.querySelector('meta[name="series-graph-api"]');
    if (meta && meta.content) return trimSlash(meta.content);
    if (typeof window.SERIES_GRAPH_API === "string" && window.SERIES_GRAPH_API) {
      return trimSlash(window.SERIES_GRAPH_API);
    }
    return "";
  }

  function apiUrl(path) {
    const base = trimSlash(apiBase);
    const suffix = path.startsWith("/") ? path : `/${path}`;
    return base ? `${base}${suffix}` : suffix;
  }

  function cloneMap(value) {
    if (value && typeof value === "object" && !Array.isArray(value)) {
      return { ...value };
    }
    return value;
  }

  function cloneDefaults() {
    const next = {};
    for (const [key, value] of Object.entries(DEFAULTS)) {
      next[key] = cloneMap(value);
    }
    return next;
  }

  /** Coerce JSON string keys back to series key types (years are ints). */
  function normalizeSeriesValue(series, raw) {
    if (raw == null) return raw;
    if (!series || series.keys.length === 1 && series.keys[0] == null) {
      return raw;
    }
    const out = {};
    for (const key of series.keys) {
      if (Object.prototype.hasOwnProperty.call(raw, key)) {
        out[key] = raw[key];
      } else if (Object.prototype.hasOwnProperty.call(raw, String(key))) {
        out[key] = raw[String(key)];
      }
    }
    return out;
  }

  function normalizeValuesPayload(rawValues) {
    const out = {};
    for (const [id, raw] of Object.entries(rawValues || {})) {
      const series = SERIES_BY_ID[id];
      out[id] = normalizeSeriesValue(series, raw);
    }
    return out;
  }

  function normalizeInputsPayload(rawInputs) {
    const out = {};
    for (const [id, raw] of Object.entries(rawInputs || {})) {
      const series = SERIES_BY_ID[id];
      out[id] = normalizeSeriesValue(series, raw);
    }
    return out;
  }

  async function fetchJson(url, options) {
    const response = await fetch(url, options);
    let payload = null;
    try {
      payload = await response.json();
    } catch (_err) {
      payload = null;
    }
    if (!response.ok) {
      const message =
        (payload && (payload.error || payload.message)) ||
        `HTTP ${response.status}`;
      const err = new Error(message);
      err.status = response.status;
      err.payload = payload;
      throw err;
    }
    return payload;
  }

  async function loadBootstrap() {
    const configured = configuredApiBase();
    const candidates = [];
    if (configured) {
      candidates.push({
        href: `${configured}/api/graph?backend=${encodeURIComponent(BACKEND)}`,
        base: configured,
      });
    }
    candidates.push(
      {
        href: new URL(
          `/api/graph?backend=${encodeURIComponent(BACKEND)}`,
          window.location.origin
        ).href,
        base: window.location.origin,
      },
      {
        href: new URL(
          `./api/graph?backend=${encodeURIComponent(BACKEND)}`,
          window.location.href
        ).href,
        base: null,
      },
      { href: new URL("./bootstrap.json", window.location.href).href, base: "" }
    );
    let lastError = null;
    for (const candidate of candidates) {
      try {
        const data = await fetchJson(candidate.href);
        if (candidate.base === null) {
          const absolute = new URL(candidate.href);
          apiBase = trimSlash(absolute.href.replace(/\/api\/graph\?.*$/, ""));
        } else {
          apiBase = candidate.base;
        }
        return data;
      } catch (err) {
        lastError = err;
      }
    }
    throw lastError || new Error("Could not load graph bootstrap");
  }

  /** A missing or stale layout.json is a pipeline bug, shown in the graph pane. */
  function layoutError(message) {
    const err = new Error(
      `${message} Re-run the export stage so it rewrites assets/graph/layout.json from graph_schema.py.`
    );
    err.layout = true;
    return err;
  }

  /** layout.json is written by the export pipeline whenever graph_schema.py has series. */
  async function loadStarterLayout() {
    let data;
    try {
      data = await fetchJson(new URL("./layout.json", window.location.href).href);
    } catch (err) {
      throw layoutError(`Could not load layout.json (${err.message}).`);
    }
    if (!data || !data.positions) throw layoutError("layout.json has no positions.");
    return data;
  }

  async function evaluateRemote(nextInputs) {
    if (!apiBase && !window.location.pathname.includes("api")) {
      // Static bootstrap-only mode (docs preview): no live recompute.
      throw new Error(
        "Live recompute needs the FormulaEvaluator API. Run: uv run python scripts/serve_graph_api.py"
      );
    }
    const url = apiUrl(`/api/evaluate`);
    const payload = await fetchJson(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ backend: BACKEND, inputs: nextInputs }),
    });
    return normalizeValuesPayload(payload.values);
  }

  function applyBootstrap(data) {
    SERIES = data.nodes || [];
    SERIES_EDGES = data.edges || [];
    SERIES_BY_ID = Object.fromEntries(SERIES.map((s) => [s.id, s]));
    DEFAULTS = normalizeInputsPayload(data.defaults || {});
    inputs = cloneDefaults();
    values = normalizeValuesPayload(data.values || {});
  }

  function formatValue(value) {
    if (typeof value === "string") return value;
    if (typeof value === "number" && Number.isFinite(value)) {
      if (Number.isInteger(value)) return String(value);
      return value.toFixed(2);
    }
    return String(value);
  }

  function valuesText(series, allValues) {
    const raw = normalizeSeriesValue(series, allValues[series.id]);
    if (series.keys.length === 1 && series.keys[0] == null) {
      return formatValue(raw);
    }
    return Panel.summarize(
      series.keys.map((key) => formatValue(raw[key])),
      "values"
    );
  }

  function addressText(series) {
    if (series.address) return series.address;
    if (series.addresses) {
      const addresses = series.addresses;
      return Panel.summarize(
        series.keys.map((key) => addresses[key] ?? addresses[String(key)]),
        "cells"
      );
    }
    return "";
  }

  function nodeSize(valuesStr) {
    const width = Math.min(360, Math.max(168, 28 + valuesStr.length * 8.2));
    return { width, height: 64 };
  }

  function buildElements(allValues) {
    const elements = [];
    for (const series of SERIES) {
      const vals = valuesText(series, allValues);
      const size = nodeSize(vals);
      elements.push({
        data: {
          id: series.id,
          name: series.label,
          valuesText: vals,
          label: `${vals}\n${series.label}`,
          role: series.role,
          sheet: series.sheet,
          kind: series.kind,
          address: addressText(series),
          editable: series.role === "input",
          width: size.width,
          height: size.height,
        },
        classes: `series ${series.role}${series.role === "input" ? " editable" : ""}`,
      });
    }
    for (const [source, target] of SERIES_EDGES) {
      elements.push({
        data: { id: `${source}->${target}`, source, target },
        classes: "dep",
      });
    }
    return elements;
  }

  function applyLayout(cyInstance) {
    const sizes = {};
    cyInstance.nodes("node.series").forEach((node) => {
      sizes[node.id()] = { width: node.data("width"), height: node.data("height") };
    });
    const placed = globalThis.SeriesGraphForceLayout.placeNodes({
      positions: STARTER_LAYOUT.positions,
      sizes,
      linkDistance: STARTER_LAYOUT.link_distance,
      gapX: FORCE_GAP_X,
      gapY: FORCE_GAP_Y,
    });
    if (!placed) throw layoutError("layout.json does not cover every series.");
    for (const [id, pos] of Object.entries(placed)) {
      cyInstance.$id(id).position(pos);
    }
  }

  function patchValues(cyInstance, allValues, changedIds) {
    for (const series of SERIES) {
      const node = cyInstance.$id(series.id);
      if (node.empty()) continue;
      const vals = valuesText(series, allValues);
      const prev = node.data("valuesText");
      const size = nodeSize(vals);
      node.data("valuesText", vals);
      node.data("label", `${vals}\n${series.label}`);
      node.data("width", size.width);
      node.data("height", size.height);
      if (changedIds && changedIds.has(series.id) && prev !== vals) {
        node.addClass("changed");
        setTimeout(() => node.removeClass("changed"), 700);
      }
    }
    cyInstance.nodes().forEach((node) => node.trigger("position"));
  }

  function toast(message) {
    const el = document.getElementById("toast");
    el.textContent = message;
    el.classList.add("show");
    clearTimeout(toast._t);
    toast._t = setTimeout(() => el.classList.remove("show"), 2200);
  }

  function downstreamOf(seriesId) {
    const out = new Set([seriesId]);
    let grew = true;
    while (grew) {
      grew = false;
      for (const [s, t] of SERIES_EDGES) {
        if (out.has(s) && !out.has(t)) {
          out.add(t);
          grew = true;
        }
      }
    }
    return out;
  }

  async function recompute(changedSeriesId) {
    try {
      values = await evaluateRemote(inputs);
      patchValues(cy, values, changedSeriesId ? downstreamOf(changedSeriesId) : null);
      if (selectedId) renderSide(selectedId);
    } catch (err) {
      console.error(err);
      toast(err.message || "Evaluate failed");
    }
  }

  function renderSide(nodeId) {
    const panel = document.getElementById("side");
    if (!nodeId) {
      panel.innerHTML =
        '<p class="empty">Select a series node. Amber inputs are editable. Drag nodes to rearrange; Ctrl+Z undoes a move. Values come from excel-grapher FormulaEvaluator.</p>';
      selectedId = null;
      return;
    }
    const node = cy.$id(nodeId);
    if (node.empty()) {
      renderSide(null);
      return;
    }
    selectedId = nodeId;
    const series = SERIES_BY_ID[nodeId];
    const editable = series.role === "input";
    const vals = valuesText(series, values);
    const keysHint =
      series.keys[0] == null ? "scalar" : Panel.summarize(series.keys, "keys");

    let editor = "";
    if (editable) {
      editor = Panel.editorHtml(series, inputs[series.id]);
      editor += `<button class="primary" type="button" id="apply-edit">Apply</button>`;
    } else {
      editor = `<p class="hint">Read-only ${series.role} series. Edit an amber input upstream to change these values.</p>`;
    }

    panel.innerHTML = `
      <h2>${Panel.escapeHtml(series.label)}</h2>
      <div class="meta">${addressText(series) || "—"} · ${series.role} · ${series.sheet}</div>
      ${Panel.hintHtml(series)}
      <div class="values-display">${vals}</div>
      <div style="margin-top:0.75rem">${editor}</div>
      <p class="hint" style="margin-top:0.85rem">Keys: ${keysHint}. Double-click an input node to focus the editor. Ctrl+Z undoes node moves.</p>
    `;

    const apply = document.getElementById("apply-edit");
    if (apply) {
      apply.addEventListener("click", async () => {
        const raw = document.getElementById("edit-value").value;
        if (!commitEdit(series, raw)) return;
        apply.disabled = true;
        await recompute(series.id);
        apply.disabled = false;
        toast(`Updated ${series.label}`);
      });
    }
  }

  function commitEdit(series, raw) {
    try {
      inputs[series.id] = Panel.parseEdit(series, raw);
      return true;
    } catch (err) {
      toast(err.message || "Invalid value");
      return false;
    }
  }

  function undoMove() {
    const last = positionUndo.pop();
    if (!last) {
      toast("Nothing to undo");
      return;
    }
    const node = cy.$id(last.id);
    if (!node.empty()) {
      node.position({ x: last.x, y: last.y });
      toast("Undo move");
    }
  }

  function attachHtmlLabels(cyInstance) {
    if (typeof cyInstance.nodeHtmlLabel !== "function") return;
    cyInstance.nodeHtmlLabel([
      {
        query: "node.series",
        halign: "center",
        valign: "center",
        halignBox: "center",
        valignBox: "center",
        tpl(data) {
          return (
            `<div class="cy-html-node">` +
            `<div class="cy-html-values">${data.valuesText}</div>` +
            `<div class="cy-html-name">${data.name}</div>` +
            `</div>`
          );
        },
      },
    ]);
    cyInstance
      .style()
      .selector("node.series")
      .style({
        label: "",
        "text-opacity": 0,
      })
      .update();
  }

  function initCy() {
    cy = cytoscape({
      container: document.getElementById("cy"),
      elements: buildElements(values),
      autoungrabify: PREVIEW,
      userPanningEnabled: !PREVIEW,
      userZoomingEnabled: !PREVIEW,
      boxSelectionEnabled: false,
      style: [
        {
          selector: "node.series",
          style: {
            shape: "round-rectangle",
            width: "data(width)",
            height: "data(height)",
            label: "data(label)",
            "text-wrap": "wrap",
            "text-max-width": 340,
            "text-valign": "center",
            "text-halign": "center",
            "font-size": 15,
            "font-weight": "bold",
            "border-width": 2,
            color: "#1c1917",
            "background-opacity": 1,
            "z-index": 10,
          },
        },
        {
          selector: "node.series.input",
          style: {
            "background-color": "#fef3c7",
            "border-color": "#d97706",
          },
        },
        {
          selector: "node.series.internal",
          style: {
            "background-color": "#e0e7ff",
            "border-color": "#6366f1",
          },
        },
        {
          selector: "node.series.output",
          style: {
            "background-color": "#d1fae5",
            "border-color": "#059669",
          },
        },
        {
          selector: "node.series.changed",
          style: {
            "border-color": "#f43f5e",
            "border-width": 3,
          },
        },
        {
          selector: "node.series:selected",
          style: {
            "border-width": 3,
            "border-color": "#0f766e",
          },
        },
        {
          selector: "edge.dep",
          style: {
            width: 2,
            "curve-style": "bezier",
            "source-endpoint": "outside-to-node",
            "target-endpoint": "outside-to-node",
            "target-arrow-shape": "triangle",
            "target-arrow-color": "#a8a29e",
            "line-color": "#a8a29e",
            "arrow-scale": 1,
            opacity: 0.85,
            "z-index": 1,
          },
        },
      ],
      layout: { name: "preset" },
      wheelSensitivity: 0.25,
      // cy.fit() will not zoom out past minZoom. A large graph needs far below 1.
      minZoom: 0.001,
      maxZoom: 2.5,
    });

    applyLayout(cy);
    try {
      attachHtmlLabels(cy);
    } catch (err) {
      console.warn("HTML labels unavailable; using native labels", err);
    }
    const initialPadding = PREVIEW ? 28 : 48;
    fitGraph(initialPadding);
    // The container can still be 0×0 on the first paint (iframe, hidden tab).
    requestAnimationFrame(() => fitGraph(initialPadding));
    window.addEventListener("resize", () => fitGraph(initialPadding));

    if (PREVIEW) return;

    cy.on("tap", "node.series", (evt) => {
      renderSide(evt.target.id());
    });
    cy.on("tap", (evt) => {
      if (evt.target === cy) renderSide(null);
    });
    cy.on("dbltap", "node.series.editable", (evt) => {
      renderSide(evt.target.id());
      const input = document.getElementById("edit-value");
      if (input) input.focus();
    });

    cy.on("grab", "node.series", (evt) => {
      const node = evt.target;
      dragOrigin = {
        id: node.id(),
        x: node.position("x"),
        y: node.position("y"),
      };
    });
    cy.on("dragfree", "node.series", (evt) => {
      if (!dragOrigin || dragOrigin.id !== evt.target.id()) return;
      const pos = evt.target.position();
      if (pos.x !== dragOrigin.x || pos.y !== dragOrigin.y) {
        positionUndo.push({ ...dragOrigin });
      }
      dragOrigin = null;
    });
  }

  async function resetAll() {
    inputs = cloneDefaults();
    positionUndo.length = 0;
    try {
      values = await evaluateRemote(inputs);
    } catch (err) {
      console.error(err);
      toast(err.message || "Reset evaluate failed");
      return;
    }
    cy.elements().remove();
    cy.add(buildElements(values));
    applyLayout(cy);
    try {
      attachHtmlLabels(cy);
    } catch (err) {
      console.warn("HTML labels unavailable; using native labels", err);
    }
    fitGraph(48);
    renderSide(null);
    toast("Reset to workbook defaults");
  }

  function fitPadding(padding) {
    if (typeof padding === "number") return padding;
    return PREVIEW ? 28 : 48;
  }

  /** Fit uses the container's current size, which is 0 until layout. */
  function fitGraph(padding) {
    if (!cy) return;
    cy.resize();
    cy.fit(undefined, fitPadding(padding));
  }

  const root = typeof globalThis !== "undefined" ? globalThis : window;
  root.SeriesGraph = {
    backend: BACKEND,
    get SERIES() {
      return SERIES;
    },
    get DEFAULTS() {
      return DEFAULTS;
    },
    cloneDefaults,
    evaluateRemote,
  };

  /** config.js may set window.SERIES_GRAPH_TITLE for this workbook. */
  function applyTitle() {
    const title =
      typeof window.SERIES_GRAPH_TITLE === "string" && window.SERIES_GRAPH_TITLE
        ? window.SERIES_GRAPH_TITLE
        : DEFAULT_TITLE;
    document.title = title;
    const heading = document.querySelector(".toolbar h1");
    if (heading) heading.textContent = title;
  }

  async function main() {
    const cyEl = typeof document !== "undefined" ? document.getElementById("cy") : null;
    if (!cyEl || typeof cytoscape !== "function") return;

    applyTitle();
    cyEl.innerHTML =
      '<p style="padding:1rem;font:14px system-ui;color:#57534e;">Loading the dependency graph… This graph is large and can take up to a minute to draw.</p>';

    try {
      const [data, starterLayout] = await Promise.all([loadBootstrap(), loadStarterLayout()]);
      applyBootstrap(data);
      STARTER_LAYOUT = starterLayout;
      cyEl.innerHTML = "";
      if (!PREVIEW) {
        document.getElementById("btn-reset").addEventListener("click", () => {
          resetAll();
        });
        document.getElementById("btn-fit").addEventListener("click", () => fitGraph(40));
        document.addEventListener("keydown", (event) => {
          const key = event.key.toLowerCase();
          if (!(event.ctrlKey || event.metaKey) || key !== "z" || event.shiftKey) return;
          const tag = (event.target && event.target.tagName) || "";
          if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
          event.preventDefault();
          undoMove();
        });
      }
      initCy();
      if (!PREVIEW) renderSide(null);
      if (!apiBase && !PREVIEW) {
        toast("API offline — edits need serve_graph_api.py");
      }
    } catch (err) {
      console.error("Series graph failed to initialize", err);
      if (cy) {
        cy.destroy();
        cy = null;
      }
      cyEl.innerHTML = err.layout
        ? `<p style="padding:1rem;font:14px system-ui;color:#b91c1c;">Graph layout error: ${Panel.escapeHtml(err.message)}</p>`
        : '<p style="padding:1rem;font:14px system-ui;color:#b91c1c;">Graph failed to load. Serve with <code>uv run python scripts/serve_graph_api.py</code> (FormulaEvaluator) or provide <code>bootstrap.json</code>.</p>';
    }
  }

  main();
})();
