#!/usr/bin/env python3
"""
api-monitor.py

Continuously monitor API endpoints, log response times,
and alert when latency or error rates cross thresholds.

Usage:
    python3 api-monitor.py
    python3 api-monitor.py --interval 30 --alert-latency 2.0

Runs forever until Ctrl+C.
"""

import argparse
import logging
import signal
import sys
import time
from collections import deque
from datetime import datetime

try:
    import requests
except ImportError:
    print("Missing dependency: pip install requests")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────
ENDPOINTS = [
    {"name": "GitHub API",    "url": "https://api.github.com"},
    {"name": "httpbin GET",   "url": "https://httpbin.org/get"},
    {"name": "httpbin delay", "url": "https://httpbin.org/delay/1"},
]

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)

# ── Globals ───────────────────────────────────────────────────────────────────
running = True
# Keep last 10 results per endpoint for rolling stats
history = {e["name"]: deque(maxlen=10) for e in ENDPOINTS}


def handle_shutdown(sig, frame):
    global running
    log.info("Shutting down monitor...")
    running = False


def check_endpoint(endpoint, timeout, alert_latency):
    """Check one endpoint and return result dict."""
    name = endpoint["name"]
    url  = endpoint["url"]

    try:
        start    = time.time()
        response = requests.get(url, timeout=timeout)
        latency  = time.time() - start

        result = {
            "name":    name,
            "ok":      response.status_code < 400,
            "status":  response.status_code,
            "latency": latency,
            "error":   None,
        }

        history[name].append(result)

        # Determine log level based on result
        if not result["ok"]:
            log.error(f"{name}: HTTP {response.status_code} ({latency:.2f}s)")
        elif latency > alert_latency:
            log.warning(f"{name}: SLOW — {latency:.2f}s (threshold: {alert_latency}s)")
        else:
            log.info(f"{name}: OK — {latency:.2f}s")

        return result

    except requests.exceptions.Timeout:
        result = {"name": name, "ok": False, "status": None,
                  "latency": timeout, "error": "timeout"}
        history[name].append(result)
        log.error(f"{name}: TIMEOUT after {timeout}s")
        return result

    except requests.exceptions.ConnectionError:
        result = {"name": name, "ok": False, "status": None,
                  "latency": None, "error": "connection_error"}
        history[name].append(result)
        log.error(f"{name}: CONNECTION ERROR")
        return result


def print_rolling_stats():
    """Print a rolling stats summary for all endpoints."""
    print(f"\n{'─'*60}")
    print(f"  Rolling Stats (last {history[ENDPOINTS[0]['name']].maxlen} checks)")
    print(f"{'─'*60}")
    print(f"  {'Endpoint':<25} {'Success':<10} {'Avg Latency':<15} {'P95 Latency'}")
    print(f"  {'─'*55}")

    for endpoint in ENDPOINTS:
        name    = endpoint["name"]
        results = list(history[name])
        if not results:
            continue

        success_rate = sum(1 for r in results if r["ok"]) / len(results) * 100
        latencies    = [r["latency"] for r in results if r["latency"] is not None]

        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            p95_latency = sorted(latencies)[int(len(latencies) * 0.95) - 1]
            lat_str     = f"{avg_latency:.2f}s"
            p95_str     = f"{p95_latency:.2f}s"
        else:
            lat_str = "—"
            p95_str = "—"

        rate_str = f"{success_rate:.0f}%"
        print(f"  {name:<25} {rate_str:<10} {lat_str:<15} {p95_str}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Monitor API endpoints and log response times"
    )
    parser.add_argument("--interval", type=int, default=10,
        help="Check interval in seconds (default: 10)")
    parser.add_argument("--timeout", type=float, default=10,
        help="Request timeout in seconds (default: 10)")
    parser.add_argument("--alert-latency", type=float, default=2.0,
        help="Alert if latency exceeds this (seconds, default: 2.0)")
    parser.add_argument("--stats-every", type=int, default=5,
        help="Print rolling stats every N checks (default: 5)")
    args = parser.parse_args()

    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    log.info(f"Starting API monitor — {len(ENDPOINTS)} endpoints, "
             f"every {args.interval}s")

    check_count = 0
    while running:
        check_count += 1
        log.info(f"--- Check #{check_count} ---")

        for endpoint in ENDPOINTS:
            if not running:
                break
            check_endpoint(endpoint, args.timeout, args.alert_latency)

        if check_count % args.stats_every == 0:
            print_rolling_stats()

        # Sleep in small increments so Ctrl+C is responsive
        for _ in range(args.interval * 10):
            if not running:
                break
            time.sleep(0.1)

    log.info("Monitor stopped")


if __name__ == "__main__":
    main()
