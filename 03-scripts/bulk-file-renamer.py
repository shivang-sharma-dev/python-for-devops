#!/usr/bin/env python3
"""
bulk-file-renamer.py

Rename files in a directory using a pattern.
Always shows a preview before making changes.

Usage:
    python3 bulk-file-renamer.py /var/log/myapp --prefix "app-" --ext .log
    python3 bulk-file-renamer.py /tmp/backups --add-date --ext .tar.gz
    python3 bulk-file-renamer.py /tmp/logs --replace "old" "new"
    python3 bulk-file-renamer.py /tmp/files --lowercase

Add --apply to actually rename (dry-run by default).
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path


def get_new_name(filename, args):
    """
    Calculate the new filename based on the given options.
    Returns new filename string, or None if no change needed.
    """
    stem   = Path(filename).stem
    suffix = Path(filename).suffix
    new_stem = stem

    # Apply transformations in order
    if args.lowercase:
        new_stem = new_stem.lower()

    if args.uppercase:
        new_stem = new_stem.upper()

    if args.replace:
        old, new = args.replace
        new_stem = new_stem.replace(old, new)

    if args.prefix:
        new_stem = args.prefix + new_stem

    if args.suffix_str:
        new_stem = new_stem + args.suffix_str

    if args.add_date:
        date = datetime.now().strftime("%Y%m%d")
        new_stem = f"{new_stem}_{date}"

    new_name = new_stem + suffix
    return new_name if new_name != filename else None


def rename_files(directory, args):
    """Preview and optionally rename files in directory."""
    path = Path(directory)

    if not path.is_dir():
        print(f"Error: Not a directory: {directory}")
        sys.exit(1)

    # Collect matching files
    if args.ext:
        files = sorted(path.glob(f"*{args.ext}"))
    else:
        files = sorted(f for f in path.iterdir() if f.is_file())

    if not files:
        print(f"No files found in {directory}")
        return

    # Calculate renames
    renames = []
    for f in files:
        new_name = get_new_name(f.name, args)
        if new_name:
            renames.append((f, path / new_name))

    if not renames:
        print("No files need renaming with the given options.")
        return

    # Show preview
    print(f"\n{'Old Name':<40} {'New Name':<40}")
    print("─" * 82)
    for old, new in renames:
        print(f"{old.name:<40} {new.name:<40}")

    print(f"\n{len(renames)} file(s) would be renamed.")

    if not args.apply:
        print("\n[DRY RUN] Add --apply to actually rename files.")
        return

    # Confirm before applying
    if not args.yes:
        answer = input("\nApply these renames? [y/N] ").strip().lower()
        if answer != "y":
            print("Aborted.")
            return

    # Apply renames
    renamed = 0
    for old, new in renames:
        if new.exists():
            print(f"  SKIP: {new.name} already exists")
            continue
        old.rename(new)
        print(f"  ✓ {old.name} → {new.name}")
        renamed += 1

    print(f"\nRenamed {renamed} file(s).")


def main():
    parser = argparse.ArgumentParser(
        description="Bulk rename files in a directory",
        epilog="Dry run by default. Add --apply to make changes."
    )
    parser.add_argument("directory",
        help="Directory containing files to rename")
    parser.add_argument("--ext",
        help="Only rename files with this extension (e.g. .log)")
    parser.add_argument("--prefix",
        help="Add prefix to filenames")
    parser.add_argument("--suffix-str", dest="suffix_str",
        help="Add suffix to filename stems (before extension)")
    parser.add_argument("--replace", nargs=2, metavar=("OLD", "NEW"),
        help="Replace OLD with NEW in filenames")
    parser.add_argument("--add-date", action="store_true",
        help="Append today's date (YYYYMMDD) to filenames")
    parser.add_argument("--lowercase", action="store_true",
        help="Convert filenames to lowercase")
    parser.add_argument("--uppercase", action="store_true",
        help="Convert filenames to uppercase")
    parser.add_argument("--apply", action="store_true",
        help="Actually rename files (default is dry run)")
    parser.add_argument("--yes", "-y", action="store_true",
        help="Skip confirmation prompt")

    args = parser.parse_args()

    if not any([args.prefix, args.suffix_str, args.replace,
                args.add_date, args.lowercase, args.uppercase]):
        parser.error("Specify at least one rename operation (--prefix, --replace, etc.)")

    rename_files(args.directory, args)


if __name__ == "__main__":
    main()
