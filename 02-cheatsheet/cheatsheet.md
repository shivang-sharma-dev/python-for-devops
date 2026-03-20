# Python for DevOps — Cheatsheet

---

## Setup
```bash
python3 --version
python3 -m venv venv
source venv/bin/activate
pip install requests boto3 pyyaml click rich python-dotenv
pip freeze > requirements.txt
pip install -r requirements.txt
deactivate
```

---

## Variables and Strings
```python
name = "web-01"
port = 8080
cpu  = 87.5
alive = True

# f-strings
print(f"Server: {name}:{port}")
print(f"CPU: {cpu:.1f}%")

# String methods
line.strip()           # remove whitespace
line.split(":")        # split into list
line.replace("a","b")  # replace
line.startswith("ERR") # True/False
line.upper()           # uppercase
"ERROR" in line        # True/False
", ".join(servers)     # list to string
```

---

## Control Flow
```python
if cpu > 95:
    print("CRITICAL")
elif cpu > 80:
    print("WARNING")
else:
    print("OK")

# One-liner
status = "HIGH" if cpu > 80 else "OK"

# for loop
for server in servers:
    print(server)

for i, server in enumerate(servers, 1):
    print(f"{i}. {server}")

# while with retry
while attempt < max_retries:
    try:
        connect()
        break
    except Exception:
        attempt += 1
        time.sleep(5)

# List comprehension
web = [s for s in servers if s.startswith("web")]
upper = [s.upper() for s in servers]

# Dict comprehension
ports = {s: 80 for s in servers}
```

---

## Functions
```python
def check(host, port=22, timeout=30):
    """Check if host:port is reachable."""
    pass

# *args and **kwargs
def check_all(*servers):
    for s in servers: check(s)

def make_tags(**kwargs):
    return kwargs

# Lambda
sorted_by_cpu = sorted(instances, key=lambda i: i["cpu"])

# Return multiple values
def stats():
    return cpu, memory, disk

c, m, d = stats()
```

---

## Data Structures
```python
# List
servers = ["web-01", "web-02"]
servers.append("web-03")
servers.remove("web-01")
len(servers)
"web-01" in servers
sorted(servers)

# Dict
server = {"name": "web-01", "ip": "10.0.1.1", "port": 80}
server["port"]              # access
server.get("port", 80)      # safe access with default
server.keys()
server.values()
server.items()
server.update({"cpu": 45})

# Set (unique items)
unique_ips = set(ip_list)
set_a & set_b    # intersection
set_a | set_b    # union
set_a - set_b    # difference

# Counter
from collections import Counter
counts = Counter(["ERROR","INFO","ERROR"])
counts.most_common(3)

# defaultdict
from collections import defaultdict
by_region = defaultdict(list)
by_region["us-east-1"].append("web-01")
```

---

## File Operations
```python
# Read
with open("/etc/hostname") as f:
    hostname = f.read().strip()

with open("access.log") as f:
    errors = [l.strip() for l in f if "ERROR" in l]

# Write
with open("report.txt", "w") as f:
    f.write("Server Report\n")

# Append
with open("app.log", "a") as f:
    f.write(f"{timestamp} INFO started\n")

# pathlib
from pathlib import Path
p = Path("/var/log/nginx/access.log")
p.exists()
p.is_file()
p.name         # access.log
p.parent       # /var/log/nginx
p.stat().st_size

# Find files
for f in Path("/var/log").rglob("*.log"):
    print(f)

# Create dirs
Path("/tmp/myapp/logs").mkdir(parents=True, exist_ok=True)
```

---

## subprocess
```python
import subprocess

# Run command
result = subprocess.run(
    ["systemctl", "status", "nginx"],
    capture_output=True,
    text=True
)
print(result.stdout)
print(result.returncode)   # 0 = success

# Raise on failure
subprocess.run(["systemctl", "start", "nginx"], check=True)

# Shell pipeline
result = subprocess.run(
    "ps aux | grep python",
    shell=True, capture_output=True, text=True
)

# With timeout
result = subprocess.run(cmd, timeout=30, capture_output=True, text=True)

# Helpers
def is_running(service):
    r = subprocess.run(["systemctl","is-active",service],
                       capture_output=True, text=True)
    return r.stdout.strip() == "active"
```

---

