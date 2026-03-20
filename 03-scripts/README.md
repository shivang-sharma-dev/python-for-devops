# Scripts

Real, runnable Python scripts for DevOps tasks.
Clone the repo, activate your venv, and run them directly.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

| Script | What it does | Run |
|---|---|---|
| `disk-usage-alert.py` | Check disk usage and alert if above threshold | `python3 disk-usage-alert.py` |
| `log-parser.py` | Parse nginx access logs and show stats | `python3 log-parser.py /var/log/nginx/access.log` |
| `health-checker.py` | Check HTTP health endpoints | `python3 health-checker.py` |
| `bulk-file-renamer.py` | Rename files in a directory by pattern | `python3 bulk-file-renamer.py /path/to/files` |
| `api-monitor.py` | Monitor API endpoints and log response times | `python3 api-monitor.py` |
| `aws-resource-lister.py` | List all EC2 instances across regions | `python3 aws-resource-lister.py` |

Read each script before running it. Every line is commented.
