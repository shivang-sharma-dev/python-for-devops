# 07 — File Operations

> Reading configs, writing logs, finding files, cleaning up old data —
> file operations are in almost every DevOps script you write.

---

## Reading Files

```python
# The right way — context manager closes file automatically
with open("/etc/hostname") as f:
    hostname = f.read().strip()

# Read all lines as a list
with open("/etc/hosts") as f:
    lines = f.readlines()           # includes \n at end of each line

# Better — iterate line by line (memory efficient for large files)
with open("/var/log/nginx/access.log") as f:
    for line in f:
        line = line.strip()         # remove \n
        if "ERROR" in line:
            print(line)

# Read into a list without the newlines
with open("/etc/hosts") as f:
    lines = [line.strip() for line in f if not line.startswith("#")]
```

---

## Writing Files

```python
# Write (creates file or overwrites if exists)
with open("/tmp/report.txt", "w") as f:
    f.write("Server Health Report\n")
    f.write("====================\n")
    f.write(f"Status: OK\n")

# Append (add to existing file)
with open("/var/log/myapp.log", "a") as f:
    f.write(f"2024-01-15 10:30:00 INFO Script started\n")

# Write multiple lines
servers = ["web-01", "web-02", "db-01"]
with open("/tmp/servers.txt", "w") as f:
    f.writelines(f"{s}\n" for s in servers)

# print() to a file — convenient
with open("/tmp/report.txt", "w") as f:
    print("Server Report", file=f)
    print(f"Total servers: {len(servers)}", file=f)
```

---

## Checking Files and Directories

```python
import os
from pathlib import Path

path = Path("/etc/nginx/nginx.conf")

path.exists()           # does it exist?
path.is_file()          # is it a file?
path.is_dir()           # is it a directory?
path.stat().st_size     # file size in bytes
path.stat().st_mtime    # last modified time (unix timestamp)

# File size in human readable form
size = path.stat().st_size
for unit in ["B", "KB", "MB", "GB"]:
    if size < 1024:
        print(f"{size:.1f} {unit}")
        break
    size /= 1024
```

---

## Walking Directories

```python
import os
from pathlib import Path

# os.walk — traverse entire directory tree
for dirpath, dirnames, filenames in os.walk("/var/log"):
    for filename in filenames:
        full_path = os.path.join(dirpath, filename)
        print(full_path)

# pathlib.rglob — find files matching a pattern
for log_file in Path("/var/log").rglob("*.log"):
    print(log_file)

# Find files larger than 100MB
for f in Path("/var/log").rglob("*"):
    if f.is_file() and f.stat().st_size > 100 * 1024 * 1024:
        size_mb = f.stat().st_size / 1024 / 1024
        print(f"{f}: {size_mb:.1f}MB")

# Find files older than 7 days
import time
seven_days_ago = time.time() - (7 * 86400)
for f in Path("/tmp").iterdir():
    if f.is_file() and f.stat().st_mtime < seven_days_ago:
        print(f"Old file: {f}")
        # f.unlink()   # uncomment to actually delete
```

---

## Copying, Moving, Deleting

```python
import shutil
from pathlib import Path

# Copy
shutil.copy("source.txt", "dest.txt")          # copy file
shutil.copy2("source.txt", "dest.txt")         # copy with metadata
shutil.copytree("src_dir/", "dest_dir/")       # copy entire directory

# Move / rename
shutil.move("old_name.txt", "new_name.txt")
shutil.move("/tmp/file.txt", "/backups/")      # move to directory

# Delete
Path("file.txt").unlink()                      # delete file
Path("file.txt").unlink(missing_ok=True)       # don't error if missing
shutil.rmtree("/tmp/old_data/")                # delete directory tree

# Disk usage of a directory
total_size = sum(f.stat().st_size for f in Path("/var/log").rglob("*") if f.is_file())
print(f"Log directory size: {total_size / 1024 / 1024:.1f}MB")
```

---

## Working with Config Files

### Reading a simple key=value config

```python
# /etc/myapp.conf:
# HOST=10.0.1.1
# PORT=8080
# DEBUG=false

config = {}
with open("/etc/myapp.conf") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            key, _, value = line.partition("=")
            config[key.strip()] = value.strip()

print(config["HOST"])   # 10.0.1.1
print(config["PORT"])   # 8080
```

### .env files (load with python-dotenv)

```python
from dotenv import load_dotenv
import os

load_dotenv("/etc/myapp.env")       # loads KEY=VALUE pairs into environment
load_dotenv()                       # loads .env from current directory

db_host = os.getenv("DB_HOST")
db_pass = os.getenv("DB_PASSWORD")
debug   = os.getenv("DEBUG", "false").lower() == "true"
```

---

## Temporary Files

```python
import tempfile

# Create a temp file (auto-deleted when context exits)
with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
    f.write("#!/bin/bash\necho hello\n")
    temp_path = f.name

# Use temp_path here, then clean up manually
import os
os.unlink(temp_path)

# Temp directory
with tempfile.TemporaryDirectory() as tmpdir:
    # tmpdir is a string path like "/tmp/tmpXYZABC"
    # everything in it is deleted when the block exits
    output_file = os.path.join(tmpdir, "output.txt")
    with open(output_file, "w") as f:
        f.write("temporary data")
```

---

## Practical Example — Log Rotation Script

```python
#!/usr/bin/env python3
"""
Rotate log files: compress logs older than 1 day,
delete compressed logs older than 7 days.
"""

import gzip
import shutil
import time
from pathlib import Path
from datetime import datetime

LOG_DIR = Path("/var/log/myapp")
MAX_AGE_DAYS = 7

def compress_file(path):
    """Compress a file with gzip and delete the original."""
    gz_path = path.with_suffix(path.suffix + ".gz")
    with open(path, "rb") as f_in:
        with gzip.open(gz_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    path.unlink()
    print(f"Compressed: {path.name} → {gz_path.name}")

def cleanup_old_files(directory, max_days):
    """Delete files older than max_days."""
    cutoff = time.time() - (max_days * 86400)
    for f in directory.glob("*.gz"):
        if f.stat().st_mtime < cutoff:
            f.unlink()
            print(f"Deleted old file: {f.name}")

def main():
    if not LOG_DIR.exists():
        print(f"Log directory not found: {LOG_DIR}")
        return

    yesterday = time.time() - 86400
    for log_file in LOG_DIR.glob("*.log"):
        if log_file.stat().st_mtime < yesterday:
            compress_file(log_file)

    cleanup_old_files(LOG_DIR, MAX_AGE_DAYS)
    print("Log rotation complete")

if __name__ == "__main__":
    main()
