#!/usr/bin/env python3
"""
log-parser.py

Parse nginx access logs and show a summary:
  - Status code breakdown
  - Top requested paths
  - Top client IPs
  - Error requests

Usage:
    python3 log-parser.py /var/log/nginx/access.log
    python3 log-parser.py /var/log/nginx/access.log --top 20
    python3 log-parser.py /var/log/nginx/access.log --errors-only
    cat access.log | python3 log-parser.py -
"""

import argparse
import re
import sys
from collections import Counter, defaultdict


# Nginx default log format:
# 127.0.0.1 - - [15/Jan/2024:10:30:00 +0000] "GET /api/health HTTP/1.1" 200 45 "-" "curl/7.68.0"
LOG_PATTERN = re.compile(
    r'(?P<ip>\S+)'           # client IP
    r' \S+ \S+'              # ident and auth (usually - -)
    r' \[(?P<time>[^\]]+)\]' # timestamp
    r' "(?P<method>\S+)'     # HTTP method
    r' (?P<path>\S+)'        # request path
    r' \S+"'                 # HTTP version
    r' (?P<status>\d{3})'    # status code
    r' (?P<size>\d+|-)'      # response size
)


def parse_line(line):
    """Parse a single nginx log line. Returns dict or None."""
    match = LOG_PATTERN.match(line)
    if not match:
        return None
    data = match.groupdict()
    data["size"] = int(data["size"]) if data["size"] != "-" else 0
    # Strip query string from path for cleaner grouping
    data["path"] = data["path"].split("?")[0]
    return data


def parse_log(source, errors_only=False):
    """Parse all lines from source (file or stdin). Return list of dicts."""
    requests = []
    skipped = 0

    for line in source:
        line = line.strip()
        if not line:
            continue
        parsed = parse_line(line)
        if parsed is None:
            skipped += 1
            continue
        if errors_only and not parsed["status"].startswith(("4", "5")):
            continue
        requests.append(parsed)

    if skipped:
        print(f"  (skipped {skipped} lines that didn't match log format)", file=sys.stderr)

    return requests


def print_section(title, items, top_n):
    """Print a ranked section of results."""
    print(f"\n{'─' * 50}")
    print(f" {title}")
    print(f"{'─' * 50}")
    for i, (key, count) in enumerate(items[:top_n], 1):
        bar = "█" * min(30, int(count / max(c for _, c in items) * 30))
        print(f"  {i:>3}. {str(key):<35} {count:>6}  {bar}")


def summarise(requests, top_n):
    """Print a full summary of parsed log data."""
    total = len(requests)
    if total == 0:
        print("No requests found.")
        return

    print(f"\n{'═' * 50}")
    print(f"  Log Summary — {total:,} requests")
    print(f"{'═' * 50}")

    # Status codes
    status_counts = Counter(r["status"] for r in requests)
    print_section("Status Codes", status_counts.most_common(), top_n)

    # Group 4xx and 5xx
    errors_4xx = sum(c for s, c in status_counts.items() if s.startswith("4"))
    errors_5xx = sum(c for s, c in status_counts.items() if s.startswith("5"))
    error_rate = round((errors_4xx + errors_5xx) / total * 100, 1)
    print(f"\n  Error rate: {error_rate}% ({errors_4xx} client errors, {errors_5xx} server errors)")

    # Top paths
    path_counts = Counter(r["path"] for r in requests)
    print_section(f"Top {top_n} Paths", path_counts.most_common(top_n), top_n)

    # Top IPs
    ip_counts = Counter(r["ip"] for r in requests)
    print_section(f"Top {top_n} Client IPs", ip_counts.most_common(top_n), top_n)

    # Bandwidth
    total_bytes = sum(r["size"] for r in requests)
    print(f"\n  Total data transferred: {total_bytes / 1024 / 1024:.1f} MB")

    # Error details
    errors = [r for r in requests if r["status"].startswith(("4", "5"))]
    if errors:
        print(f"\n{'─' * 50}")
        print(f" Recent Errors (last 10)")
        print(f"{'─' * 50}")
        for r in errors[-10:]:
            print(f"  [{r['status']}] {r['method']:<6} {r['path']}")


def main():
    parser = argparse.ArgumentParser(
        description="Parse nginx access logs and show a summary",
        epilog="Use '-' as file to read from stdin"
    )
    parser.add_argument(
        "file", nargs="?", default="-",
        help="Log file to parse (default: stdin)"
    )
    parser.add_argument(
        "--top", "-n", type=int, default=10,
        help="Number of top results to show (default: 10)"
    )
    parser.add_argument(
        "--errors-only", action="store_true",
        help="Only show 4xx and 5xx requests"
    )
    args = parser.parse_args()

    if args.file == "-":
        requests = parse_log(sys.stdin, args.errors_only)
    else:
        try:
            with open(args.file) as f:
                requests = parse_log(f, args.errors_only)
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)

    summarise(requests, args.top)


if __name__ == "__main__":
    main()
