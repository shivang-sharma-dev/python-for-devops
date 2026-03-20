# 02 — Variables and Data Types

---

## Variables

A variable is a name that points to a value. That's it.

```python
# Assign with =
server_name = "web-01"
port = 8080
is_running = True
cpu_usage = 87.5

# Python figures out the type automatically (dynamic typing)
# You don't write: string server_name = "web-01" like in Java/C

# Check the type
print(type(server_name))   # <class 'str'>
print(type(port))          # <class 'int'>
print(type(cpu_usage))     # <class 'float'>
print(type(is_running))    # <class 'bool'>

# Multiple assignment
host = port = timeout = None    # all point to None

# Swap values (Python makes this clean)
a, b = 10, 20
a, b = b, a     # a=20, b=10 now
```

### Naming conventions

```python
# Use snake_case for everything in Python (not camelCase)
server_name = "web-01"        # good
serverName  = "web-01"        # bad — works but against convention

# Constants are UPPER_CASE (convention only, not enforced)
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
AWS_REGION = "us-east-1"

# Descriptive names — your future self will thank you
x = 86400          # bad — what is x?
seconds_per_day = 86400  # good
```

---

## Strings

Strings are how you work with text — server names, log lines,
file paths, API responses. You'll use them constantly.

```python
# Three ways to create strings
single = 'web-01'
double = "web-01"
multi  = """
This is a
multi-line string
"""

# f-strings — the best way to embed variables in strings
server = "web-01"
port = 8080
print(f"Connecting to {server}:{port}")
# Connecting to web-01:8080

# You can put expressions inside {}
print(f"2 + 2 = {2 + 2}")
print(f"Server: {server.upper()}")
print(f"Disk: {87.3:.1f}%")    # format to 1 decimal place
```

### String methods you'll use constantly

```python
line = "  ERROR: disk usage at 95%  "

line.strip()                    # "ERROR: disk usage at 95%"  (remove whitespace)
line.lower()                    # "  error: disk usage at 95%  "
line.upper()                    # "  ERROR: DISK USAGE AT 95%  "
line.replace("ERROR", "WARN")  # "  WARN: disk usage at 95%  "
line.split(":")                 # ['  ERROR', ' disk usage at 95%  ']
line.startswith("  ERROR")      # True
line.endswith("%  ")            # True
"95" in line                    # True
line.count("9")                 # 1

# Split a log line into parts
log = "2024-01-15 10:30:00 ERROR nginx failed to start"
parts = log.split(" ", 3)       # split on space, max 3 splits
date, time, level, message = parts
print(level)    # ERROR
print(message)  # nginx failed to start

# Join a list back into a string
servers = ["web-01", "web-02", "web-03"]
print(", ".join(servers))       # web-01, web-02, web-03
print("\n".join(servers))       # one per line
```

### String formatting for paths and commands

```python
import os

# Build file paths properly (don't concatenate with +)
log_dir = "/var/log"
app = "nginx"
log_file = os.path.join(log_dir, app, "error.log")
# /var/log/nginx/error.log

# Or use pathlib (modern way)
from pathlib import Path
log_file = Path("/var/log") / "nginx" / "error.log"
print(log_file)         # /var/log/nginx/error.log
print(log_file.name)    # error.log
print(log_file.parent)  # /var/log/nginx
print(log_file.suffix)  # .log
```

---

## Numbers

```python
# Integers
count = 0
max_connections = 1000
port = 8080

# Floats
cpu = 87.5
threshold = 0.95

# Basic math
total = 10 + 5      # 15
diff  = 10 - 5      # 5
prod  = 10 * 5      # 50
quot  = 10 / 5      # 2.0  (always float with /)
floor = 10 // 3     # 3    (integer division)
mod   = 10 % 3      # 1    (remainder)
power = 2 ** 10     # 1024 (exponent)

# Convert between types
int("42")           # 42    string to int
float("3.14")       # 3.14  string to float
str(8080)           # "8080" int to string
int(3.9)            # 3     float to int (truncates, doesn't round)
round(3.9)          # 4

# Useful built-ins
abs(-5)             # 5
min(3, 1, 4, 1, 5) # 1
max(3, 1, 4, 1, 5) # 5
sum([1, 2, 3, 4])   # 10
```

---

## Booleans

```python
is_healthy = True
is_down    = False

# Comparison operators — all return True or False
5 > 3       # True
5 < 3       # False
5 == 5      # True  (== not = for comparison)
5 != 3      # True
5 >= 5      # True
5 <= 4      # False

# Logical operators
True and False   # False  (both must be True)
True or False    # True   (at least one must be True)
not True         # False

# Real example
cpu = 87
memory = 92
disk = 45

if cpu > 80 and memory > 80:
    print("ALERT: Both CPU and memory are high")

if cpu > 95 or memory > 95:
    print("CRITICAL: Resource usage dangerously high")
```

### Truthy and Falsy — important to understand

```python
# These are all "falsy" in Python (evaluate to False in if statements)
False
None
0
0.0
""         # empty string
[]         # empty list
{}         # empty dict
()         # empty tuple

# Everything else is "truthy"

# So you can write:
servers = []
if not servers:
    print("No servers found")   # prints this

servers = ["web-01"]
if servers:
    print(f"Found {len(servers)} server(s)")  # prints this
```

---

## None

`None` is Python's way of saying "no value". Different from 0
or empty string — those are values. `None` means absence of value.

```python
result = None           # not set yet

def get_server_ip(name):
    # returns None if server not found
    servers = {"web-01": "10.0.1.1", "web-02": "10.0.1.2"}
    return servers.get(name)   # returns None if key missing

ip = get_server_ip("web-99")
if ip is None:              # use 'is None', not '== None'
    print("Server not found")

# Common pattern: default value if None
ip = get_server_ip("web-99") or "unknown"
print(ip)   # "unknown"
```

---

## Type Checking and Conversion

```python
# Check type
isinstance("hello", str)    # True
isinstance(42, int)          # True
isinstance(42, (int, float)) # True — is it int OR float?

# Common conversions in DevOps scripts
port_str = "8080"
port = int(port_str)        # "8080" → 8080

threshold = "0.95"
threshold = float(threshold) # "0.95" → 0.95

count = 42
count_str = str(count)      # 42 → "42"

# Boolean conversion
bool(1)     # True
bool(0)     # False
bool("")    # False
bool("no")  # True  (non-empty string is truthy — even "false"!)
```

---

## Practical Example — Putting It Together

```python
#!/usr/bin/env python3
"""
Read server metrics and check thresholds.
This is the kind of thing you'd write in week 1 of a DevOps role.
"""

# Server data (would come from an API or config in real life)
server_name = "web-01"
cpu_usage   = 87.5       # percent
memory_free = 512        # MB
disk_usage  = 92         # percent
is_running  = True

# Thresholds
CPU_THRESHOLD  = 80      # alert if above this
DISK_THRESHOLD = 90      # alert if above this

# Check and report
print(f"=== Health Check: {server_name} ===")
print(f"  CPU:    {cpu_usage}%  {'⚠ HIGH' if cpu_usage > CPU_THRESHOLD else 'OK'}")
print(f"  Memory: {memory_free}MB free")
print(f"  Disk:   {disk_usage}%  {'⚠ HIGH' if disk_usage > DISK_THRESHOLD else 'OK'}")
print(f"  Status: {'Running' if is_running else 'DOWN'}")
```

Output:
```
=== Health Check: web-01 ===
  CPU:    87.5%  ⚠ HIGH
  Memory: 512MB free
  Disk:   92%  ⚠ HIGH
  Status: Running
```
