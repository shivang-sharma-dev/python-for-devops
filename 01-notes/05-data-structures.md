# 05 — Data Structures

---

## Lists

An ordered collection of items. The go-to for storing sequences
of things — servers, log lines, IP addresses, task results.

```python
servers = ["web-01", "web-02", "db-01", "cache-01"]

# Access by index (0-based)
servers[0]      # "web-01"  (first)
servers[-1]     # "cache-01" (last)
servers[1:3]    # ["web-02", "db-01"] (slice)

# Modify
servers.append("web-03")               # add to end
servers.insert(0, "lb-01")             # insert at index
servers.extend(["mon-01", "mon-02"])   # add multiple
servers.remove("db-01")                # remove by value
servers.pop()                          # remove and return last
servers.pop(0)                         # remove and return by index

# Info
len(servers)                    # count
"web-01" in servers             # True/False
servers.index("web-02")         # find index of value
servers.count("web-01")         # how many times it appears

# Sort
servers.sort()                  # sort in place (modifies list)
sorted_copy = sorted(servers)   # return sorted copy (original unchanged)
servers.sort(reverse=True)      # reverse sort

# Iterate
for server in servers:
    print(server)

for i, server in enumerate(servers, 1):    # start counting at 1
    print(f"{i}. {server}")
```

### Lists of dicts — very common in DevOps

```python
instances = [
    {"id": "i-001", "name": "web-01", "state": "running", "cpu": 45},
    {"id": "i-002", "name": "web-02", "state": "running", "cpu": 87},
    {"id": "i-003", "name": "db-01",  "state": "stopped", "cpu": 0},
]

# Filter running instances
running = [i for i in instances if i["state"] == "running"]

# Sort by CPU usage (highest first)
by_cpu = sorted(instances, key=lambda i: i["cpu"], reverse=True)

# Get just the names
names = [i["name"] for i in instances]

# Find high-CPU instances
high_cpu = [i for i in instances if i["cpu"] > 80]
for i in high_cpu:
    print(f"{i['name']}: {i['cpu']}% CPU")
```

---

## Dictionaries

Key-value pairs. The most used data structure in Python DevOps
work — API responses, config files, and AWS SDK responses all
come back as dicts.

```python
server = {
    "name":    "web-01",
    "ip":      "10.0.1.1",
    "port":    80,
    "running": True,
    "tags":    ["web", "production"]
}

# Access
server["name"]                  # "web-01"
server.get("name")              # "web-01" (same, but safer)
server.get("missing_key")       # None (doesn't crash)
server.get("missing_key", "?")  # "?" (default value)

# Modify
server["port"] = 443                    # update
server["region"] = "us-east-1"         # add new key
del server["tags"]                      # delete key

# Check existence
"name" in server                # True
"missing" in server             # False

# Iterate
for key in server:
    print(key)

for key, value in server.items():
    print(f"{key}: {value}")

# Useful methods
server.keys()                   # all keys
server.values()                 # all values
server.items()                  # all (key, value) pairs
server.update({"cpu": 87, "memory": 65})  # merge another dict

# Merge two dicts (Python 3.9+)
defaults = {"port": 80, "timeout": 30}
overrides = {"port": 443, "debug": True}
merged = defaults | overrides
# {"port": 443, "timeout": 30, "debug": True}
```

### Nested dicts — AWS SDK returns these constantly

```python
aws_response = {
    "Reservations": [
        {
            "Instances": [
                {
                    "InstanceId": "i-001",
                    "State": {"Code": 16, "Name": "running"},
                    "Tags": [
                        {"Key": "Name", "Value": "web-01"},
                        {"Key": "Env",  "Value": "production"}
                    ]
                }
            ]
        }
    ]
}

# Navigate nested structure
instance = aws_response["Reservations"][0]["Instances"][0]
print(instance["InstanceId"])       # i-001
print(instance["State"]["Name"])    # running

# Extract tags into a simpler dict
tags = {t["Key"]: t["Value"] for t in instance["Tags"]}
# {"Name": "web-01", "Env": "production"}
print(tags["Name"])    # web-01
```

---

## Sets

Unordered collections of unique items. Perfect for deduplication
and membership testing.

