"""Determine the SDK version from environment variables or git."""

import os
import subprocess
import sys


def get_sdk_version() -> str:
    """Return the SDK version using this priority order:

    1. ``INPUT_VERSION`` env var (from workflow_dispatch)
    2. ``SDK_VERSION`` env var (existing)
    3. Git tag (exact match) or short commit hash
    """
    if input_version := os.environ.get("INPUT_VERSION"):
        print(f"Using INPUT_VERSION from workflow input: {input_version}", file=sys.stderr)
        return input_version

    if sdk_version := os.environ.get("SDK_VERSION"):
        print(f"Using existing SDK_VERSION: {sdk_version}", file=sys.stderr)
        return sdk_version

    try:
        version = subprocess.check_output(
            ["git", "describe", "--tags", "--exact-match"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        try:
            version = subprocess.check_output(
                ["git", "rev-parse", "--short=7", "HEAD"],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
        except subprocess.CalledProcessError:
            version = ""

    if not version:
        print("Error: Failed to determine SDK_VERSION from git.", file=sys.stderr)
        sys.exit(1)

    print(f"Using SDK version from git: {version}", file=sys.stderr)
    return version


if __name__ == "__main__":
    print(get_sdk_version())
