# 12 — Cloud SDKs (boto3 / AWS)

> boto3 is the AWS SDK for Python. It lets you manage every AWS resource
> from your scripts — EC2, S3, RDS, Lambda, CloudWatch, everything.
> The patterns here transfer to GCP and Azure SDKs too.

---

## Setup

```bash
pip install boto3

# Configure credentials (one-time setup)
aws configure
# AWS Access Key ID: AKIAIOSFODNN7EXAMPLE
# AWS Secret Access Key: wJalrXUtnFEMI...
# Default region: us-east-1
# Output format: json

# Or set environment variables
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI...
export AWS_DEFAULT_REGION=us-east-1
```

---

## Client vs Resource

boto3 gives you two ways to interact with AWS:

```python
import boto3

# Client — low-level, direct API mapping, returns raw dicts
ec2_client = boto3.client("ec2", region_name="us-east-1")
response = ec2_client.describe_instances()    # returns nested dict

# Resource — higher-level, object-oriented, easier to use
ec2_resource = boto3.resource("ec2", region_name="us-east-1")
instances = list(ec2_resource.instances.all())   # returns Instance objects

# Use client when you need full control
# Use resource when you want cleaner code
```

---

## EC2 — Common Operations

```python
import boto3

ec2 = boto3.resource("ec2", region_name="us-east-1")
client = boto3.client("ec2", region_name="us-east-1")

# List all instances
for instance in ec2.instances.all():
    name = "unknown"
    if instance.tags:
        for tag in instance.tags:
            if tag["Key"] == "Name":
                name = tag["Value"]
    print(f"{instance.id} | {name} | {instance.state['Name']} | {instance.instance_type}")

# Filter instances
running = ec2.instances.filter(
    Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
)

# Filter by tag
web_servers = ec2.instances.filter(
    Filters=[{"Name": "tag:Role", "Values": ["web"]}]
)

# Start/stop instances
instance = ec2.Instance("i-1234567890")
instance.stop()
instance.start()
instance.reboot()

# Get instance public IP
print(instance.public_ip_address)
print(instance.private_ip_address)
```

---

## S3 — Common Operations

```python
import boto3
from pathlib import Path

s3 = boto3.client("s3")
s3_resource = boto3.resource("s3")

# List buckets
response = s3.list_buckets()
for bucket in response["Buckets"]:
    print(bucket["Name"])

# List objects in a bucket
response = s3.list_objects_v2(Bucket="my-bucket", Prefix="backups/")
for obj in response.get("Contents", []):
    print(f"{obj['Key']} — {obj['Size']} bytes")

# Upload a file
s3.upload_file(
    Filename="/tmp/backup.tar.gz",
    Bucket="my-bucket",
    Key="backups/2024-01-15/backup.tar.gz"
)

# Upload with metadata
s3.upload_file(
    Filename="/tmp/report.pdf",
    Bucket="my-bucket",
    Key="reports/report.pdf",
    ExtraArgs={"ContentType": "application/pdf", "ServerSideEncryption": "AES256"}
)

# Download a file
s3.download_file("my-bucket", "backups/backup.tar.gz", "/tmp/backup.tar.gz")

# Delete an object
s3.delete_object(Bucket="my-bucket", Key="old-file.txt")

# Generate a pre-signed URL (temporary access link)
url = s3.generate_presigned_url(
    "get_object",
    Params={"Bucket": "my-bucket", "Key": "private-report.pdf"},
    ExpiresIn=3600      # 1 hour
)
print(url)              # share this URL — expires in 1 hour
```

---

## CloudWatch — Metrics and Logs

