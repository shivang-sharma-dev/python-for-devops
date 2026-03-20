#!/usr/bin/env python3
"""
aws-resource-lister.py

List EC2 instances across one or more AWS regions.
Shows a clean table with instance name, type, state, and IP.

Requirements:
    pip install boto3
    aws configure  (or set AWS_ACCESS_KEY_ID etc. in environment)

Usage:
    python3 aws-resource-lister.py
    python3 aws-resource-lister.py --regions us-east-1 eu-west-1
    python3 aws-resource-lister.py --state running
    python3 aws-resource-lister.py --json
"""

import argparse
import json
import sys

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print("Missing dependency: pip install boto3")
    sys.exit(1)

DEFAULT_REGIONS = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]


def get_tag(tags, key, default="—"):
    """Extract a tag value from an AWS tags list."""
    if not tags:
        return default
    for tag in tags:
        if tag["Key"] == key:
            return tag["Value"]
    return default


def get_instances_in_region(region, state_filter=None):
    """
    Return list of instance dicts for a given region.
    Optionally filter by state (running, stopped, etc.)
    """
    try:
        ec2       = boto3.client("ec2", region_name=region)
        paginator = ec2.get_paginator("describe_instances")

        filters = []
        if state_filter:
            filters.append({
                "Name":   "instance-state-name",
                "Values": [state_filter]
            })

        instances = []
        for page in paginator.paginate(Filters=filters):
            for reservation in page["Reservations"]:
                for inst in reservation["Instances"]:
                    instances.append({
                        "id":         inst["InstanceId"],
                        "name":       get_tag(inst.get("Tags"), "Name"),
                        "type":       inst["InstanceType"],
                        "state":      inst["State"]["Name"],
                        "public_ip":  inst.get("PublicIpAddress", "—"),
                        "private_ip": inst.get("PrivateIpAddress", "—"),
                        "region":     region,
                        "env":        get_tag(inst.get("Tags"), "Environment"),
                        "launched":   str(inst["LaunchTime"])[:10],
                    })
        return instances

    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "AuthFailure":
            print(f"  Auth failed for region {region}", file=sys.stderr)
        elif code == "UnauthorizedOperation":
            print(f"  No permission to list EC2 in {region}", file=sys.stderr)
        else:
            print(f"  AWS error in {region}: {e}", file=sys.stderr)
        return []

    except Exception as e:
        print(f"  Error in {region}: {e}", file=sys.stderr)
        return []


def print_table(instances):
    """Print instances as a formatted table."""
    if not instances:
        print("No instances found.")
        return

    # Column widths
    col = {
        "name":   max(len(i["name"]) for i in instances) + 2,
        "id":     13,
        "type":   12,
        "state":  10,
        "ip":     16,
        "region": 14,
        "env":    12,
    }

    # Header
    print(f"\n{'─' * 90}")
    header = (
        f"{'Name':<{col['name']}} "
        f"{'ID':<{col['id']}} "
        f"{'Type':<{col['type']}} "
        f"{'State':<{col['state']}} "
        f"{'Private IP':<{col['ip']}} "
        f"{'Region':<{col['region']}} "
        f"{'Env'}"
    )
    print(f"  {header}")
    print(f"{'─' * 90}")

    # Sort: region → state → name
    for inst in sorted(instances, key=lambda i: (i["region"], i["state"], i["name"])):
        state = inst["state"]
        row = (
            f"{inst['name']:<{col['name']}} "
            f"{inst['id']:<{col['id']}} "
            f"{inst['type']:<{col['type']}} "
            f"{state:<{col['state']}} "
            f"{inst['private_ip']:<{col['ip']}} "
            f"{inst['region']:<{col['region']}} "
            f"{inst['env']}"
        )
        print(f"  {row}")

    print(f"\n  Total: {len(instances)} instance(s)")

    # State summary
    from collections import Counter
    states = Counter(i["state"] for i in instances)
    state_str = "  " + " | ".join(f"{s}: {c}" for s, c in states.most_common())
    print(state_str)


def main():
    parser = argparse.ArgumentParser(
        description="List EC2 instances across AWS regions"
    )
    parser.add_argument("--regions", nargs="+",
        default=DEFAULT_REGIONS,
        help=f"Regions to check (default: {' '.join(DEFAULT_REGIONS)})")
    parser.add_argument("--state",
        choices=["running", "stopped", "pending", "terminated"],
        help="Filter by instance state")
    parser.add_argument("--json", "as_json", action="store_true",
        help="Output as JSON")
    args = parser.parse_args()

    print(f"Listing EC2 instances in: {', '.join(args.regions)}")
    if args.state:
        print(f"Filter: state={args.state}")

    all_instances = []
    for region in args.regions:
        print(f"  Checking {region}...", end="", flush=True)
        instances = get_instances_in_region(region, args.state)
        print(f" {len(instances)} instance(s)")
        all_instances.extend(instances)

    if args.as_json:
        print(json.dumps(all_instances, indent=2))
    else:
        print_table(all_instances)


if __name__ == "__main__":
    try:
        main()
    except NoCredentialsError:
        print("AWS credentials not found. Run 'aws configure' or set environment variables.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(0)
