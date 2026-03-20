# 13 — Error Handling and Logging

> A script that crashes silently is worse than no script at all.
> Proper error handling and logging are what separate scripts
> that run in production from scripts that run once and get abandoned.

---

## The Problem With Silent Failures

```python
# This script looks fine but fails silently
import requests

def sync_servers():
    response = requests.get("https://api.example.com/servers")
    data = response.json()
    for server in data["servers"]:
        update_inventory(server)

sync_servers()
# If the API is down → requests throws an exception → script crashes
# If the API returns HTML instead of JSON → .json() throws → silent failure
# If "servers" key is missing → KeyError → script crashes
# None of these failures are logged anywhere
```

---

## The logging Module

Stop using `print()` in production scripts. Use `logging` instead.

```python
import logging

# Basic setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

log = logging.getLogger(__name__)

log.debug("Detailed debug info")     # only shows if level=DEBUG
log.info("Script started")           # normal operations
log.warning("Disk usage is high")    # something unexpected but ok
log.error("Failed to connect to DB") # something failed
log.critical("System is down")       # very serious failure
```

---

## Logging to File AND Console

```python
import logging
import sys

def setup_logging(log_file, level=logging.INFO):
    """Set up logging to both file and console."""
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

setup_logging("/var/log/myapp/deploy.log")
log = logging.getLogger(__name__)
log.info("Deployment started")
```

---

## Exception Handling Patterns

```python
import logging
log = logging.getLogger(__name__)

# Catch specific exceptions — always prefer this
try:
    with open("/etc/myapp/config.json") as f:
        config = json.load(f)
except FileNotFoundError:
    log.error("Config file not found at /etc/myapp/config.json")
    sys.exit(1)
except json.JSONDecodeError as e:
    log.error(f"Config file is not valid JSON: {e}")
    sys.exit(1)

# Log the full traceback for unexpected errors
try:
    process_data(data)
except Exception:
    log.exception("Unexpected error processing data")  # logs full traceback
    raise

# Re-raise with more context
try:
    connect_to_database(host, port)
except ConnectionError as e:
    raise ConnectionError(f"Cannot connect to database at {host}:{port}") from e

# Custom exceptions
class DeploymentError(Exception):
    """Raised when a deployment step fails."""
    pass

class ConfigError(Exception):
    """Raised when configuration is invalid."""
    pass

def deploy(config):
    if "servers" not in config:
        raise ConfigError("'servers' key missing from config")
    if not config["servers"]:
        raise ConfigError("No servers defined in config")
```

---

## Exit Codes — Signal Success or Failure

```python
import sys

# Convention:
# 0 = success
# 1 = general error
# 2 = misuse of command
# 3+ = application-specific errors

def main():
    try:
        run_deployment()
        log.info("Deployment successful")
        sys.exit(0)
    except ConfigError as e:
        log.error(f"Configuration error: {e}")
        sys.exit(2)
    except DeploymentError as e:
        log.error(f"Deployment failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        log.info("Deployment cancelled by user")
        sys.exit(1)
```

---

## Practical Example — Production-Grade Script

```python
#!/usr/bin/env python3
"""
health_monitor.py

Monitors service health and sends Slack alerts on failure.
Designed to run every 5 minutes via cron.
"""

import logging
import os
import sys
import requests
from datetime import datetime

# ── Configuration ────────────────────────────────────────────────────────────
SERVICES = [
    {"name": "API",      "url": "https://api.myapp.com/health"},
    {"name": "Admin",    "url": "https://admin.myapp.com/health"},
    {"name": "Worker",   "url": "https://worker.myapp.com/health"},
]
SLACK_WEBHOOK  = os.getenv("SLACK_WEBHOOK_URL")
TIMEOUT        = 10   # seconds
LOG_FILE       = "/var/log/myapp/health-monitor.log"

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger(__name__)


# ── Core logic ────────────────────────────────────────────────────────────────
def check_service(service):
    """Check a service's health endpoint. Return (healthy, latency, error)."""
    try:
        response = requests.get(service["url"], timeout=TIMEOUT)
        latency = response.elapsed.total_seconds()
        if response.status_code == 200:
            return True, latency, None
        return False, latency, f"HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        return False, None, "Timed out"
    except requests.exceptions.ConnectionError:
        return False, None, "Connection refused"
    except Exception as e:
        return False, None, str(e)


def send_alert(failures):
    """Send a Slack alert for failed services."""
    if not SLACK_WEBHOOK:
        log.warning("SLACK_WEBHOOK_URL not set — skipping alert")
        return

    lines = [f"🚨 *Health Check Failures* — {datetime.now():%Y-%m-%d %H:%M}"]
    for name, error in failures:
        lines.append(f"  • *{name}*: {error}")

    try:
        response = requests.post(
            SLACK_WEBHOOK,
            json={"text": "\n".join(lines)},
            timeout=5
        )
        response.raise_for_status()
        log.info("Slack alert sent")
    except Exception as e:
        log.error(f"Failed to send Slack alert: {e}")


def main():
    log.info(f"Starting health check for {len(SERVICES)} services")
    failures = []

    for service in SERVICES:
        healthy, latency, error = check_service(service)
        if healthy:
            log.info(f"  ✓ {service['name']}: OK ({latency:.2f}s)")
        else:
            log.error(f"  ✗ {service['name']}: FAIL — {error}")
            failures.append((service["name"], error))

    if failures:
        send_alert(failures)
        log.error(f"Health check FAILED: {len(failures)}/{len(SERVICES)} services down")
        sys.exit(1)
    else:
        log.info("All services healthy")
        sys.exit(0)


if __name__ == "__main__":
    main()
