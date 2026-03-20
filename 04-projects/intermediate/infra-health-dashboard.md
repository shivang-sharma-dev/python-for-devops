# Project: Infrastructure Health Dashboard

**Level:** Intermediate
**Time:** 4–5 hours
**Covers:** Notes 08–14 (all DevOps topics)

---

## What You're Building

A terminal dashboard that shows live health status of your
infrastructure — servers, services, disk usage, and API endpoints —
refreshing every 30 seconds.

---

## Final Result

```
╔══════════════════════════════════════════════════════════╗
║  Infrastructure Health Dashboard  │  Last updated: 14:32 ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  SERVERS                                                 ║
║  web-01   10.0.1.1   ● Running   CPU: 45%   Disk: 62%   ║
║  web-02   10.0.1.2   ● Running   CPU: 87%   Disk: 71%   ║
║  db-01    10.0.1.5   ● Running   CPU: 12%   Disk: 88% ⚠ ║
║                                                          ║
║  SERVICES (this machine)                                 ║
║  nginx        ● active                                   ║
║  postgresql   ● active                                   ║
║  redis        ✗ inactive  ← restarted 2 minutes ago     ║
║                                                          ║
║  API ENDPOINTS                                           ║
║  /health      200   45ms  ▁▂▁▃▂▁▁▂ (last 8 checks)     ║
║  /api/users   200   120ms ▂▃▄▅▃▂▄▃                      ║
║  /api/orders  503   —     ▁▁▁▁▁▁▁█ ← degraded           ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

---

## Requirements

**Step 1 — Data collection**
Write separate functions for each data source:
- `get_server_stats(ip)` — SSH to each server, run `top` and `df`
- `get_local_services()` — use `subprocess` to run `systemctl`
- `check_endpoints(urls)` — use `requests` to check each API

**Step 2 — Dashboard rendering**
- Use the `rich` library for the terminal UI
- Use `rich.table.Table` for the structured data
- Use `rich.live.Live` to refresh in place without flickering

**Step 3 — Historical sparklines**
- Keep the last 8 latency readings per endpoint
- Render them as ASCII sparklines: `▁▂▃▄▅▆▇█`

**Step 4 — Alerting**
- Highlight rows in red when values exceed thresholds
- Send a Slack alert if any service goes down (only once, not every refresh)
- Track "first seen down" time to include in alerts

**Step 5 — Config**
- Read all server IPs, service names, and endpoint URLs from a YAML file
- Support `--config` flag to specify config file path

---

## Key Libraries

```bash
pip install rich paramiko requests pyyaml
```

```python
# Live dashboard with rich
from rich.live import Live
from rich.table import Table
import time

def make_table(data):
    table = Table(title="Infrastructure Health")
    table.add_column("Server")
    table.add_column("CPU")
    table.add_column("Status")
    for row in data:
        table.add_row(row["name"], f"{row['cpu']}%", row["status"])
    return table

with Live(make_table([]), refresh_per_second=1) as live:
    while True:
        data = collect_all_data()
        live.update(make_table(data))
        time.sleep(30)

# Sparkline from list of values
def sparkline(values):
    bars = "▁▂▃▄▅▆▇█"
    if not values: return ""
    min_v, max_v = min(values), max(values)
    if min_v == max_v: return bars[0] * len(values)
    return "".join(bars[int((v - min_v) / (max_v - min_v) * 7)] for v in values)
```
