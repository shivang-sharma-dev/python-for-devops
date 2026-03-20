#!/usr/bin/env python3
"""
disk-usage-alert.py

Check disk usage across multiple paths and alert if any exceed
the threshold. Designed to run via cron every 15 minutes.

Usage:
    python3 disk-usage-alert.py
    python3 disk-usage-alert.py --threshold 95
    python3 disk-usage-alert.py --paths / /data /var

Cron (every 15 minutes):
    */15 * * * * /usr/bin/python3 /opt/scripts/disk-usage-alert.py >> /var/log/disk-alert.log 2>&1
"""

import argparse
import logging
import os
import shutil
import sys
from datetime import datetime

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)


# ── Core functions ────────────────────────────────────────────────────────────
def get_disk_usage(path):
    """
    Return disk usage for a path as a percentage.
    Returns None if the path doesn't exist or can't be read.
    """
    try:
        total, used, free = shutil.disk_usage(path)
        return {
            "path":       path,
            "total_gb":   round(total / 1024**3, 1),
            "used_gb":    round(used  / 1024**3, 1),
            "free_gb":    round(free  / 1024**3, 1),
            "percent":    round(used / total * 100, 1),
        }
    except FileNotFoundError:
        log.warning(f"Path not found: {path}")
        return None
    except PermissionError:
        log.warning(f"Permission denied: {path}")
        return None


def send_slack_alert(webhook_url, message):
    """Send a message to a Slack webhook."""
    try:
        import requests
        response = requests.post(webhook_url, json={"text": message}, timeout=5)
        response.raise_for_status()
        log.info("Slack alert sent")
    except Exception as e:
        log.error(f"Failed to send Slack alert: {e}")


def format_alert_message(alerts):
    """Format disk alerts into a readable message."""
    lines = [f"🚨 Disk Usage Alert — {datetime.now():%Y-%m-%d %H:%M}"]
    for alert in alerts:
        lines.append(
            f"  • {alert['path']}: {alert['percent']}% used "
            f"({alert['used_gb']}GB / {alert['total_gb']}GB)"
        )
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Check disk usage and alert if above threshold"
    )
    parser.add_argument(
        "--paths", nargs="+", default=["/"],
        metavar="PATH",
        help="Paths to check (default: /)"
    )
    parser.add_argument(
        "--threshold", "-t", type=int, default=90,
        metavar="PERCENT",
        help="Alert threshold in percent (default: 90)"
    )
    parser.add_argument(
        "--slack-webhook",
        default=os.getenv("SLACK_WEBHOOK_URL"),
        help="Slack webhook URL (or set SLACK_WEBHOOK_URL env var)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print alerts but don't send notifications"
    )
    args = parser.parse_args()

    log.info(f"Checking disk usage on: {', '.join(args.paths)} (threshold: {args.threshold}%)")

    alerts = []
    for path in args.paths:
        usage = get_disk_usage(path)
        if usage is None:
            continue

        if usage["percent"] > args.threshold:
            log.warning(
                f"ALERT: {path} is {usage['percent']}% full "
                f"({usage['used_gb']}GB used, {usage['free_gb']}GB free)"
            )
            alerts.append(usage)
        else:
            log.info(f"OK: {path} is {usage['percent']}% full")

    if alerts:
        message = format_alert_message(alerts)
        if args.dry_run:
            print("\n[DRY RUN] Would send alert:")
            print(message)
        elif args.slack_webhook:
            send_slack_alert(args.slack_webhook, message)
        else:
            log.warning("No Slack webhook configured — set SLACK_WEBHOOK_URL")

        sys.exit(1)     # non-zero exit so cron/monitoring knows something is wrong
    else:
        log.info("All paths within threshold")
        sys.exit(0)


if __name__ == "__main__":
    main()
