#!/usr/bin/env python3
"""
CherryOS Auto-Flasher via mpremote
"""

import shutil
import subprocess
import sys
from pathlib import Path

FILES = ["CherryOS.py", "kernel.py", "main.py", "CherryAPI.py"]

SRC_DIR = Path(__file__).resolve().parent


def run(cmd, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def check_mpremote():
    if shutil.which("mpremote") is None:
        print("❌ mpremote not found. Install it: pip install mpremote")
        sys.exit(1)


def check_board():
    result = run(["mpremote", "connect", "list"])
    if result.returncode != 0 or not result.stdout.strip():
        print("❌ No board found. Check the USB cable and try again.")
        sys.exit(1)


def copy_files(port_args):
    print("Uploading files...")
    for i, filename in enumerate(FILES, start=1):
        src = SRC_DIR / filename
        if not src.exists():
            print(f"❌ Missing file: {src}")
            sys.exit(1)
        print(f"  [{i}/{len(FILES)}] {filename}")
        result = run(["mpremote", *port_args, "cp", str(src), f":{filename}"])
        if result.returncode != 0:
            print(f"❌ Failed to upload {filename}")
            print(result.stderr.strip())
            sys.exit(1)
    print("✅ Upload complete!")


def run_main(port_args):
    print("Starting CherryOS...")
    result = run(["mpremote", *port_args, "rtc", "--set", "+", "run", str(SRC_DIR / "main.py")])
    if result.returncode != 0:
        print("❌ Failed to start CherryOS")
        print(result.stderr.strip())
        sys.exit(1)
    print("✨ CherryOS is running!")


def ask(prompt, default=""):
    answer = input(prompt).strip()
    return answer if answer else default


def ask_yes_no(prompt, default=True):
    suffix = "Y/n" if default else "y/N"
    answer = input(f"{prompt} ({suffix}): ").strip().lower()
    if not answer:
        return default
    return answer in ("y", "yes")


def main():
    print("🍒 CherryOS Flasher 🍒")

    check_mpremote()

    port = ask("COM port (leave empty for auto-detect): ")
    port_args = ["connect", port] if port else []
    run_after = ask_yes_no("Run CherryOS after flashing?", default=True)

    check_board()
    copy_files(port_args)

    if run_after:
        run_main(port_args)


if __name__ == "__main__":
    main()