# Python for DevOps — Interview Q&A

> These are the questions that actually come up in DevOps interviews.
> Not "what is a decorator" — but "how would you write a retry function"
> or "what's the difference between subprocess.run and Popen".

---

## Python Fundamentals

**Q: What is the difference between a list and a tuple?**

A list is mutable — you can add, remove, or change items.
A tuple is immutable — once created it cannot change.
Use tuples for data that should stay fixed (coordinates, RGB values,
function return values). Use lists when you need to modify the collection.

```python
servers = ["web-01", "web-02"]   # list — can append/remove
coords  = (40.71, -74.00)        # tuple — fixed, shouldn't change
```

---

**Q: When would you use a set instead of a list?**

Two cases: when you need unique items, or when you need fast membership testing.

```python
# Deduplication
unique_ips = set(all_ips_from_logs)

# Membership testing — O(1) for set, O(n) for list
blocked = {"1.2.3.4", "5.6.7.8"}
if request_ip in blocked:   # instant lookup regardless of set size
    reject()
```

---

**Q: What is a list comprehension? When would you use one?**

A concise way to build a list by filtering or transforming another iterable.
Use it when the logic fits in one readable line. If it needs a comment to
understand, write a regular for loop instead.

```python
# Get names of running instances
running_names = [i["name"] for i in instances if i["state"] == "running"]

# If the logic is complex, a loop is clearer
running_names = []
for instance in instances:
    if instance["state"] == "running" and instance["region"] == "us-east-1":
        name = get_tag(instance, "Name", default=instance["id"])
        running_names.append(name)
```

---

**Q: What does `if __name__ == "__main__"` do?**

It checks whether the script is being run directly or imported as a module.

When you run `python3 script.py`, Python sets `__name__` to `"__main__"`.
When another script imports it, `__name__` is set to the module name.

The pattern lets a file work as both a runnable script and an importable library.

```python
def check_disk():
    ...

def main():
    check_disk()

if __name__ == "__main__":
    main()    # only runs when executed directly, not when imported
```

---

## subprocess

**Q: What is the difference between `subprocess.run` and `subprocess.Popen`?**

`subprocess.run` waits for the command to finish, then returns.
Use it for most tasks — simple, clean, blocking.

`subprocess.Popen` starts the process and returns immediately.
Use it when you need to stream output in real time, interact with
the process while it runs, or run multiple processes in parallel.

```python
# subprocess.run — wait for completion
result = subprocess.run(["df", "-h"], capture_output=True, text=True)
print(result.stdout)   # available after command finishes

# Popen — stream output line by line
process = subprocess.Popen(["tail", "-f", "/var/log/syslog"],
                           stdout=subprocess.PIPE, text=True)
for line in process.stdout:
    print(line.strip())   # each line as it arrives
```

---

**Q: Why should you pass commands as a list, not a string?**

Passing a string with `shell=True` opens you to shell injection — if any
part of the command comes from user input, an attacker can inject arbitrary
commands. Using a list bypasses the shell entirely, so each element is
treated as a literal argument.

```python
# Dangerous — user_input could be "; rm -rf /"
subprocess.run(f"ls {user_input}", shell=True)

# Safe — user_input is passed as a literal argument
subprocess.run(["ls", user_input])
```

---

**Q: What does `check=True` do in subprocess.run?**

It raises `subprocess.CalledProcessError` if the command exits with a
non-zero return code. Without it, a failed command silently continues
the script — which is almost never what you want in automation.

```python
# Without check=True — silent failure
result = subprocess.run(["systemctl", "start", "badservice"])
# returncode is 1 but no exception raised

# With check=True — loud failure
subprocess.run(["systemctl", "start", "badservice"], check=True)
# raises CalledProcessError immediately
```

---

## Error Handling

**Q: How would you write a retry function with exponential backoff?**

```python
import time

def with_retry(func, max_retries=3, initial_delay=1, backoff=2):
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise   # re-raise on final attempt
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s")
            time.sleep(delay)
            delay *= backoff   # 1s, 2s, 4s, 8s...

# Usage
data = with_retry(lambda: requests.get(url, timeout=5).json())
```

---

**Q: What is the difference between `except Exception` and a bare `except`?**

