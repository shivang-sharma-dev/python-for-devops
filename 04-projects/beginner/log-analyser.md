# Project: Log Analyser

**Level:** Beginner
**Time:** 2–3 hours
**Covers:** Notes 03–06, 10 (control flow, functions, data structures, parsing)

---

## What You're Building

A tool that reads application log files, extracts meaningful
information, and produces a daily summary report.

---

## Final Result

```
$ python3 log-analyser.py /var/log/myapp/ --date 2024-01-15

=== Log Analysis: 2024-01-15 ===

Total lines processed: 48,291
Time range: 00:00:01 → 23:59:58

Log levels:
  INFO    : 45,102 (93.4%)
  WARNING :  2,841  (5.9%)
  ERROR   :    348  (0.7%)

Top 10 errors:
  1. Database connection timeout        (89 occurrences)
  2. Redis key not found               (67 occurrences)
  ...

Errors by hour:
  00:00  ██
  01:00  █
  ...
  14:00  █████████████████  ← peak error hour

Report saved to report_20240115.txt
```

---

## Log Format

Assume this log format:
```
2024-01-15 14:32:01 ERROR [database] Connection timeout after 30s
2024-01-15 14:32:02 INFO  [api] GET /users 200 45ms
2024-01-15 14:32:03 WARN  [cache] Cache miss for key user:42
```

---

## Requirements

**Step 1 — Parse log lines**
Write a function `parse_line(line)` that uses regex to extract:
- date, time, level (INFO/WARN/ERROR), component, message

**Step 2 — Load a day's logs**
- Accept a directory path
- Load all `.log` files in that directory
- Filter lines matching the given `--date` argument

**Step 3 — Analyse the data**
- Count by log level
- Count unique error messages (strip timestamps/IDs)
- Group errors by hour

**Step 4 — Generate the report**
- Print to console
- Save to a text file
- Add ASCII bar charts for the hourly breakdown

**Step 5 — Handle large files**
- Don't load everything into memory at once
- Process line by line using a generator

---

## Stretch Goals

- Support multiple log formats (auto-detect)
- Compare two days' error rates
- Send report by email using `smtplib`
- Export to JSON for use in a dashboard
