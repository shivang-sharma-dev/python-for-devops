# 04 — Functions

---

## Why Functions Matter

Without functions, every script is a wall of code that runs
top to bottom. With functions, you break the problem into
named, reusable pieces.

```python
# Without functions — hard to read, hard to reuse
import subprocess
result = subprocess.run(["systemctl", "is-active", "nginx"],
                        capture_output=True, text=True)
nginx_status = result.stdout.strip()
if nginx_status != "active":
    subprocess.run(["systemctl", "start", "nginx"])

result = subprocess.run(["systemctl", "is-active", "postgresql"],
                        capture_output=True, text=True)
pg_status = result.stdout.strip()
if pg_status != "active":
    subprocess.run(["systemctl", "start", "postgresql"])

# With functions — clear, reusable
def ensure_service_running(service_name):
    result = subprocess.run(
        ["systemctl", "is-active", service_name],
        capture_output=True, text=True
    )
    if result.stdout.strip() != "active":
        subprocess.run(["systemctl", "start", service_name])
        print(f"Started {service_name}")

ensure_service_running("nginx")
ensure_service_running("postgresql")
```

---

## Defining and Calling Functions

```python
# Basic function
def greet():
    print("Hello from a function")

greet()     # call it

# With parameters
def check_threshold(value, threshold):
    if value > threshold:
        print(f"{value} exceeds threshold of {threshold}")
    else:
        print(f"{value} is within threshold")

check_threshold(87, 80)    # 87 exceeds threshold of 80
check_threshold(45, 80)    # 45 is within threshold

# Returning a value
def is_critical(cpu, memory):
    return cpu > 95 or memory > 95

if is_critical(97, 60):
    print("Take action immediately")
```

---

## Default Arguments

```python
def connect(host, port=22, timeout=30, user="ubuntu"):
    print(f"Connecting to {user}@{host}:{port} (timeout: {timeout}s)")

connect("web-01")                           # uses all defaults
connect("web-01", port=2222)               # override port only
connect("web-01", 8080, 10)               # positional
connect("db-01", user="postgres", port=5432)  # keyword args
```

---

## *args and **kwargs

```python
# *args — accept any number of positional arguments
def check_servers(*servers):
    for server in servers:
        print(f"Checking {server}")

check_servers("web-01")
check_servers("web-01", "web-02", "db-01")

# **kwargs — accept any number of keyword arguments
def create_tag(**tags):
    for key, value in tags.items():
        print(f"{key} = {value}")

create_tag(env="production", team="platform", cost_center="infra")

# Real use — building a flexible AWS tag dict
def make_tags(name, env, **extra):
    tags = {"Name": name, "Environment": env}
    tags.update(extra)
    return tags

tags = make_tags("web-01", "prod", team="platform", owner="alice")
# {"Name": "web-01", "Environment": "prod", "team": "platform", "owner": "alice"}
```

---

## Return Values

```python
# Return a single value
def get_disk_percent(path="/"):
    import shutil
    total, used, free = shutil.disk_usage(path)
    return round(used / total * 100, 1)

usage = get_disk_percent()
print(f"Disk: {usage}%")

# Return multiple values (Python returns a tuple)
def get_system_stats():
    import shutil, os
    total, used, free = shutil.disk_usage("/")
    load = os.getloadavg()[0]           # 1-minute load average
    return round(used / total * 100, 1), load

disk, load = get_system_stats()         # unpack the tuple
print(f"Disk: {disk}%, Load: {load}")

# Return a dict for multiple named values
def get_server_info(name):
    return {
        "name": name,
        "ip": "10.0.1.1",
        "status": "running",
        "uptime_days": 42
    }

info = get_server_info("web-01")
print(info["status"])                   # running
```

---

## Docstrings — Document Your Functions