`except Exception` catches most exceptions but not system exits (`SystemExit`,
`KeyboardInterrupt`, `GeneratorExit`). This is usually what you want.

A bare `except:` catches everything including `KeyboardInterrupt` (Ctrl+C),
which means the user can't stop your script cleanly. Almost always wrong.

```python
try:
    risky_operation()
except Exception as e:     # catches RuntimeError, ValueError, etc. — but not Ctrl+C
    log.error(f"Failed: {e}")
```

---

## APIs and Networking

**Q: How do you make an authenticated API request with requests?**

```python
import requests

# Bearer token (most REST APIs)
headers = {"Authorization": "Bearer your_token_here"}
response = requests.get("https://api.example.com/data", headers=headers)

# Basic auth
response = requests.get(url, auth=("username", "password"))

# API key in query string
response = requests.get(url, params={"api_key": "your_key"})

# Reuse auth across multiple requests with a Session
session = requests.Session()
session.headers["Authorization"] = "Bearer your_token"
r1 = session.get("/users")
r2 = session.get("/servers")
```

---

**Q: How do you handle rate limiting from an API?**

Check for HTTP 429 (Too Many Requests), read the `Retry-After` header,
and sleep before retrying.

```python
import time, requests

def get_with_rate_limit(url, **kwargs):
    for _ in range(5):
        response = requests.get(url, **kwargs)
        if response.status_code == 429:
            wait = int(response.headers.get("Retry-After", 5))
            print(f"Rate limited. Waiting {wait}s...")
            time.sleep(wait)
            continue
        response.raise_for_status()
        return response
    raise RuntimeError("Too many retries")
```

---

## File and Data Handling

**Q: How do you safely read a config file that might not exist?**

```python
import json
from pathlib import Path

def load_config(path, defaults=None):
    config_path = Path(path)
    if not config_path.exists():
        return defaults or {}
    try:
        return json.loads(config_path.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}") from e
```

---

**Q: How do you process a very large log file without running out of memory?**

Read it line by line instead of loading it all at once with `read()`.

```python
# Bad — loads entire file into memory
with open("huge.log") as f:
    lines = f.readlines()   # 10GB file = 10GB of RAM

# Good — processes one line at a time, constant memory usage
with open("huge.log") as f:
    for line in f:          # file object is an iterator
        process(line.strip())

# Or use a generator
def error_lines(filepath):
    with open(filepath) as f:
        for line in f:
            if "ERROR" in line:
                yield line.strip()

for error in error_lines("/var/log/app.log"):
    print(error)
```

---

## AWS / Cloud

**Q: How do you list all EC2 instances in a region with boto3?**

```python
import boto3

ec2 = boto3.client("ec2", region_name="us-east-1")
paginator = ec2.get_paginator("describe_instances")

for page in paginator.paginate():
    for reservation in page["Reservations"]:
        for instance in reservation["Instances"]:
            print(instance["InstanceId"], instance["State"]["Name"])
```

Note the paginator — without it you only get the first page of results
(typically 100 instances). Always paginate in production.

---

**Q: How do you handle AWS errors properly?**

```python
from botocore.exceptions import ClientError

try:
    s3.head_object(Bucket="my-bucket", Key="file.txt")
except ClientError as e:
    code = e.response["Error"]["Code"]
    if code == "404":
        print("File does not exist")
    elif code == "403":
        print("Access denied")
    else:
        raise   # re-raise unexpected errors
```

---

## CLI Tools

**Q: How do you make a Python script accept command-line arguments?**

```python
import argparse

parser = argparse.ArgumentParser(description="Check disk usage")
parser.add_argument("path", help="Path to check")
parser.add_argument("--threshold", type=int, default=90)
parser.add_argument("--json", action="store_true")
args = parser.parse_args()

print(args.path)        # positional argument
print(args.threshold)   # 90 or user-provided int
print(args.json)        # True or False
```

---

**Q: What is the difference between argparse and click?**

Both parse command-line arguments. `argparse` is in the standard library
(no install needed) and is good for simple scripts. `click` is a third-party
library that uses decorators and is much cleaner for complex CLIs with
multiple subcommands, automatic help generation, and rich types.

For a script with one or two flags: `argparse`.
For a tool with multiple commands like `git commit`, `git push`: `click`.
