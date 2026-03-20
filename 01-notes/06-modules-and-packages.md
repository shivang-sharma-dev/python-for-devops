# 06 — Modules and Packages

---

## What is a Module?

A module is just a Python file. When you write `import os`,
Python finds `os.py` somewhere on your system and loads it.
That's all there is to it.

```python
# myutils.py — this IS a module
def check_disk(path="/"):
    import shutil
    total, used, free = shutil.disk_usage(path)
    return round(used / total * 100, 1)

def ping(host):
    import subprocess
    result = subprocess.run(["ping", "-c", "1", host], capture_output=True)
    return result.returncode == 0

# main.py — import and use the module
import myutils

usage = myutils.check_disk("/")
reachable = myutils.ping("8.8.8.8")
```

---

## Ways to Import

```python
# Import the whole module
import os
import subprocess
os.getcwd()                     # must prefix with module name

# Import specific things from a module
from os import getcwd, listdir
from pathlib import Path
getcwd()                        # no prefix needed

# Import with alias (for long names)
import subprocess as sp
sp.run(["ls"])

# Import everything (avoid — pollutes namespace)
from os import *

# Best practice: one import per line, alphabetical
import os
import subprocess
import sys
from pathlib import Path
```

---

## The Standard Library — What You'll Actually Use

These ship with Python. No installation needed.

### os — Operating System

```python
import os

os.getcwd()                         # current directory
os.chdir("/tmp")                    # change directory
os.listdir("/etc")                  # list directory contents
os.path.exists("/etc/nginx")        # does path exist?
os.path.isfile("/etc/nginx/nginx.conf")  # is it a file?
os.path.isdir("/etc/nginx")         # is it a directory?
os.path.join("/var", "log", "nginx") # build a path safely
os.path.basename("/var/log/nginx/access.log")  # "access.log"
os.path.dirname("/var/log/nginx/access.log")   # "/var/log/nginx"
os.path.splitext("access.log")      # ("access", ".log")
os.makedirs("/tmp/myapp/logs", exist_ok=True)  # create directories
os.remove("/tmp/file.txt")          # delete file
os.rename("old.txt", "new.txt")     # rename
os.getenv("HOME")                   # read environment variable
os.getenv("DB_PASSWORD", "default") # with default
os.environ["APP_ENV"] = "production" # set environment variable
os.getpid()                         # current process ID
os.cpu_count()                      # number of CPUs
```

### pathlib — Modern File Paths

```python
from pathlib import Path

p = Path("/var/log/nginx/access.log")

p.name          # "access.log"
p.stem          # "access"
p.suffix        # ".log"
p.parent        # Path("/var/log/nginx")
p.exists()      # True/False
p.is_file()     # True/False
p.is_dir()      # True/False
p.stat().st_size    # file size in bytes

# Build paths with /
log_dir = Path("/var/log")
nginx_log = log_dir / "nginx" / "access.log"

# Read and write files
content = p.read_text()
p.write_text("new content")

# List files in a directory
for f in Path("/etc").iterdir():
    print(f)

# Find all .log files recursively
for log in Path("/var/log").rglob("*.log"):
    print(log)

# Create directories
Path("/tmp/myapp/logs").mkdir(parents=True, exist_ok=True)
```

### sys — System and Interpreter

```python
import sys

sys.argv                # command line arguments as a list
sys.argv[0]             # script name
sys.argv[1]             # first argument

sys.exit(0)             # exit with code 0 (success)
sys.exit(1)             # exit with code 1 (error)

sys.path                # where Python looks for modules
sys.version             # Python version string

sys.stdout.write("no newline")   # write without print
sys.stderr.write("error msg\n")  # write to stderr

print("error", file=sys.stderr)  # print to stderr
```

### subprocess — Run Shell Commands

```python
import subprocess

# Run a command, capture output
result = subprocess.run(
    ["df", "-h", "/"],
    capture_output=True,
    text=True               # decode bytes to string
)
print(result.stdout)        # command output
print(result.stderr)        # error output
print(result.returncode)    # 0 = success

# Check if command succeeded
result = subprocess.run(["systemctl", "is-active", "nginx"],
                        capture_output=True, text=True)
if result.returncode == 0:
    print("nginx is running")

# Run and raise exception if it fails
subprocess.run(["systemctl", "start", "nginx"], check=True)
# Raises CalledProcessError if nginx fails to start
```

### json — Parse and Write JSON

```python
import json

# Parse JSON string → Python dict
text = '{"host": "web-01", "port": 8080}'
data = json.loads(text)
print(data["host"])     # web-01

# Read JSON file
with open("config.json") as f:
    config = json.load(f)

# Write Python dict → JSON string
data = {"server": "web-01", "healthy": True}
text = json.dumps(data)                     # compact
text = json.dumps(data, indent=2)           # pretty printed

# Write JSON file
with open("output.json", "w") as f:
    json.dump(data, f, indent=2)
```

### datetime — Dates and Times

```python
from datetime import datetime, timedelta

now = datetime.now()
print(now.strftime("%Y-%m-%d %H:%M:%S"))   # 2024-01-15 10:30:00

# Parse a date string
dt = datetime.strptime("2024-01-15", "%Y-%m-%d")

# Arithmetic
yesterday = now - timedelta(days=1)
next_week = now + timedelta(weeks=1)

# Timestamps (for log file names)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"backup_{timestamp}.tar.gz"
# backup_20240115_103000.tar.gz
```

### re — Regular Expressions

```python
import re

log = "2024-01-15 10:30:00 ERROR [nginx] connection refused from 10.0.1.5"

# Search — find first match
match = re.search(r"\d+\.\d+\.\d+\.\d+", log)
if match:
    print(match.group())    # 10.0.1.5

# Find all matches
ips = re.findall(r"\d+\.\d+\.\d+\.\d+", log)

# Match from start of string
match = re.match(r"(\d{4}-\d{2}-\d{2})", log)
date = match.group(1)       # 2024-01-15

# Substitute
clean = re.sub(r"\d+\.\d+\.\d+\.\d+", "REDACTED", log)

# Split
parts = re.split(r"\s+", log)   # split on whitespace
```

---

## Installing Third-Party Packages

```bash
# Always activate your venv first
source venv/bin/activate

pip install requests        # HTTP library
pip install boto3           # AWS SDK
pip install pyyaml          # YAML parsing
pip install click           # CLI tools
pip install rich            # beautiful terminal output
pip install paramiko        # SSH from Python
pip install python-dotenv   # load .env files
```

---

## The __name__ == "__main__" Pattern

Every Python file you write should follow this pattern:

```python
#!/usr/bin/env python3
"""
disk_check.py — Check disk usage and alert if high.
"""

def check_disk(path="/", threshold=90):
    """Check disk usage at path. Return (usage_pct, is_alert)."""
    import shutil
    total, used, free = shutil.disk_usage(path)
    usage = round(used / total * 100, 1)
    return usage, usage > threshold


def main():
    usage, alert = check_disk("/", threshold=85)
    print(f"Disk: {usage}%")
    if alert:
        print("ALERT: Disk usage is high!")


# This block only runs when the script is run directly
# NOT when it's imported by another module
if __name__ == "__main__":
    main()
```

Why this matters:

```python
# If another script imports your module:
import disk_check

result = disk_check.check_disk("/data")   # works, uses the function
# main() does NOT run — that's the whole point
```

This makes your scripts both importable (as a library) and
runnable (as a standalone script).