```python
import boto3
from datetime import datetime, timedelta

cw = boto3.client("cloudwatch", region_name="us-east-1")
logs = boto3.client("logs", region_name="us-east-1")

# Get EC2 CPU usage for last hour
response = cw.get_metric_statistics(
    Namespace="AWS/EC2",
    MetricName="CPUUtilization",
    Dimensions=[{"Name": "InstanceId", "Value": "i-1234567890"}],
    StartTime=datetime.utcnow() - timedelta(hours=1),
    EndTime=datetime.utcnow(),
    Period=300,         # 5-minute intervals
    Statistics=["Average"]
)

for point in sorted(response["Datapoints"], key=lambda x: x["Timestamp"]):
    print(f"{point['Timestamp']}: {point['Average']:.1f}%")

# Put a custom metric
cw.put_metric_data(
    Namespace="MyApp/Performance",
    MetricData=[{
        "MetricName": "DeploymentDuration",
        "Value": 45.3,
        "Unit": "Seconds",
        "Dimensions": [{"Name": "Environment", "Value": "production"}]
    }]
)

# Read CloudWatch logs
response = logs.get_log_events(
    logGroupName="/aws/lambda/my-function",
    logStreamName="2024/01/15/[$LATEST]abc123",
    startTime=int((datetime.utcnow() - timedelta(hours=1)).timestamp() * 1000)
)
for event in response["events"]:
    print(event["message"])
```

---

## Handling Pagination

AWS API responses are paginated — they only return a limited number
of results per call. Always paginate for production code.

```python
import boto3

ec2 = boto3.client("ec2")

# Manual pagination (fragile — easy to miss pages)
response = ec2.describe_instances()
instances = response["Reservations"]
while "NextToken" in response:
    response = ec2.describe_instances(NextToken=response["NextToken"])
    instances.extend(response["Reservations"])

# Paginator (the right way — handles pagination for you)
paginator = ec2.get_paginator("describe_instances")
for page in paginator.paginate():
    for reservation in page["Reservations"]:
        for instance in reservation["Instances"]:
            print(instance["InstanceId"])

# S3 paginator
s3 = boto3.client("s3")
paginator = s3.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket="my-bucket", Prefix="logs/"):
    for obj in page.get("Contents", []):
        print(obj["Key"])
```

---

## Error Handling with AWS

```python
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def get_instance_info(instance_id):
    ec2 = boto3.client("ec2")
    try:
        response = ec2.describe_instances(InstanceIds=[instance_id])
        instance = response["Reservations"][0]["Instances"][0]
        return instance
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "InvalidInstanceID.NotFound":
            print(f"Instance {instance_id} not found")
        elif error_code == "UnauthorizedOperation":
            print("You don't have permission to describe instances")
        else:
            print(f"AWS error: {e}")
        return None
    except NoCredentialsError:
        print("AWS credentials not configured")
        return None
    except IndexError:
        print(f"Instance {instance_id} not found")
        return None
```

---

## Practical Example — EC2 Instance Report

```python
#!/usr/bin/env python3
"""
Generate a report of all EC2 instances across regions.
"""

import boto3
from collections import defaultdict

REGIONS = ["us-east-1", "us-west-2", "eu-west-1"]

def get_tag(instance, key, default="unknown"):
    if instance.get("Tags"):
        for tag in instance["Tags"]:
            if tag["Key"] == key:
                return tag["Value"]
    return default

def get_instances_in_region(region):
    ec2 = boto3.client("ec2", region_name=region)
    paginator = ec2.get_paginator("describe_instances")
    instances = []
    for page in paginator.paginate():
        for res in page["Reservations"]:
            for inst in res["Instances"]:
                instances.append({
                    "id":     inst["InstanceId"],
                    "name":   get_tag(inst, "Name"),
                    "type":   inst["InstanceType"],
                    "state":  inst["State"]["Name"],
                    "region": region,
                })
    return instances

all_instances = []
for region in REGIONS:
    print(f"Checking {region}...")
    all_instances.extend(get_instances_in_region(region))

# Summary
by_state = defaultdict(list)
for inst in all_instances:
    by_state[inst["state"]].append(inst["name"])

print(f"\nTotal instances: {len(all_instances)}")
for state, names in by_state.items():
    print(f"  {state}: {len(names)}")

# Running instances
running = [i for i in all_instances if i["state"] == "running"]
print(f"\nRunning instances:")
for inst in sorted(running, key=lambda i: i["name"]):
    print(f"  {inst['name']:<20} {inst['type']:<12} {inst['region']}")
