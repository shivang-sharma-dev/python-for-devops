# 09 — Networking and APIs

> REST APIs are everywhere in DevOps — GitHub, Slack, PagerDuty,
> monitoring tools, cloud providers. The requests library is how
> you talk to all of them from Python.

---

## Installing requests

```bash
pip install requests
```

---

## Making HTTP Requests

```python
import requests

# GET request
response = requests.get("https://api.github.com/repos/python/cpython")

print(response.status_code)    # 200
print(response.headers)        # response headers dict
print(response.text)           # response body as string
print(response.json())         # parse JSON response into dict

# Always check if it succeeded
response.raise_for_status()    # raises HTTPError if 4xx or 5xx
```

---

## Common Request Patterns

```python
import requests

# With query parameters
response = requests.get(
    "https://api.github.com/search/repositories",
    params={"q": "devops", "sort": "stars", "per_page": 5}
)
# URL becomes: https://api.github.com/search/repositories?q=devops&sort=stars&per_page=5

# With headers (auth tokens, content type)
headers = {
    "Authorization": "Bearer ghp_yourtoken",
    "Accept": "application/vnd.github.v3+json"
}
response = requests.get("https://api.github.com/user", headers=headers)

# POST with JSON body
response = requests.post(
    "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    json={"text": "Deployment complete! :rocket:"}
)

# POST with form data
response = requests.post(
    "https://api.example.com/login",
    data={"username": "alice", "password": "secret"}
)

# With timeout (always set this in production)
response = requests.get("https://api.example.com", timeout=10)

# With SSL verification disabled (avoid in production)
response = requests.get("https://internal-api.local", verify=False)
```

---

## Using a Session (Reuse Connections)

```python
import requests

# Session reuses the TCP connection — much faster for multiple requests
session = requests.Session()
session.headers.update({
    "Authorization": "Bearer your_token",
    "Content-Type": "application/json"
})

# All requests through session inherit the headers
r1 = session.get("https://api.example.com/users")
r2 = session.get("https://api.example.com/servers")
r3 = session.post("https://api.example.com/deploy", json={"app": "web"})
```

---

## Error Handling for API Calls

```python
import requests
from requests.exceptions import Timeout, ConnectionError, HTTPError

def call_api(url, **kwargs):
    """Make an API call with proper error handling."""
    try:
        response = requests.get(url, timeout=10, **kwargs)
        response.raise_for_status()     # raise on 4xx/5xx
        return response.json()

    except Timeout:
        print(f"Request to {url} timed out")
        return None

    except ConnectionError:
        print(f"Could not connect to {url}")
        return None

    except HTTPError as e:
        print(f"HTTP error {e.response.status_code}: {e.response.text}")
        return None
```

---

## Real-World Examples

### Send a Slack alert

```python
import requests

def send_slack_alert(webhook_url, message, color="danger"):
    payload = {
        "attachments": [
            {
                "color": color,
                "text": message,
                "footer": "DevOps Bot"
            }
        ]
    }
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200

# Usage
SLACK_WEBHOOK = "https://hooks.slack.com/services/..."
send_slack_alert(SLACK_WEBHOOK, "🚨 High CPU on web-01: 95%", color="danger")
send_slack_alert(SLACK_WEBHOOK, "✅ Deployment complete", color="good")
```

### Check a health endpoint

```python
import requests

def check_health(url, expected_status=200):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == expected_status:
            return True, response.elapsed.total_seconds()
        return False, None
    except Exception:
        return False, None

services = [
    "https://api.myapp.com/health",
    "https://admin.myapp.com/health",
    "https://worker.myapp.com/health",
]

for url in services:
    healthy, latency = check_health(url)
    status = f"OK ({latency:.2f}s)" if healthy else "FAIL"
    print(f"{url}: {status}")
```

### Create a GitHub issue automatically

```python
import requests

def create_github_issue(token, owner, repo, title, body):
    response = requests.post(
        f"https://api.github.com/repos/{owner}/{repo}/issues",
        headers={"Authorization": f"token {token}"},
        json={"title": title, "body": body}
    )
    response.raise_for_status()
    issue = response.json()
    print(f"Created issue #{issue['number']}: {issue['html_url']}")
    return issue["number"]

create_github_issue(
    token="ghp_yourtoken",
    owner="myorg",
    repo="infra",
    title="High disk usage on web-01",
    body="Disk usage is at 94%. Needs immediate attention."
)
```

---

## Sockets — Low-Level Networking

```python
import socket

# Get IP of a hostname
ip = socket.gethostbyname("google.com")
print(ip)   # 142.250.80.46

# Check if a port is open
def is_port_open(host, port, timeout=3):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

print(is_port_open("google.com", 443))      # True
print(is_port_open("10.0.1.1", 5432))      # True/False (is postgres reachable?)

# Get your machine's hostname and IP
print(socket.gethostname())
print(socket.gethostbyname(socket.gethostname()))
```
