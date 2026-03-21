#!/usr/bin/env python3
"""Create a draft release on the binary release repository and update Package.swift."""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from sdk_tools import REPO_ROOT


BINARY_REPO_DIR = REPO_ROOT / "binary-repo"


def run(cmd: list[str], cwd: Optional[Path] = None, capture_output: bool = False) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, cwd=cwd, capture_output=capture_output, text=True)
    if result.returncode != 0:
        if capture_output:
            print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    return result


def create_draft_release(binary_repo: str, version: str, xcframework_zip: str, checksum: str) -> None:
    print(f"Creating draft release {version} on {binary_repo}...")
    run([
        "gh", "release", "create", version,
        xcframework_zip,
        "--repo", binary_repo,
        "--title", f"Release {version}",
        "--notes", f"Release of version {version}.\n Checksum: `{checksum}`.",
        "--draft",
    ])


def get_asset_url(binary_repo: str, version: str) -> str:
    print("Fetching asset URL from draft release...")
    result = run(
        ["gh", "release", "view", version, "--repo", binary_repo, "--json", "assets"],
        capture_output=True,
    )
    assets = json.loads(result.stdout)["assets"]
    xcframework_asset = next((a for a in assets if a["name"].endswith(".xcframework.zip")), None)
    if xcframework_asset is None:
        names = [a["name"] for a in assets]
        print(f"Error: no *.xcframework.zip asset found in release assets: {names}", file=sys.stderr)
        sys.exit(1)
    url = xcframework_asset["apiUrl"] + ".zip"
    print(f"Asset URL: {url}")
    return url


TARGET_NAME = "MyPrivateLib"


def update_package_swift(asset_url: str, checksum: str) -> None:
    package_swift = BINARY_REPO_DIR / "Package.swift"
    print(f"Updating {package_swift}...")

    result = run(["swift", "package", "dump-package"], cwd=BINARY_REPO_DIR, capture_output=True)
    package_json = json.loads(result.stdout)
    target = next((t for t in package_json["targets"] if t["name"] == TARGET_NAME), None)
    if target is None:
        names = [t["name"] for t in package_json["targets"]]
        print(f"Error: target '{TARGET_NAME}' not found in Package.swift. Found: {names}", file=sys.stderr)
        sys.exit(1)

    current_url: str = target["url"]
    current_checksum: str = target["checksum"]

    content = package_swift.read_text()
    content = content.replace(current_url, asset_url)
    content = content.replace(current_checksum, checksum)
    package_swift.write_text(content)


def commit_and_tag(version: str) -> str:
    print("Committing Package.swift update...")
    run(["git", "config", "user.email", "app@universe.observer"], cwd=BINARY_REPO_DIR)
    run(["git", "config", "user.name", "MyPrivateLib App"], cwd=BINARY_REPO_DIR)
    run(["git", "add", "Package.swift"], cwd=BINARY_REPO_DIR)
    run(["git", "commit", "-m", f"Update Package.swift for release {version}"], cwd=BINARY_REPO_DIR)

    print(f"Creating tag {version} and pushing...")
    run(["git", "tag", version], cwd=BINARY_REPO_DIR)
    run(["git", "push", "--set-upstream", "origin", "main"], cwd=BINARY_REPO_DIR)
    run(["git", "push", "origin", "main"], cwd=BINARY_REPO_DIR)

    result = run(["git", "rev-parse", "HEAD"], cwd=BINARY_REPO_DIR, capture_output=True)
    return result.stdout.strip()


def update_release_target(binary_repo: str, version: str, commit_sha: str) -> None:
    print(f"Updating draft release target to commit {commit_sha}...")
    run([
        "gh", "release", "edit", version,
        "--repo", binary_repo,
        "--target", commit_sha,
    ])


def main() -> None:
    binary_repo = os.environ.get("RELEASE_REPO")
    version = os.environ.get("SDK_VERSION")
    xcframework_zip = os.environ.get("XCFRAMEWORK_ZIP_OUTPUT")
    checksum = os.environ.get("XCFRAMEWORK_ZIP_CHECKSUM")

    missing = [
        name for name, val in [
            ("RELEASE_REPO", binary_repo),
            ("SDK_VERSION", version),
            ("XCFRAMEWORK_ZIP_OUTPUT", xcframework_zip),
            ("XCFRAMEWORK_ZIP_CHECKSUM", checksum),
        ] if not val
    ]
    if missing:
        print(f"Error: missing required environment variables: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    errors: list[str] = []

    xcframework_path = Path(xcframework_zip)
    if not xcframework_path.name.endswith(".xcframework.zip"):
        errors.append(f"XCFRAMEWORK_ZIP_OUTPUT filename must end with '.xcframework.zip', got '{xcframework_path.name}'")
    if not xcframework_path.exists():
        errors.append(f"XCFRAMEWORK_ZIP_OUTPUT does not exist: {xcframework_zip}")

    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    create_draft_release(binary_repo, version, xcframework_zip, checksum)
    asset_url = get_asset_url(binary_repo, version)
    update_package_swift(asset_url, checksum)
    commit_sha = commit_and_tag(version)
    update_release_target(binary_repo, version, commit_sha)

    print("Release upload complete.")


if __name__ == "__main__":
    main()
