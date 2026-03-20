# Project: Server Inventory Tool

**Level:** Beginner
**Time:** 2–3 hours
**Covers:** Notes 02–07 (variables, control flow, functions, data structures, file operations)

---

## What You're Building

A command-line tool that reads a list of servers from a CSV file,
pings each one to check if it's reachable, and writes a status
report to a new CSV file.

This is genuinely useful. Most teams maintain a server inventory
somewhere. Yours will actually tell you which ones are alive.

---

## Final Result

```
$ python3 inventory.py servers.csv --output report.csv
Loading servers from servers.csv...
Found 5 servers

Checking connectivity:
  web-01  (10.0.1.1)  ... reachable   (12ms)
  web-02  (10.0.1.2)  ... reachable   (15ms)
  db-01   (10.0.1.5)  ... UNREACHABLE
  cache   (10.0.1.8)  ... reachable   (8ms)
  lb-01   (10.0.1.10) ... reachable   (11ms)

Summary: 4/5 reachable
Report saved to report.csv
```

---

## Input File (servers.csv)

Create this file to test with:

```
name,ip,role,owner
web-01,10.0.1.1,web,platform
web-02,10.0.1.2,web,platform
db-01,10.0.1.5,database,dba-team
cache,10.0.1.8,cache,platform
lb-01,10.0.1.10,loadbalancer,platform
```

---

## Requirements

Build it step by step:

**Step 1 — Read the CSV**
- Read `servers.csv` using the `csv` module
- Store each row as a dict in a list
- Print how many servers were loaded

**Step 2 — Ping each server**
- Use `subprocess` to run `ping -c 1 -W 1 IP_ADDRESS`
- If `returncode == 0` → reachable
- Capture the round-trip time from the ping output using regex or string parsing

**Step 3 — Build the report**
- Add `status` ("reachable" or "unreachable") and `latency_ms` to each server dict
- Write the updated data to `report.csv`

**Step 4 — Add CLI arguments**
- Use `argparse` to accept the input file and `--output` flag
- Add `--timeout` flag to control ping timeout
- Add `--parallel` flag to ping all servers simultaneously (use `concurrent.futures.ThreadPoolExecutor`)

**Step 5 — Make it production-ready**
- Add proper error handling for missing files, bad IPs
- Add logging instead of print statements
- Add a `--dry-run` flag that reads the CSV but doesn't ping

---

## Stretch Goals

- Output as JSON (`--format json`)
- Send a Slack alert if any servers are unreachable
- Add SSH connectivity check (port 22 open?) instead of just ping
- Store results in SQLite for trend tracking over time

---

## Hints

```python
# Ping a host and get latency
import subprocess, re

def ping(ip, timeout=1):
    result = subprocess.run(
        ["ping", "-c", "1", "-W", str(timeout), ip],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return False, None
    # Extract time from: "round-trip min/avg/max = 1.2/1.2/1.2 ms"
    match = re.search(r"time=(\d+\.?\d*)", result.stdout)
    latency = float(match.group(1)) if match else None
    return True, latency

# Parallel execution
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(check_server, servers))
```