```python
def check_disk_usage(path, threshold=90):
    """
    Check disk usage at the given path.

    Args:
        path (str): Filesystem path to check (e.g. "/" or "/data")
        threshold (int): Alert threshold in percent. Default is 90.

    Returns:
        tuple: (usage_percent, is_alert)
            usage_percent (float): Current disk usage as a percentage
            is_alert (bool): True if usage exceeds threshold

    Example:
        usage, alert = check_disk_usage("/", threshold=85)
        if alert:
            send_alert(f"Disk at {usage}%")
    """
    import shutil
    total, used, free = shutil.disk_usage(path)
    usage = round(used / total * 100, 1)
    return usage, usage > threshold

# Access the docstring
help(check_disk_usage)
print(check_disk_usage.__doc__)
```

---

## Variable Scope

```python
# Variables inside a function are LOCAL — not visible outside
def my_function():
    local_var = "I only exist inside this function"
    print(local_var)    # works

my_function()
# print(local_var)    # NameError — doesn't exist out here

# Variables outside a function are GLOBAL — visible inside (read-only)
MAX_RETRIES = 3

def retry_connection():
    print(f"Will retry {MAX_RETRIES} times")    # can read it
    # MAX_RETRIES = 5    # this creates a new LOCAL variable, doesn't change global

# To modify a global variable inside a function (avoid this pattern)
counter = 0
def increment():
    global counter
    counter += 1

# Better pattern: pass values in and return them out
def increment(counter):
    return counter + 1

counter = increment(counter)
```

---

## Lambda Functions

Small anonymous functions for simple operations.

```python
# Regular function
def double(x):
    return x * 2

# Lambda equivalent
double = lambda x: x * 2

# Where lambdas shine — as arguments to other functions
servers = [
    {"name": "web-01", "cpu": 87},
    {"name": "db-01",  "cpu": 23},
    {"name": "web-02", "cpu": 65},
]

# Sort by CPU usage
sorted_servers = sorted(servers, key=lambda s: s["cpu"])
# Sort highest first
sorted_servers = sorted(servers, key=lambda s: s["cpu"], reverse=True)

# Filter high CPU servers
high_cpu = list(filter(lambda s: s["cpu"] > 80, servers))

# Map — apply function to all items
names = list(map(lambda s: s["name"], servers))
# ["web-01", "db-01", "web-02"]
```

---

## Practical Example — A Script With Good Function Design

```python
#!/usr/bin/env python3
"""
Server health check script.
Shows how to break a real task into clean, focused functions.
"""

import subprocess
import sys
from datetime import datetime

SERVICES = ["nginx", "postgresql", "redis"]
CPU_THRESHOLD = 80


def get_service_status(service):
    """Return 'active' or 'inactive' for a systemd service."""
    result = subprocess.run(
        ["systemctl", "is-active", service],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()


def get_cpu_usage():
    """Return current CPU usage as a percentage (float)."""
    result = subprocess.run(
        ["top", "-bn1"],
        capture_output=True,
        text=True
    )
    for line in result.stdout.splitlines():
        if "Cpu(s)" in line:
            idle = float(line.split()[7].replace(",", "."))
            return round(100 - idle, 1)
    return None


def check_services(services):
    """Check all services and return a list of failed ones."""
    failed = []
    for service in services:
        status = get_service_status(service)
        symbol = "✓" if status == "active" else "✗"
        print(f"  {symbol} {service}: {status}")
        if status != "active":
            failed.append(service)
    return failed


def run_health_check():
    """Main health check — runs all checks and reports."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n=== Health Check [{timestamp}] ===\n")

    print("Services:")
    failed_services = check_services(SERVICES)

    print("\nCPU:")
    cpu = get_cpu_usage()
    if cpu is not None:
        status = "⚠ HIGH" if cpu > CPU_THRESHOLD else "OK"
        print(f"  Usage: {cpu}% {status}")

    # Summary
    issues = len(failed_services)
    if cpu and cpu > CPU_THRESHOLD:
        issues += 1

    print(f"\nResult: {'ISSUES FOUND' if issues else 'ALL OK'}")
    return issues == 0


if __name__ == "__main__":
    healthy = run_health_check()
    sys.exit(0 if healthy else 1)
```
