# Python for DevOps

> Learn Python from scratch, the way a DevOps engineer actually uses it.
> No fluff. No toy examples. Real scripts you'll write on the job.

---

## Why This Repo Exists

Most Python courses teach you to build web apps or data science models.
That's great — but DevOps engineers use Python differently.

You use Python to:
- Automate repetitive server tasks you're tired of doing by hand
- Parse logs and extract meaningful information from them
- Talk to cloud APIs to manage infrastructure at scale
- Write health checks that run every few minutes in production
- Build CLI tools your whole team actually uses
- Replace 200-line bash scripts with something readable and maintainable

This repo teaches Python with exactly that in mind. Every example is
something you'd actually write at work.

---

## Who This is For

```
Complete beginner to Python?         ✓ Start at note 01
Know basic Python, new to DevOps?    ✓ Start at note 07
Experienced, want a reference?       ✓ Use the cheatsheet
Preparing for interviews?            ✓ Go to 05-interview-prep
```

---

## The Learning Path

```
PHASE 1 — Learn the language
  Variables · Data types · Control flow
  Functions · Data structures · Modules

        ↓

PHASE 2 — Apply it to DevOps
  File operations · Running processes
  Calling APIs · Parsing configs

        ↓

PHASE 3 — Write production-grade code
  Automation · Cloud SDKs
  Error handling · CLI tools

        ↓

PHASE 4 — Build real things
  Scripts you can run today
  Projects for your portfolio
```

---

## Repo Structure

```
python-for-devops/
│
├── 01-notes/          14 files — zero to DevOps Python
├── 02-cheatsheet/     quick reference for everything
├── 03-scripts/        real runnable scripts, not exercises
├── 04-projects/       beginner and intermediate projects
├── 05-interview-prep/ questions DevOps engineers actually get asked
└── 06-resources/      books, courses, tools, YouTube
```

---

## Setup

```bash
# Check Python version (need 3.8+)
python3 --version

# Create a virtual environment (do this for every project)
python3 -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install packages used in this repo
pip install requests boto3 click pyyaml rich

# Deactivate when done
deactivate
```

---

## Progress Tracker

- [ ] 01 Why Python for DevOps
- [ ] 02 Variables and Data Types
- [ ] 03 Control Flow
- [ ] 04 Functions
- [ ] 05 Data Structures
- [ ] 06 Modules and Packages
- [ ] 07 File Operations
- [ ] 08 Working with Processes
- [ ] 09 Networking and APIs
- [ ] 10 Parsing Formats
- [ ] 11 Automation Scripting
- [ ] 12 Cloud SDKs
- [ ] 13 Error Handling and Logging
- [ ] 14 Writing CLI Tools
- [ ] Run all scripts in 03-scripts/
- [ ] Complete at least one project
- [ ] Review interview prep

---

*Part of the [DevOps Mastery](https://github.com/yourusername) learning series.*
