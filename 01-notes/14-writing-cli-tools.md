# 14 — Writing CLI Tools

> A good CLI tool feels like a first-class Unix command.
> It has help text, meaningful flags, and behaves predictably.
> This is what separates a script from a tool your team actually uses.

---

## argparse — Built-In Argument Parsing

```python
#!/usr/bin/env python3
import argparse

parser = argparse.ArgumentParser(
    description="Check disk usage and alert if above threshold",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  %(prog)s /                    Check root filesystem
  %(prog)s / --threshold 95     Custom threshold
  %(prog)s /data --warn         Warn only, don't exit 1
    """
)

parser.add_argument("path",
    help="Filesystem path to check (e.g. / or /data)")

parser.add_argument("--threshold", "-t",
    type=int,
    default=90,
    metavar="PERCENT",
    help="Alert threshold in percent (default: 90)")

parser.add_argument("--warn",
    action="store_true",
    help="Print warning but always exit 0")

parser.add_argument("--json",
    action="store_true",
    help="Output result as JSON")

parser.add_argument("--verbose", "-v",
    action="store_true",
    help="Show detailed output")

parser.add_argument("--version",
    action="version",
    version="%(prog)s 1.0.0")

args = parser.parse_args()
print(args.path)            # the positional argument
print(args.threshold)       # 90 or user-provided
print(args.warn)            # True or False
print(args.json)            # True or False
```

---

## click — The Better Way (for larger tools)

```bash
pip install click
```

```python
#!/usr/bin/env python3
import click
import json
import shutil
import sys

@click.group()
@click.version_option("1.0.0")
def cli():
    """DevOps toolkit — a collection of useful commands."""
    pass


@cli.command()
@click.argument("path", default="/")
@click.option("--threshold", "-t", default=90, show_default=True,
              help="Alert threshold in percent")
@click.option("--format", "output_format",
              type=click.Choice(["text", "json"]),
              default="text", show_default=True)
def disk(path, threshold, output_format):
    """Check disk usage at PATH."""
    total, used, free = shutil.disk_usage(path)
    usage = round(used / total * 100, 1)
    is_alert = usage > threshold

    if output_format == "json":
        click.echo(json.dumps({
            "path": path,
            "usage_percent": usage,
            "alert": is_alert
        }, indent=2))
    else:
        color = "red" if is_alert else "green"
        click.echo(f"Path:  {path}")
        click.echo(f"Usage: ", nl=False)
        click.secho(f"{usage}%", fg=color, bold=True)

    if is_alert:
        sys.exit(1)


@cli.command()
@click.argument("services", nargs=-1, required=True)
@click.option("--restart/--no-restart", default=False,
              help="Restart failed services")
def services(services, restart):
    """Check status of one or more systemd SERVICES."""
    import subprocess

    for service in services:
        result = subprocess.run(
            ["systemctl", "is-active", service],
            capture_output=True, text=True
        )
        status = result.stdout.strip()
        color = "green" if status == "active" else "red"
        click.secho(f"  {service}: {status}", fg=color)

        if status != "active" and restart:
            click.echo(f"  Restarting {service}...")
            subprocess.run(["systemctl", "restart", service])


if __name__ == "__main__":
    cli()
```

Running it:
```bash
python3 tool.py disk /                      # check root disk
python3 tool.py disk / --threshold 95       # custom threshold
python3 tool.py disk / --format json        # JSON output
python3 tool.py services nginx postgresql   # check services
python3 tool.py services nginx --restart    # check and restart if down
python3 tool.py --help                      # auto-generated help
python3 tool.py disk --help                 # command-specific help
```

---

## Reading from stdin (pipe-friendly)

```python
import sys
import click

@cli.command()
@click.argument("input", type=click.File("r"), default="-")
def parse_logs(input):
    """Parse log lines from INPUT file or stdin.

    Examples:
      cat access.log | tool parse-logs
      tool parse-logs access.log
    """
    for line in input:
        if "ERROR" in line:
            click.secho(line.strip(), fg="red")
        elif "WARNING" in line:
            click.secho(line.strip(), fg="yellow")
        else:
            click.echo(line.strip())
```

---

## Making a Script Installable

With a proper `setup.py` or `pyproject.toml`, your tool installs
as a command the user can run from anywhere.

```toml
# pyproject.toml
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "devops-toolkit"
version = "1.0.0"
dependencies = ["click", "requests", "boto3"]

[project.scripts]
devops = "devops_toolkit.main:cli"
```

```bash
pip install -e .       # install in development mode
devops disk /          # now works from anywhere
devops services nginx
```

---

## Rich — Beautiful Terminal Output

```bash
pip install rich
```

```python
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()

# Coloured output with markup
console.print("[bold green]✓ Deployment complete[/bold green]")
console.print("[bold red]✗ Health check failed[/bold red]")
console.print(f"[yellow]WARNING:[/yellow] Disk at 87%")

# Progress bar
from rich.progress import track
import time

for step in track(["Build", "Test", "Push", "Deploy"], description="Deploying..."):
    time.sleep(1)
    console.print(f"  [green]✓[/green] {step}")

# Table
table = Table(title="Server Status")
table.add_column("Server",  style="cyan")
table.add_column("CPU",     justify="right")
table.add_column("Status",  justify="center")

table.add_row("web-01", "45%",  "[green]OK[/green]")
table.add_row("web-02", "87%",  "[yellow]WARN[/yellow]")
table.add_row("db-01",  "22%",  "[green]OK[/green]")

console.print(table)
```

---

## Putting It All Together — A Real CLI Tool

```python
#!/usr/bin/env python3
"""
ops — A CLI tool for common DevOps tasks.
"""

import click
import sys
import subprocess
import shutil
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
def ops():
    """Ops — command-line tools for DevOps tasks."""
    pass


@ops.command()
def health():
    """Quick system health overview."""
    table = Table(title="System Health")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_column("Status", justify="center")

    # CPU load
    import os
    load = os.getloadavg()[0]
    cpus = os.cpu_count()
    load_pct = round(load / cpus * 100)
    load_status = "[red]HIGH[/red]" if load_pct > 80 else "[green]OK[/green]"
    table.add_row("CPU Load", f"{load:.2f} ({load_pct}%)", load_status)

    # Disk
    total, used, free = shutil.disk_usage("/")
    disk_pct = round(used / total * 100)
    disk_status = "[red]HIGH[/red]" if disk_pct > 90 else "[green]OK[/green]"
    table.add_row("Disk /", f"{disk_pct}%", disk_status)

    console.print(table)


@ops.command()
@click.argument("service")
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
@click.option("--lines", "-n", default=50, help="Number of lines to show")
def logs(service, follow, lines):
    """Show logs for a systemd SERVICE."""
    cmd = ["journalctl", "-u", service, f"-n{lines}"]
    if follow:
        cmd.append("-f")
    subprocess.run(cmd)


if __name__ == "__main__":
    ops()
