# 01 — Why Python for DevOps

---

## The Honest Answer

You could do most DevOps work with bash alone. People did it for
decades. But at some point bash becomes painful — the syntax gets
weird, error handling is a mess, and you spend more time debugging
the script than doing the actual work.

Python hits the right balance. It reads like English, handles
complexity gracefully, has libraries for everything, and is the
language most cloud providers (AWS, GCP, Azure) use for their
official SDKs.

It is also the most commonly asked-about scripting language in
DevOps interviews.

---

## What You Actually Use Python For in DevOps

Not theory. Real things that real engineers write:

```python
# 1. Reading a config file and doing something with it
import yaml
with open("config.yml") as f:
    config = yaml.safe_load(f)
print(f"Deploying to {config['environment']}")

# 2. Running a shell command and checking if it worked
import subprocess
result = subprocess.run(["systemctl", "status", "nginx"], capture_output=True)
if result.returncode != 0:
    print("nginx is not running!")

# 3. Calling an API to get data
import requests
response = requests.get("https://api.github.com/repos/python/cpython")
print(f"Stars: {response.json()['stargazers_count']}")

# 4. Listing AWS resources
import boto3
ec2 = boto3.client("ec2", region_name="us-east-1")
instances = ec2.describe_instances()
for r in instances["Reservations"]:
    for i in r["Instances"]:
        print(i["InstanceId"], i["State"]["Name"])

# 5. Parsing a log file for errors
with open("/var/log/nginx/error.log") as f:
    errors = [line for line in f if "ERROR" in line]
print(f"Found {len(errors)} errors")
```

All five of those are things you will write within your first
few months as a DevOps engineer.

---

## Python vs Bash — The Real Decision

Both are valuable. Neither replaces the other.

```
BASH is better when:
  You're gluing commands together
  The script is under 20 lines
  You're working directly with files and pipes
  It's a one-off task you'll run once
  You're already inside a shell script

PYTHON is better when:
  You need proper error handling
  You're parsing structured data (JSON, YAML, CSV)
  You're calling REST APIs
  The logic has more than a few conditions
  The script will run in production regularly
  Other people need to read and maintain it
  You're using cloud SDKs (boto3, google-cloud, azure-sdk)
  You need to write tests for it
```

A practical rule: if you find yourself writing `awk` inside
`sed` inside a `for` loop in bash — switch to Python.

---

## Setting Up Python

```bash
# Check what you have
python3 --version       # want 3.8 or newer

# Install on Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Install on RHEL/CentOS
sudo dnf install python3 python3-pip

# Always use virtual environments
# Never install packages globally with pip
python3 -m venv venv
source venv/bin/activate
pip install requests boto3 pyyaml click rich
```

---

## Virtual Environments — Why They Matter

```
WITHOUT virtual environments:
  pip install requests        → installs globally
  pip install requests==2.26  → in another project, different version
  → version conflicts, broken projects, "works on my machine" hell

WITH virtual environments:
  Each project has its own isolated Python and packages.
  Project A uses requests 2.26
  Project B uses requests 2.31
  They never interfere with each other.

# Create one per project, always
python3 -m venv venv
source venv/bin/activate      # activates it
pip install whatever          # installs only in this venv
deactivate                    # when done

# The venv/ folder is never committed to git
echo "venv/" >> .gitignore
```

---

## pip — Installing Packages

```bash
pip install requests                # install
pip install requests==2.31.0        # specific version
pip install -r requirements.txt     # install from file

pip list                            # what's installed
pip freeze > requirements.txt       # save current packages to file
pip uninstall requests              # uninstall
pip show requests                   # info about a package
pip install --upgrade requests      # upgrade
```

### requirements.txt

```
# requirements.txt
requests==2.31.0
boto3==1.34.0
pyyaml==6.0.1
click==8.1.7
rich==13.7.0
```

Commit this file to git. Anyone cloning your repo runs
`pip install -r requirements.txt` and gets the exact same setup.

---

## Running Python Scripts

```bash
python3 script.py                   # run a script
python3 script.py arg1 arg2         # with arguments
python3 -c "print('hello')"         # one-liner
python3 -m module_name              # run a module

# Make a script executable
chmod +x script.py
./script.py                         # first line must be: #!/usr/bin/env python3

# Interactive Python (for testing ideas quickly)
python3
>>> 2 + 2
4
>>> exit()

# Even better interactive shell
pip install ipython
ipython
```

---

## The Standard Library — Free Tools You Already Have

Python ships with hundreds of useful modules. These are the ones
DevOps engineers use most:

```python
import os           # interact with the operating system
import sys          # system-specific stuff (argv, exit, path)
import subprocess   # run shell commands
import shutil       # high-level file operations
import pathlib      # modern file path handling
import json         # parse and write JSON
import csv          # parse and write CSV
import configparser # parse .ini config files
import logging      # proper logging
import argparse     # parse command-line arguments
import re           # regular expressions
import time         # sleep, timing
import datetime     # dates and times
import socket       # networking
import hashlib      # hashing (md5, sha256)
import gzip         # read/write gzip files
import tarfile      # read/write tar archives
import tempfile     # create temp files safely
import threading    # concurrent operations
import collections  # Counter, defaultdict, namedtuple
```

No installation needed. Just import and use.
