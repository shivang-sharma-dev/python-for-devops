# Project: Deployment Notifier

**Level:** Intermediate
**Time:** 3–4 hours
**Covers:** Notes 08–11, 13–14 (subprocess, APIs, automation, error handling, CLI)

---

## What You're Building

A CLI tool that wraps a deployment script, monitors its progress,
and sends real-time notifications to Slack with success/failure status,
duration, and a link to the logs.

This is the kind of tool that gets used by an entire engineering team.

---

## Final Result

```
$ deploy notify --env production --app api --slack-channel deploys

🚀 Deployment started
   App:         api
   Environment: production
   Version:     v2.4.1
   By:          alice
   Started:     2024-01-15 14:30:00

[running deployment script...]

✅ Deployment successful
   Duration:  2m 34s
   Logs:      https://logs.mycompany.com/deploy/abc123
```

Slack message sent to #deploys:
```
✅ *api* deployed to *production*
Version: v2.4.1 | Duration: 2m 34s | By: alice
```

---

## Requirements

**Step 1 — Basic structure**
- Create a `click` CLI with a `notify` command
- Accept `--env`, `--app`, `--version` arguments
- Read Slack webhook from environment variable

**Step 2 — Run the deployment**
- Accept a `--command` argument (the deployment command to wrap)
- Run it with `subprocess.Popen` to stream output in real time
- Capture start time, end time, and duration

**Step 3 — Send Slack notifications**
- Send a "started" message at the beginning
- Send a "success" or "failure" message at the end
- Include: app, environment, version, duration, who ran it (`os.getenv("USER")`)
- Update the original message (use Slack message update API) rather than posting a new one

**Step 4 — Error handling**
- If the deployment command fails (non-zero exit), send a failure notification
- Include the last 20 lines of output in the failure message
- Exit with code 1 so CI/CD pipelines know it failed

**Step 5 — Config file**
- Read default settings from `~/.deploy-notifier.yaml`
- Allow per-project config in `.deploy-notifier.yaml` in the project root

---

## Stretch Goals

- Support multiple notification backends (Slack, Teams, Discord)
- Add deployment approval step (wait for a Slack reaction before proceeding)
- Store deployment history in a SQLite database
- Generate a link to a web dashboard showing recent deployments

---

## Key Concepts Practiced

```python
# Stream subprocess output in real time
import subprocess, sys

process = subprocess.Popen(
    ["./deploy.sh"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

output_lines = []
for line in process.stdout:
    print(line, end="")          # stream to console
    output_lines.append(line)    # capture for later

process.wait()
exit_code = process.returncode
```
