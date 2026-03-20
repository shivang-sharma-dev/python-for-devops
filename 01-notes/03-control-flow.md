# 03 — Control Flow

---

## if / elif / else

```python
cpu = 87

if cpu > 95:
    print("CRITICAL")
elif cpu > 80:
    print("WARNING")
elif cpu > 60:
    print("ELEVATED")
else:
    print("OK")
```

Python uses indentation (4 spaces) to define blocks.
No curly braces. The colon at the end of `if` is required.

```python
# One-liner (ternary) — for simple cases only
status = "HIGH" if cpu > 80 else "OK"
print(f"CPU: {cpu}% — {status}")
```

### Checking multiple conditions

```python
cpu    = 87
memory = 91
disk   = 45

# AND — all conditions must be true
if cpu > 80 and memory > 80:
    print("Both CPU and memory are high")

# OR — at least one must be true
if cpu > 95 or memory > 95:
    print("Something is critically high")

# NOT
if not is_running:
    print("Server is down")

# Chained comparisons (Python-specific, very clean)
if 80 < cpu < 95:
    print("CPU in warning range")

if 0 <= disk <= 100:
    print("Disk usage is valid")
```

---

## for loops

```python
servers = ["web-01", "web-02", "db-01", "cache-01"]

# Basic for loop
for server in servers:
    print(f"Checking {server}...")

# With index — use enumerate, not range(len(x))
for index, server in enumerate(servers):
    print(f"{index + 1}. {server}")

# Loop over a range of numbers
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):       # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2):   # 0, 2, 4, 6, 8
    print(i)

# Loop over a dictionary
config = {"host": "10.0.1.1", "port": 8080, "debug": False}

for key in config:
    print(key)                          # keys only

for key, value in config.items():
    print(f"{key}: {value}")            # key-value pairs

for value in config.values():
    print(value)                        # values only
```

### break and continue

```python
servers = ["web-01", "web-02", "DOWN", "web-03", "web-04"]

# break — stop the loop entirely
for server in servers:
    if server == "DOWN":
        print("Found a down server, stopping check")
        break
    print(f"Checking {server}")

# continue — skip this iteration, go to next
for server in servers:
    if server == "DOWN":
        print(f"Skipping {server}")
        continue
    print(f"Checking {server}")
```

---

## while loops

```python
import time

# Retry logic — a classic DevOps pattern
max_retries = 3
attempt = 0

while attempt < max_retries:
    try:
        # try to connect to server
        connect_to_server()
        print("Connected!")
        break                   # success — exit loop
    except ConnectionError:
        attempt += 1
        print(f"Attempt {attempt} failed. Retrying in 5s...")
        time.sleep(5)
else:
    # the else runs if the while loop completed without break
    print("All retries exhausted. Giving up.")

# Infinite loop with break (polling pattern)
while True:
    status = check_deployment_status()
    if status == "complete":
        print("Deployment done!")
        break
    elif status == "failed":
        print("Deployment failed!")
        break
    print("Still deploying... checking again in 10s")
    time.sleep(10)
```

---

## List Comprehensions

A concise way to build lists. Once you learn these, you'll
use them all the time.

```python
servers = ["web-01", "web-02", "db-01", "cache-01", "web-03"]

# Without list comprehension
web_servers = []
for s in servers:
    if s.startswith("web"):
        web_servers.append(s)

# With list comprehension — same thing, one line
web_servers = [s for s in servers if s.startswith("web")]
# ["web-01", "web-02", "web-03"]

# Transform items
upper = [s.upper() for s in servers]
# ["WEB-01", "WEB-02", "DB-01", "CACHE-01", "WEB-03"]

# Both filter and transform
web_upper = [s.upper() for s in servers if s.startswith("web")]
# ["WEB-01", "WEB-02", "WEB-03"]

# Real example: extract IPs from a list of log lines
log_lines = [
    "10.0.1.1 GET /api/health 200",
    "10.0.1.2 POST /api/data 201",
    "10.0.1.1 GET /api/users 404",
]
ips = [line.split()[0] for line in log_lines]
# ["10.0.1.1", "10.0.1.2", "10.0.1.1"]
```

---

## Dictionary Comprehensions

Same idea, for dictionaries.

```python
servers = ["web-01", "web-02", "db-01"]
ports   = [80, 80, 5432]

# Build a dict from two lists
server_ports = {s: p for s, p in zip(servers, ports)}
# {"web-01": 80, "web-02": 80, "db-01": 5432}

# Filter a dict
config = {"host": "10.0.1.1", "port": 8080, "debug": True, "secret": "abc"}
safe_config = {k: v for k, v in config.items() if k != "secret"}
# {"host": "10.0.1.1", "port": 8080, "debug": True}
```

---

## Exception Handling

In scripts that run in production, you must handle errors
explicitly. Silent failures are worse than crashes.

```python
# Basic try/except
try:
    with open("/etc/nginx/nginx.conf") as f:
        content = f.read()
except FileNotFoundError:
    print("nginx config not found — is nginx installed?")

# Multiple exceptions
try:
    response = requests.get(url, timeout=5)
    data = response.json()
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.ConnectionError:
    print("Could not connect")
except ValueError:
    print("Response was not valid JSON")

# Catch any exception (use sparingly — too broad)
try:
    risky_operation()
except Exception as e:
    print(f"Something went wrong: {e}")

# finally — runs no matter what (great for cleanup)
f = None
try:
    f = open("important.log")
    process(f)
except IOError as e:
    print(f"Could not read file: {e}")
finally:
    if f:
        f.close()   # always close the file

# else — runs only if no exception was raised
try:
    result = int(user_input)
except ValueError:
    print("That's not a number")
else:
    print(f"Got number: {result}")   # only runs if try succeeded
```

---

## Practical Example — A Real Script Structure

```python
#!/usr/bin/env python3
"""
Check disk usage on a list of servers and alert if above threshold.
Shows how control flow comes together in a real script.
"""

import sys

SERVERS = ["web-01", "web-02", "db-01"]
DISK_THRESHOLD = 85     # alert if disk usage above this %

def get_disk_usage(server):
    """Simulate getting disk usage — in real life this would SSH to the server."""
    # Fake data for the example
    usage = {"web-01": 72, "web-02": 91, "db-01": 65}
    return usage.get(server)

def check_all_servers():
    alerts = []

    for server in SERVERS:
        usage = get_disk_usage(server)

        if usage is None:
            print(f"  {server}: could not retrieve disk usage")
            continue

        if usage > DISK_THRESHOLD:
            print(f"  {server}: {usage}% ⚠ ALERT")
            alerts.append(server)
        else:
            print(f"  {server}: {usage}% OK")

    return alerts

print("=== Disk Usage Check ===")
alerting_servers = check_all_servers()

if alerting_servers:
    print(f"\n{len(alerting_servers)} server(s) need attention: {', '.join(alerting_servers)}")
    sys.exit(1)     # exit with error code so CI/CD knows something is wrong
else:
    print("\nAll servers OK")
    sys.exit(0)
```
