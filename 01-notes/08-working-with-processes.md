# 08 — Working with Processes

> subprocess is the bridge between Python and the shell.
> It lets you run any command from Python, capture its output,
> check if it succeeded, and react accordingly.

---

## subprocess.run — The Main Tool

```python
import subprocess

# Run a command
result = subprocess.run(["ls", "-la", "/tmp"])
# Output goes to terminal directly. result.returncode = 0 or non-zero.

# Capture output instead of printing it
result = subprocess.run(
    ["df", "-h", "/"],
    capture_output=True,    # capture stdout and stderr
    text=True               # decode bytes to string (use this always)
)
print(result.stdout)        # the command's output
print(result.stderr)        # any error output
print(result.returncode)    # 0 = success

# Check if it succeeded
if result.returncode == 0:
    print("Command succeeded")
else:
    print(f"Command failed: {result.stderr}")
```

---

## Running Shell Commands Safely

```python
# ALWAYS pass commands as a list, not a string
# This prevents shell injection attacks

# Safe
subprocess.run(["systemctl", "restart", "nginx"])

# Unsafe — avoid (unless you need shell features like pipes)
subprocess.run("systemctl restart nginx", shell=True)

# When you DO need shell=True (pipes, redirects, globs)
result = subprocess.run(
    "ps aux | grep python | grep -v grep",
    shell=True,
    capture_output=True,
    text=True
)
```

---

## Check=True — Fail Loudly

```python
# Without check=True — silent failures
result = subprocess.run(["systemctl", "start", "nonexistent-service"],
                        capture_output=True, text=True)
# returncode is non-zero but no exception raised — easy to miss

# With check=True — raises CalledProcessError on failure
try:
    subprocess.run(
        ["systemctl", "start", "nginx"],
        check=True,
        capture_output=True,
        text=True
    )
    print("nginx started")
except subprocess.CalledProcessError as e:
    print(f"Failed to start nginx: {e.stderr}")
```

---

## Capturing and Processing Output

```python
import subprocess

def get_disk_usage():
    """Return dict of filesystem → usage percent."""
    result = subprocess.run(
        ["df", "-h"],
        capture_output=True,
        text=True,
        check=True
    )
    usage = {}
    for line in result.stdout.splitlines()[1:]:     # skip header
        parts = line.split()
        if len(parts) >= 6:
            filesystem = parts[0]
            percent = int(parts[4].rstrip("%"))
            mount = parts[5]
            usage[mount] = {"filesystem": filesystem, "usage": percent}
    return usage

disks = get_disk_usage()
for mount, info in disks.items():
    if info["usage"] > 80:
        print(f"WARNING: {mount} is {info['usage']}% full")
```

---

## Running Commands with Timeout

```python
import subprocess

try:
    result = subprocess.run(
        ["ping", "-c", "3", "google.com"],
        capture_output=True,
        text=True,
        timeout=10          # kill command if it takes more than 10 seconds
    )
    print(result.stdout)
except subprocess.TimeoutExpired:
    print("Command timed out")
```

---

## subprocess.Popen — For More Control

```python
import subprocess

# Run a long command and stream output line by line
process = subprocess.Popen(
    ["tail", "-f", "/var/log/syslog"],
    stdout=subprocess.PIPE,
    text=True
)

try:
    for line in process.stdout:
        print(line.strip())
        if "ERROR" in line:
            print("Found an error!")
            break
finally:
    process.terminate()
    process.wait()
```

---

## Practical Patterns

```python
import subprocess

def run(cmd, **kwargs):
    """Wrapper that prints the command and handles errors cleanly."""
    print(f"$ {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            **kwargs
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e.stderr.strip()}")
        raise

def service_is_running(name):
    result = subprocess.run(
        ["systemctl", "is-active", name],
        capture_output=True, text=True
    )
    return result.stdout.strip() == "active"

def restart_service(name):
    subprocess.run(["systemctl", "restart", name], check=True)

def get_process_count(name):
    result = subprocess.run(
        ["pgrep", "-c", name],
        capture_output=True, text=True
    )
    return int(result.stdout.strip()) if result.returncode == 0 else 0

# Usage
if not service_is_running("nginx"):
    print("nginx is down, restarting...")
    restart_service("nginx")
    print("nginx restarted")

workers = get_process_count("gunicorn")
print(f"Gunicorn workers: {workers}")
```

---

## os.environ — Environment Variables

```python
import os

# Read
db_host = os.environ["DB_HOST"]            # raises KeyError if missing
db_host = os.environ.get("DB_HOST")        # returns None if missing
db_host = os.environ.get("DB_HOST", "localhost")  # with default

# Set (only for current process and its children)
os.environ["APP_ENV"] = "production"

# Pass custom env to subprocess
env = os.environ.copy()
env["FLASK_ENV"] = "production"
subprocess.run(["python3", "app.py"], env=env)

# All environment variables
for key, value in os.environ.items():
    if "PASSWORD" not in key.upper():       # don't print secrets
        print(f"{key}={value}")
```
