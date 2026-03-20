#!/usr/bin/env python3
"""
health-checker.py

Check HTTP health endpoints for a list of services.
Prints a clean summary and exits 1 if any service is unhealthy.

Usage:
    python3 health-checker.py
    python3 health-checker.py --config services.yaml
    python3 health-checker.py --timeout 5 --retries 2

Config file (services.yaml):
    services:
      - name: API
        url: https://api.myapp.com/health
      - name: Admin
        url: https://admin.myapp.com/health
        expected_status: 200
        expected_text: "healthy"
"""

import argparse
import os
import sys
import time
import yaml

try:
    import requests
except ImportError:
    print("Missing dependency: pip install requests pyyaml")
    sys.exit(1)

# ── Default services (used if no config file provided) ────────────────────────
DEFAULT_SERVICES = [
    {"name": "Google",     "url": "https://www.google.com"},
    {"name": "GitHub API", "url": "https://api.github.com"},
    {"name": "Cloudflare", "url": "https://1.1.1.1"},
]


# ── Core ──────────────────────────────────────────────────────────────────────
def check_service(service, timeout, retries):
    """
    Check a single service. Retries on failure.
    Returns dict with: name, url, healthy, status_code, latency, error
    """
    url             = service["url"]
    name            = service["name"]
    expected_status = service.get("expected_status", 200)
    expected_text   = service.get("expected_text")

    last_error = None

    for attempt in range(retries):
        try:
            start    = time.time()
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            latency  = time.time() - start

            # Check status code
            if response.status_code != expected_status:
                last_error = f"Expected {expected_status}, got {response.status_code}"
                time.sleep(1)
                continue

            # Check response body if configured
            if expected_text and expected_text not in response.text:
                last_error = f"Response body missing '{expected_text}'"
                time.sleep(1)
                continue

            return {
                "name":        name,
                "url":         url,
                "healthy":     True,
                "status_code": response.status_code,
                "latency":     latency,
                "error":       None,
            }

        except requests.exceptions.Timeout:
            last_error = f"Timed out after {timeout}s"
        except requests.exceptions.ConnectionError:
            last_error = "Connection refused"
        except Exception as e:
            last_error = str(e)

        if attempt < retries - 1:
            time.sleep(2)

    return {
        "name":        name,
        "url":         url,
        "healthy":     False,
        "status_code": None,
        "latency":     None,
        "error":       last_error,
    }


def load_config(path):
    """Load services from a YAML config file."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return data.get("services", [])


def print_results(results):
    """Print a clean summary table."""
    print(f"\n{'Service':<20} {'Status':<10} {'Latency':<12} {'Details'}")
    print("─" * 65)

    for r in results:
        if r["healthy"]:
            status  = "✓  OK"
            latency = f"{r['latency'] * 1000:.0f}ms"
            details = f"HTTP {r['status_code']}"
        else:
            status  = "✗  FAIL"
            latency = "—"
            details = r["error"] or "Unknown error"

        print(f"{r['name']:<20} {status:<10} {latency:<12} {details}")

    print()
    healthy = sum(1 for r in results if r["healthy"])
    total   = len(results)
    print(f"Result: {healthy}/{total} services healthy")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Check HTTP health endpoints"
    )
    parser.add_argument("--config", "-c",
        help="YAML config file with services list")
    parser.add_argument("--timeout", type=float, default=10,
        help="Request timeout in seconds (default: 10)")
    parser.add_argument("--retries", type=int, default=2,
        help="Number of retries per service (default: 2)")
    args = parser.parse_args()

    if args.config:
        try:
            services = load_config(args.config)
        except FileNotFoundError:
            print(f"Config file not found: {args.config}")
            sys.exit(1)
        except Exception as e:
            print(f"Failed to parse config: {e}")
            sys.exit(1)
    else:
        services = DEFAULT_SERVICES
        print("No config file specified — using default services")

    print(f"Checking {len(services)} service(s) "
          f"(timeout: {args.timeout}s, retries: {args.retries})")

    results = []
    for service in services:
        result = check_service(service, args.timeout, args.retries)
        results.append(result)

    print_results(results)

    failed = [r for r in results if not r["healthy"]]
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
