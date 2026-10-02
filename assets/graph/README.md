# Series dependency graph (docs + Model API)

Cytoscape explorer for Q-CRAFT. The page asks for ``backend=formula_evaluator``.
The server builds one workbook graph from the output bindings, caches it under
``.cache/dependency-graph``, and reloads that cache on startup. The exported
``Model`` remains available as ``backend=export``.

The viewer itself (`app.js`, `index.html`, `series-panel.js`, `style.css`,
`force-layout.js`) comes unforked from the template. This overlay supplies only
`config.js` (Railway API base and page title), `bootstrap.json`, and
`qcraft/graph_schema.py` (nodes may carry a side-panel `hint`).

## Run locally

```bash
uv sync --group graph
uv run python scripts/write_graph_bootstrap.py   # static docs snapshot
uv run python scripts/check_graph_eval.py
uv run python scripts/serve_graph_api.py
# open http://127.0.0.1:8765/
```

Docs homepage embeds
``https://teal-insights.github.io/qcraft-2024-11-15/assets/graph/index.html?preview=1``
(read-only); click through to the fullscreen page at
``https://teal-insights.github.io/qcraft-2024-11-15/assets/graph/index.html``.
