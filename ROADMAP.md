# Python for DevOps — Roadmap

> Estimated time: 4–5 weeks at 1–2 hours per day.
> Go at your own pace. The checkpoints tell you when you're ready to move on.

---

## The Big Picture

```
Week 1          Week 2          Week 3          Week 4-5
────────        ────────        ────────        ────────────
Learn the       Apply to        Write           Build
language        DevOps tasks    real scripts    projects

Notes 01-06     Notes 07-10     Notes 11-14     03-scripts/
                                                04-projects/
```

---

## Phase 1 — Learn the Language (Week 1)

These notes cover Python fundamentals. Skip nothing here —
each one is used directly in the DevOps notes that follow.

| Note | Time | Checkpoint |
|---|---|---|
| 01 — Why Python for DevOps | 30 min | You know when to use Python vs bash |
| 02 — Variables and Data Types | 1.5 hr | You can work with strings, numbers, booleans |
| 03 — Control Flow | 1.5 hr | You can write if/else, for loops, while loops |
| 04 — Functions | 1.5 hr | You can write reusable functions with arguments |
| 05 — Data Structures | 2 hr | You can use lists, dicts, sets, tuples confidently |
| 06 — Modules and Packages | 1 hr | You can import stdlib modules and install packages |

**Phase 1 checkpoint — before moving on you should be able to:**
- Write a script that reads a list of servers, filters ones that match a pattern, and prints them sorted
- Write a function that takes a filename and returns the number of lines in it
- Import `os`, `sys`, and `json` without looking them up

---

## Phase 2 — Apply It to DevOps (Week 2)

Now the language meets the job. Every note here solves a
real problem DevOps engineers face.

| Note | Time | Checkpoint |
|---|---|---|
| 07 — File Operations | 1.5 hr | Read configs, write logs, walk directory trees |
| 08 — Working with Processes | 1.5 hr | Run shell commands from Python, capture output |
| 09 — Networking and APIs | 2 hr | Make HTTP requests, handle responses, call REST APIs |
| 10 — Parsing Formats | 1.5 hr | Parse JSON, YAML, CSV, INI files |

**Phase 2 checkpoint:**
- Write a script that reads a YAML config file and starts a process based on it
- Write a script that calls a REST API and saves the response to a JSON file
- Run `df -h` from Python and parse the output

---

## Phase 3 — Write Production-Grade Code (Week 3)

The difference between a script that works once and one that
runs reliably in production every day.

| Note | Time | Checkpoint |
|---|---|---|
| 11 — Automation Scripting | 2 hr | Write idempotent, retry-able automation scripts |
| 12 — Cloud SDKs | 2 hr | List EC2 instances, manage S3 files with boto3 |
| 13 — Error Handling and Logging | 1.5 hr | Scripts that don't silently fail |
| 14 — Writing CLI Tools | 1.5 hr | Build a proper CLI tool with arguments and help text |

**Phase 3 checkpoint:**
- Write a script that lists all running EC2 instances in a region
- Write a script that retries a failing operation up to 3 times with backoff
- Your scripts log to a file AND to the console at the same time

---

## Phase 4 — Build Real Things (Week 4–5)

Run the scripts in `03-scripts/`, understand every line,
then modify them. Then pick a project from `04-projects/`.

```
03-scripts/  →  read, run, modify, break, fix
04-projects/ →  build something from scratch
```

---

## Topic Dependency Map

```
why-python
    │
    ├──► variables-and-data-types
    │           │
    │           ├──► control-flow
    │           │         │
    │           │         └──► functions ──► automation-scripting
    │           │                   │
    │           └──► data-structures┘
    │                       │
    │                       └──► parsing-formats
    │
    ├──► modules-and-packages ──► cloud-sdks
    │
    ├──► file-operations ──► automation-scripting
    │
    ├──► working-with-processes ──► automation-scripting
    │
    ├──► networking-and-apis ──► cloud-sdks
    │
    └──► error-handling-and-logging ──► writing-cli-tools
```

---

## Python vs Bash — When to Use Which

A question you will ask yourself constantly. Here's the answer:

```
Use BASH when:                      Use PYTHON when:
──────────────                      ────────────────
Gluing commands together            Logic gets complex (if/else chains)
< 20 lines                          > 20 lines
One-off quick task                  Will be run regularly
No external data needed             Parsing JSON/YAML/CSV
Simple file operations              Error handling matters
Already in a shell script           Talking to APIs or cloud SDKs
                                    Needs to be tested
                                    Shared with the team
```
