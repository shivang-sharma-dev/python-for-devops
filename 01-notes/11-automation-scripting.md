# 11 — Automation Scripting

> A script that works once is a prototype.
> A script that works reliably every day in production is automation.
> This note covers the patterns that make the difference.

---

## Idempotency — The Most Important Principle

An idempotent script produces the same result whether you run it
once or ten times. This matters in automation because scripts get
re-run — by mistake, by retry logic, by schedulers.

```python
# NOT idempotent — creates duplicate entries every time
def add_server_to_inventory(server_name):
    with open("inventory.txt", "a") as f:
        f.write(f"{server_name}\n")  # always appends, even if already there

# Idempotent — checks first
def add_server_to_inventory(server_name):
    try:
        with open("inventory.txt") as f:
            existing = [line.strip() for line in f]
    except FileNotFoundError:
        existing = []

    if server_name not in existing:
        with open("inventory.txt", "a") as f:
            f.write(f"{server_name}\n")
        print(f"Added {server_name}")
    else:
        print(f"{server_name} already in inventory")
```

---

## Retry Logic

Networks fail. APIs rate-limit. Servers restart. Good automation
handles transient failures without human intervention.

```python
import time
import requests

def with_retry(func, max_retries=3, delay=5, backoff=2):
    """
    Call func and retry on failure.
    delay doubles after each retry (exponential backoff).
    """
    attempt = 0
    wait = delay

    while attempt < max_retries:
        try:
            return func()
        except Exception as e:
            attempt += 1
            if attempt == max_retries:
                raise   # re-raise after final attempt
            print(f"Attempt {attempt} failed: {e}. Retrying in {wait}s...")
            time.sleep(wait)
            wait *= backoff

# Usage
def fetch_metrics():
    response = requests.get("https://metrics.example.com/api", timeout=5)
    response.raise_for_status()
    return response.json()

data = with_retry(fetch_metrics, max_retries=3, delay=5)
```

---

## Locking — Prevent Concurrent Runs

If two instances of your script run at the same time, bad things
can happen. A lock file prevents this.

```python
import sys
import os
import fcntl

LOCK_FILE = "/tmp/myapp-backup.lock"

def acquire_lock():
    """Return lock file handle or exit if already running."""
    try:
        lock = open(LOCK_FILE, "w")
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock.write(str(os.getpid()))
        lock.flush()
        return lock
    except IOError:
        print("Another instance is already running. Exiting.")
        sys.exit(1)

def release_lock(lock):
    fcntl.flock(lock, fcntl.LOCK_UN)
    lock.close()
    os.unlink(LOCK_FILE)

# Usage
lock = acquire_lock()
try:
    run_backup()
finally:
    release_lock(lock)     # always release even if script crashes
```

---

## Scheduling — Running Scripts Periodically

For scripts that run regularly, use cron or systemd timers (see Linux repo).
But sometimes you want the scheduler inside Python itself:

```python
import time
import schedule     # pip install schedule

def check_disk():
    print("Checking disk usage...")

def send_report():
    print("Sending daily report...")

schedule.every(5).minutes.do(check_disk)
schedule.every().day.at("08:00").do(send_report)
schedule.every().monday.at("09:00").do(send_weekly_report)

while True:
    schedule.run_pending()
    time.sleep(1)
```

---

## Dry Run Mode

Always add a `--dry-run` flag to scripts that modify things.
This lets you test what would happen without doing it.

```python
import argparse

def delete_old_files(directory, days, dry_run=False):
    import time
    from pathlib import Path

    cutoff = time.time() - (days * 86400)
    deleted = 0

    for f in Path(directory).rglob("*"):
        if f.is_file() and f.stat().st_mtime < cutoff:
            if dry_run:
                print(f"[DRY RUN] Would delete: {f}")
            else:
                f.unlink()
                print(f"Deleted: {f}")
            deleted += 1

    print(f"\n{'Would delete' if dry_run else 'Deleted'} {deleted} files")

parser = argparse.ArgumentParser()
parser.add_argument("directory")
parser.add_argument("--days", type=int, default=7)
parser.add_argument("--dry-run", action="store_true")
args = parser.parse_args()

delete_old_files(args.directory, args.days, args.dry_run)
```

---

## Config-Driven Scripts

Hard-coding values in scripts is bad. Put everything configurable
in a config file or environment variables.

```python
#!/usr/bin/env python3
"""
Deployment script that reads config from a YAML file.
Run: python3 deploy.py --config deploy.yaml
"""

import yaml
import argparse
import subprocess
import sys

def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)

def deploy(config, environment):
    env_config = config["environments"][environment]
    servers = env_config["servers"]
    app_path = env_config["app_path"]

    print(f"Deploying to {environment} ({len(servers)} servers)")
    for server in servers:
        print(f"  Deploying to {server}...")
        subprocess.run(
            ["rsync", "-avz", "./dist/", f"{server}:{app_path}"],
            check=True
        )
    print("Deployment complete")

parser = argparse.ArgumentParser()
parser.add_argument("--config", default="deploy.yaml")
parser.add_argument("environment", choices=["staging", "production"])
args = parser.parse_args()

config = load_config(args.config)
deploy(config, args.environment)
```

---

## Signal Handling — Graceful Shutdown

When your script is killed (SIGTERM from systemd, Ctrl+C), clean up properly.

```python
import signal
import sys
import time

shutdown_requested = False

def handle_shutdown(signum, frame):
    global shutdown_requested
    print("\nShutdown requested — finishing current task...")
    shutdown_requested = True

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

def do_work():
    print("Processing...")
    time.sleep(2)
    print("Done with task")

while not shutdown_requested:
    do_work()

print("Cleaned up. Goodbye.")
sys.exit(0)
```

---

## Practical Example — Production Backup Script

```python
#!/usr/bin/env python3
"""
Database backup script.
- Idempotent (won't overwrite today's backup if already exists)
- Retries on failure
- Cleans up old backups
- Logs everything
"""

import subprocess
import logging
import sys
import os
import time
from datetime import datetime
from pathlib import Path

BACKUP_DIR = Path("/backups/postgres")
DB_NAME    = os.getenv("DB_NAME", "myapp")
KEEP_DAYS  = 7

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("/var/log/db-backup.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


def backup_filename():
    return BACKUP_DIR / f"{DB_NAME}_{datetime.now():%Y%m%d}.sql.gz"


def run_backup(output_file):
    log.info(f"Starting backup of {DB_NAME} → {output_file}")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    cmd = f"pg_dump {DB_NAME} | gzip > {output_file}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"pg_dump failed: {result.stderr}")

    size_mb = output_file.stat().st_size / 1024 / 1024
    log.info(f"Backup complete: {size_mb:.1f}MB")


def cleanup_old_backups():
    cutoff = time.time() - (KEEP_DAYS * 86400)
    for f in BACKUP_DIR.glob("*.sql.gz"):
        if f.stat().st_mtime < cutoff:
            f.unlink()
            log.info(f"Deleted old backup: {f.name}")


def main():
    output_file = backup_filename()

    if output_file.exists():
        log.info(f"Today's backup already exists: {output_file.name}")
        return

    for attempt in range(1, 4):
        try:
            run_backup(output_file)
            cleanup_old_backups()
            return
        except Exception as e:
            log.warning(f"Attempt {attempt} failed: {e}")
            if attempt < 3:
                time.sleep(30)

    log.error("All backup attempts failed")
    sys.exit(1)


if __name__ == "__main__":
    main()