```python
# Create
active_servers = {"web-01", "web-02", "db-01"}
failed_servers  = {"web-02", "cache-01"}

# Deduplication — main use case
ips_from_logs = ["10.0.1.1", "10.0.1.2", "10.0.1.1", "10.0.1.3", "10.0.1.2"]
unique_ips = set(ips_from_logs)
# {"10.0.1.1", "10.0.1.2", "10.0.1.3"}

# Set operations
active_servers & failed_servers     # intersection: {"web-02"}
active_servers | failed_servers     # union: all servers
active_servers - failed_servers     # difference: in active but not failed
active_servers ^ failed_servers     # symmetric difference: in one but not both

# Membership (sets are MUCH faster than lists for this)
"web-01" in active_servers          # True

# Modify
active_servers.add("web-03")
active_servers.remove("web-01")     # raises error if not found
active_servers.discard("missing")   # no error if not found
```

---

## Tuples

Like lists but immutable — can't be changed after creation.
Use for data that should not change.

```python
# Create
coordinates = (40.7128, -74.0060)     # lat, lon of New York
rgb = (255, 128, 0)

# Access (same as list)
coordinates[0]      # 40.7128
coordinates[-1]     # -74.0060

# Unpack
lat, lon = coordinates
r, g, b = rgb

# Named tuples — much more readable
from collections import namedtuple

Server = namedtuple("Server", ["name", "ip", "port"])
web01 = Server("web-01", "10.0.1.1", 80)
print(web01.name)   # web-01
print(web01.ip)     # 10.0.1.1

# Functions that return multiple values actually return tuples
def disk_stats():
    return 85.2, 14.8, True    # used, free, is_alert

used, free, alert = disk_stats()
```

---

## Choosing the Right Data Structure

```
Need to store items in order?         → list
Need fast key-value lookup?           → dict
Need unique items / deduplication?   → set
Need immutable sequence?             → tuple
Need to count occurrences?           → collections.Counter
Need dict with default values?       → collections.defaultdict

Examples:
  Log lines in order          → list
  Config file values          → dict
  Unique IP addresses         → set
  RGB color values            → tuple
  Word frequency in logs      → Counter
  Group servers by region     → defaultdict(list)
```

---

## collections module — The Extras

```python
from collections import Counter, defaultdict, namedtuple

# Counter — count occurrences
log_levels = ["ERROR", "INFO", "ERROR", "WARNING", "ERROR", "INFO"]
counts = Counter(log_levels)
print(counts)               # Counter({'ERROR': 3, 'INFO': 2, 'WARNING': 1})
print(counts["ERROR"])      # 3
print(counts.most_common(2)) # [('ERROR', 3), ('INFO', 2)]

# Real use: count HTTP status codes from access log
import re
with open("/var/log/nginx/access.log") as f:
    codes = Counter(re.search(r'" (\d{3}) ', line).group(1)
                    for line in f
                    if re.search(r'" (\d{3}) ', line))
print(codes.most_common())

# defaultdict — dict that creates default values automatically
servers_by_region = defaultdict(list)
servers_by_region["us-east-1"].append("web-01")   # no KeyError!
servers_by_region["us-east-1"].append("web-02")
servers_by_region["eu-west-1"].append("web-03")

for region, servers in servers_by_region.items():
    print(f"{region}: {', '.join(servers)}")
```

---

## Practical Example — Processing AWS Instance Data

```python
#!/usr/bin/env python3
"""
Process a list of EC2 instances (as if returned from boto3)
and produce a clean summary. Shows real use of dicts and lists.
"""

instances = [
    {"id": "i-001", "name": "web-01", "type": "t3.medium",  "state": "running",  "region": "us-east-1", "cpu": 45},
    {"id": "i-002", "name": "web-02", "type": "t3.medium",  "state": "running",  "region": "us-east-1", "cpu": 87},
    {"id": "i-003", "name": "db-01",  "type": "r5.large",   "state": "running",  "region": "us-east-1", "cpu": 22},
    {"id": "i-004", "name": "web-03", "type": "t3.medium",  "state": "stopped",  "region": "eu-west-1", "cpu": 0},
    {"id": "i-005", "name": "cache",  "type": "r5.medium",  "state": "running",  "region": "eu-west-1", "cpu": 61},
]

# Running instances only
running = [i for i in instances if i["state"] == "running"]
print(f"Running: {len(running)}/{len(instances)}")

# Group by region
from collections import defaultdict
by_region = defaultdict(list)
for inst in instances:
    by_region[inst["region"]].append(inst["name"])

for region, names in by_region.items():
    print(f"  {region}: {', '.join(names)}")

# High CPU instances (above 80%)
high_cpu = sorted(
    [i for i in running if i["cpu"] > 80],
    key=lambda i: i["cpu"],
    reverse=True
)
if high_cpu:
    print("\nHigh CPU:")
    for i in high_cpu:
        print(f"  {i['name']}: {i['cpu']}%")
```
