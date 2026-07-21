# Data Visualization Automation

**Skill Name:** data-visualization-automation  
**Author:** 灵犀 AI (nima54851)  
**Compatible:** OpenClaw + n8n  
**Tags:** data, charts, visualization, analytics, plotly, d3, charts

---

## What This Skill Does

Automate the generation of charts, dashboards, and data visualizations from raw data (CSV, JSON, API). Uses Python (Plotly, Matplotlib, D3.js) to generate interactive and static visualizations, then auto-embeds them into reports, dashboards, or n8n workflows.

## Use Cases

- Auto-generate weekly analytics charts for GitHub/Python/AI project metrics
- Build live dashboards from n8n workflow data outputs
- Turn JSON API responses into visual charts automatically
- Create SVG/PNG charts for reports and READMEs

## Core Scripts

### `chart_generator.py`

```python
#!/usr/bin/env python3
"""AI-powered chart generator from CSV/JSON data."""
import json, sys, argparse, base64
import pandas as pd
import plotly.express as px
import plotly.io as pio

TYPES = {
    "bar": px.bar,
    "line": px.line,
    "scatter": px.scatter,
    "pie": px.pie,
    "area": px.area,
    "histogram": px.histogram,
}

def generate_chart(data_file, chart_type="bar", title="Chart", output="chart.html"):
    df = pd.read_csv(data_file) if data_file.endswith(".csv") else pd.read_json(data_file)
    
    func = TYPES.get(chart_type, px.bar)
    fig = func(df, title=title)
    fig.update_layout(template="plotly_dark")
    fig.write_html(output)
    print(f"✅ Chart saved: {output}")
    return output

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    p.add_argument("--type", default="bar", choices=list(TYPES.keys()))
    p.add_argument("--title", default="Data Visualization")
    p.add_argument("--output", default="chart.html")
    args = p.parse_args()
    generate_chart(args.file, args.type, args.title, args.output)
```

### `dashboard_builder.py`

```python
#!/usr/bin/env python3
"""Build multi-panel HTML dashboard from data sources."""
import json, sys, plotly.graph_objects as go
from plotly.subplots import make_subplots

def build_dashboard(panels: list[dict]) -> str:
    """panels: [{title, data_file, chart_type}, ...]"""
    rows, cols = len(panels), 1
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=[p["title"] for p in panels])

    for i, panel in enumerate(panels, 1):
        import pandas as pd
        df = pd.read_csv(panel["data_file"]) if "," in panel["data_file"] or ".csv" in panel["data_file"] else pd.read_json(panel["data_file"])
        trace = get_trace(df, panel["chart_type"], i)
        fig.add_trace(trace, row=i, col=1)

    fig.update_layout(height=300 * rows, template="plotly_dark", showlegend=False)
    return fig.to_html(full_html=True)

def get_trace(df, chart_type, i):
    import plotly.express as px
    cols = list(df.columns)
    x, y = cols[0], cols[1] if len(cols) > 1 else cols[0]
    if chart_type == "bar": return px.bar(df, x=x, y=y).data[0]
    if chart_type == "line": return px.line(df, x=x, y=y).data[0]
    return px.scatter(df, x=x, y=y).data[0]

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        panels = json.load(f)
    html = build_dashboard(panels)
    with open("dashboard.html", "w") as f:
        f.write(html)
    print("✅ Dashboard: dashboard.html")
```

## n8n Workflow: AI Chart Generator

Trigger: Webhook → Python Script (chart_generator.py) → File Node → HTTP Request (GitHub Pages upload)

## n8n Workflow JSON

```json
{
  "name": "AI Data Visualization Pipeline",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": { "path": "visualize" }
    },
    {
      "name": "HTTP Request (Fetch Data)",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": { "url": "={{$json.dataUrl}}", "response": { "response": { "responseFormat": "json" } } }
    },
    {
      "name": "Generate Chart (Python)",
      "type": "n8n-nodes-base.python",
      "parameters": {
        "pythonCode": "import pandas as pd; import plotly.express as px\ndf = pd.DataFrame($json.data); fig = px.bar(df, x='date', y='value', title='Daily Metrics'); $json.chart_html = fig.to_html()"
      }
    },
    {
      "name": "Return Chart",
      "type": "n8n-nodes-base.respondToWebhook",
      "parameters": { "respondWith": "json", "responseBody": "={{ $json.chart_html }}" }
    }
  ],
  "connections": {
    "Webhook": { "main": [[{ "node": "HTTP Request (Fetch Data)", "type": "main", "index": 0 }]] },
    "HTTP Request (Fetch Data)": { "main": [[{ "node": "Generate Chart (Python)", "type": "main", "index": 0 }]] },
    "Generate Chart (Python)": { "main": [[{ "node": "Return Chart", "type": "main", "index": 0 }]] }
  }
}
```

## Quick Start

```bash
# Install dependencies
pip install pandas plotly

# Generate a bar chart from CSV
python3 chart_generator.py --file data.csv --type bar --title "Weekly Stars" --output stars.html

# Build multi-panel dashboard
python3 dashboard_builder.py panels.json
```

## Dependencies

- `pandas` — data manipulation
- `plotly` — interactive charts
- `kaleido` — export to PNG/SVG (`pip install kaleido`)
