# 10 — Parsing Formats

> Config files, API responses, log files — they all come in
> specific formats. This note covers the ones you'll encounter
> every day in DevOps.

---

## JSON

```python
import json

# Parse string → dict
text = '{"host": "web-01", "port": 8080, "ssl": true}'
data = json.loads(text)
print(data["host"])         # web-01
print(data["ssl"])          # True (Python bool)

# Read from file
with open("config.json") as f:
    config = json.load(f)

# Dict → string
data = {"server": "web-01", "healthy": True, "cpu": 87.5}
text = json.dumps(data)                 # compact
text = json.dumps(data, indent=2)       # pretty
text = json.dumps(data, indent=2, sort_keys=True)

# Write to file
with open("output.json", "w") as f:
    json.dump(data, f, indent=2)

# Handle dates (json doesn't support datetime natively)
from datetime import datetime
data = {"timestamp": datetime.now().isoformat(), "server": "web-01"}
# isoformat() gives: "2024-01-15T10:30:00"
```

---

## YAML

YAML is everywhere in DevOps — Kubernetes manifests, Docker Compose,
Ansible playbooks, GitHub Actions, Helm charts.

```bash
pip install pyyaml
```

```python
import yaml

# Parse YAML string
config_text = """
server:
  host: web-01
  port: 8080
  ssl: true

replicas: 3
tags:
  - web
  - production
"""
config = yaml.safe_load(config_text)    # always use safe_load, not load
print(config["server"]["host"])         # web-01
print(config["tags"])                   # ["web", "production"]

# Read YAML file
with open("config.yaml") as f:
    config = yaml.safe_load(f)

# Write YAML
data = {"server": "web-01", "replicas": 3, "tags": ["web", "prod"]}
with open("output.yaml", "w") as f:
    yaml.dump(data, f, default_flow_style=False)

# Multiple YAML documents in one file (---)
with open("k8s-manifests.yaml") as f:
    docs = list(yaml.safe_load_all(f))
    for doc in docs:
        print(doc["kind"])    # Deployment, Service, ConfigMap...
```

---

## INI / Config Files

```python
import configparser

# Read a config file:
# [database]
# host = 10.0.1.5
# port = 5432
# name = myapp_db
#
# [app]
# debug = false
# workers = 4

config = configparser.ConfigParser()
config.read("/etc/myapp/config.ini")

db_host = config["database"]["host"]        # 10.0.1.5
db_port = config.getint("database", "port") # 5432 as int
debug   = config.getboolean("app", "debug") # False as bool

# With defaults
timeout = config.get("app", "timeout", fallback="30")

# Write a config file
config = configparser.ConfigParser()
config["database"] = {"host": "10.0.1.5", "port": "5432"}
config["app"] = {"debug": "false", "workers": "4"}
with open("/etc/myapp/config.ini", "w") as f:
    config.write(f)
```

---

## CSV

```python
import csv

# Read CSV file
with open("servers.csv") as f:
    reader = csv.DictReader(f)          # first row = headers
    for row in reader:
        print(row["name"], row["ip"])

# All rows as a list of dicts
with open("servers.csv") as f:
    servers = list(csv.DictReader(f))

# Filter
web_servers = [s for s in servers if s["type"] == "web"]

# Write CSV
servers = [
    {"name": "web-01", "ip": "10.0.1.1", "type": "web"},
    {"name": "db-01",  "ip": "10.0.1.5", "type": "db"},
]
with open("output.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "ip", "type"])
    writer.writeheader()
    writer.writerows(servers)
```

---

## Environment Variables and .env Files

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
import os

# Load from .env file
load_dotenv()           # looks for .env in current directory
load_dotenv(".env.prod") # specific file

# Now use them as normal env vars
db_host = os.getenv("DB_HOST", "localhost")
db_pass = os.getenv("DB_PASSWORD")     # None if not set
api_key = os.environ["API_KEY"]        # KeyError if not set

# .env file looks like:
# DB_HOST=10.0.1.5
# DB_PASSWORD=supersecret
# API_KEY=abc123
# DEBUG=false
```

---

## Log Parsing with regex

```python
import re
from collections import Counter

# Parse nginx access log line:
# 10.0.1.5 - - [15/Jan/2024:10:30:00 +0000] "GET /api/health HTTP/1.1" 200 45

LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>\S+) \S+" '
    r'(?P<status>\d+) (?P<size>\d+)'
)

def parse_access_log(filepath):
    requests = []
    with open(filepath) as f:
        for line in f:
            match = LOG_PATTERN.match(line)
            if match:
                requests.append(match.groupdict())
    return requests

def analyze_logs(filepath):
    requests = parse_access_log(filepath)

    # Status code breakdown
    status_counts = Counter(r["status"] for r in requests)
    print("\nStatus codes:")
    for code, count in status_counts.most_common():
        print(f"  {code}: {count}")

    # Top paths
    path_counts = Counter(r["path"] for r in requests)
    print("\nTop 10 paths:")
    for path, count in path_counts.most_common(10):
        print(f"  {path}: {count}")

    # Error requests (4xx, 5xx)
    errors = [r for r in requests if r["status"].startswith(("4", "5"))]
    print(f"\nErrors: {len(errors)}/{len(requests)}")
```

---

## TOML (Python 3.11+ built-in)

```python
# Python 3.11+
import tomllib

with open("pyproject.toml", "rb") as f:     # must open in binary mode
    config = tomllib.load(f)

# Earlier Python versions
# pip install tomli
import tomli
with open("pyproject.toml", "rb") as f:
    config = tomli.load(f)

# TOML looks like:
# [tool.myapp]
# host = "web-01"
# port = 8080
# tags = ["web", "prod"]

print(config["tool"]["myapp"]["host"])
```