## HTTP / APIs
```python
import requests

# GET
r = requests.get("https://api.example.com/data", timeout=10)
r.status_code       # 200
r.json()            # parse JSON response
r.raise_for_status()# raise on 4xx/5xx

# With auth + headers
r = requests.get(url,
    headers={"Authorization": "Bearer TOKEN"},
    params={"page": 1},
    timeout=10
)

# POST JSON
r = requests.post(url,
    json={"key": "value"},
    timeout=10
)

# Session (reuse connection)
session = requests.Session()
session.headers.update({"Authorization": "Bearer TOKEN"})
r = session.get("https://api.example.com/users")
```

---

## Parsing Formats
```python
import json, yaml, configparser, csv
from dotenv import load_dotenv
import os

# JSON
data = json.loads(text)
text = json.dumps(data, indent=2)
with open("f.json") as f: data = json.load(f)
with open("f.json","w") as f: json.dump(data, f, indent=2)

# YAML
with open("config.yaml") as f:
    config = yaml.safe_load(f)

# INI
config = configparser.ConfigParser()
config.read("config.ini")
config["section"]["key"]
config.getint("section", "key")
config.getboolean("section", "key")

# CSV
with open("servers.csv") as f:
    rows = list(csv.DictReader(f))

# .env files
load_dotenv()
db = os.getenv("DB_HOST", "localhost")
```

---

## Error Handling and Logging
```python
import logging, sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

log.info("Started")
log.warning("Disk high")
log.error("Failed to connect")
log.exception("Unhandled error")  # includes traceback

# Exception handling
try:
    risky()
except FileNotFoundError:
    log.error("File not found")
    sys.exit(1)
except Exception:
    log.exception("Unexpected error")
    raise

# Exit codes
sys.exit(0)   # success
sys.exit(1)   # failure
```

---

## boto3 (AWS)
```python
import boto3

# EC2
ec2 = boto3.resource("ec2", region_name="us-east-1")
for i in ec2.instances.all():
    print(i.id, i.state["Name"])

running = ec2.instances.filter(
    Filters=[{"Name":"instance-state-name","Values":["running"]}]
)

# S3
s3 = boto3.client("s3")
s3.upload_file("local.txt", "my-bucket", "remote.txt")
s3.download_file("my-bucket", "remote.txt", "local.txt")

paginator = s3.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket="my-bucket"):
    for obj in page.get("Contents", []):
        print(obj["Key"])

# Error handling
from botocore.exceptions import ClientError
try:
    s3.head_object(Bucket="bucket", Key="file")
except ClientError as e:
    if e.response["Error"]["Code"] == "404":
        print("Not found")
```

---

## CLI with click
```python
import click

@click.group()
def cli(): pass

@cli.command()
@click.argument("path", default="/")
@click.option("--threshold", "-t", default=90, show_default=True)
@click.option("--json", "as_json", is_flag=True)
def disk(path, threshold, as_json):
    """Check disk usage at PATH."""
    pass

@cli.command()
@click.argument("services", nargs=-1, required=True)
def check(services):
    """Check systemd services."""
    pass

if __name__ == "__main__":
    cli()
```

---

## Automation Patterns
```python
# Retry with backoff
import time

def with_retry(func, retries=3, delay=5):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            if attempt == retries - 1: raise
            time.sleep(delay * (2 ** attempt))

# Idempotency check
def add_if_missing(item, filepath):
    existing = Path(filepath).read_text().splitlines() \
               if Path(filepath).exists() else []
    if item not in existing:
        with open(filepath, "a") as f:
            f.write(f"{item}\n")

# Lock file
import fcntl
lock = open("/tmp/script.lock", "w")
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)

# Environment variables
import os
DEBUG   = os.getenv("DEBUG", "false").lower() == "true"
PORT    = int(os.getenv("PORT", "8080"))
API_KEY = os.environ["API_KEY"]   # raises if missing
```

---

## Useful One-Liners
```python
# Disk usage percent
import shutil
used_pct = shutil.disk_usage("/").used / shutil.disk_usage("/").total * 100

# Load average
import os
load_1min = os.getloadavg()[0]

# Current timestamp for filenames
from datetime import datetime
ts = datetime.now().strftime("%Y%m%d_%H%M%S")

# Flatten list of lists
flat = [x for sublist in nested for x in sublist]

# Unique items preserving order
seen = set()
unique = [x for x in items if not (x in seen or seen.add(x))]

# Read env file into dict
env = dict(line.strip().split("=",1) for line in open(".env")
           if line.strip() and not line.startswith("#"))
```
