#!/usr/bin/env python3
"""Build the MyPrivateLib XCFramework."""

import os
import shutil
import subprocess
import sys

from sdk_tools import REPO_ROOT
from sdk_tools.process import xcbeautify_piped_exit_on_failure
from sdk_tools.version import get_sdk_version


def install_tuist() -> None:
    print("Installing Tuist...")
    for cmd in [
        ["brew", "tap", "--quiet", "tuist/tuist"],
        ["brew", "install", "--quiet", "--formula", "tuist"],
    ]:
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"Command {cmd} failed with exit code {result.returncode}")
            sys.exit(result.returncode)


def tuist_setup() -> None:
    print("Installing dependencies via Tuist...")
    for cmd, label in [
        (["tuist", "install"], "tuist install"),
        (["tuist", "generate", "--no-open"], "tuist generate"),
    ]:
        result = subprocess.Popen(cmd, cwd=REPO_ROOT)
        result.wait()
        if result.returncode != 0:
            print(f"{label} failed with exit code {result.returncode}")
            sys.exit(result.returncode)


def compute_checksum(zip_path: str) -> str:
    result = subprocess.run(
        ["xcrun", "swift", "package", "compute-checksum", zip_path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"compute-checksum failed: {result.stderr}")
        sys.exit(result.returncode)
    checksum = result.stdout.strip()
    print(f"Checksum: {checksum}")
    return checksum


def main() -> None:
    sdk_version = get_sdk_version()
    print(f"Building XCFramework For Version '{sdk_version}'...")

    framework_name = "MyPrivateLib"
    scheme_name = "MyPrivateLib"
    archive_path = REPO_ROOT / ".build"
    product_output = archive_path / "Product"
    xcframework_path = product_output / f"{framework_name}-{sdk_version}.xcframework"

    if archive_path.exists():
        shutil.rmtree(archive_path)
    archive_path.mkdir(parents=True)

    install_tuist()
    tuist_setup()

    common_args = [
        "-project", "MyPrivateLib.xcodeproj",
        "-configuration", "Release",
        "-scheme", scheme_name,
        "-skipPackagePluginValidation",
        "-skipMacroValidation",
    ]

    print("Archiving for iOS Device...")
    xcbeautify_piped_exit_on_failure([
        "xcodebuild", "archive",
        *common_args,
        "-destination", "generic/platform=iOS",
        "-archivePath", str(archive_path / "iOS.xcarchive"),
    ])

    print("Archiving for iOS Simulator...")
    xcbeautify_piped_exit_on_failure([
        "xcodebuild", "archive",
        *common_args,
        "-destination", "generic/platform=iOS Simulator",
        "-archivePath", str(archive_path / "iOS-Simulator.xcarchive"),
    ])

    print("Creating XCFramework...")
    product_output.mkdir(parents=True, exist_ok=True)
    xcbeautify_piped_exit_on_failure([
        "xcodebuild", "-create-xcframework",
        "-archive", str(archive_path / "iOS.xcarchive"),
        "-framework", f"{framework_name}.framework",
        "-archive", str(archive_path / "iOS-Simulator.xcarchive"),
        "-framework", f"{framework_name}.framework",
        "-output", str(xcframework_path),
    ])

    if keychain_path := os.environ.get("KEYCHAIN_PATH"):
        print("Signing XCFramework...")
        result = subprocess.run([
            "codesign", "--timestamp",
            "--keychain", keychain_path,
            "-s", "Apple Distribution",
            str(xcframework_path),
        ])
        if result.returncode != 0:
            print(f"codesign failed with exit code {result.returncode}")
            sys.exit(result.returncode)
    else:
        print("KEYCHAIN_PATH not set, skipping XCFramework signing.")

    print("Zipping XCFramework...")
    xcframework_zip_path = shutil.make_archive(
        base_name=str(product_output / f"{framework_name}-{sdk_version}.xcframework"),
        format="zip",
        root_dir=str(product_output),
        base_dir=xcframework_path.name,
    )

    xcframework_zip_checksum = compute_checksum(xcframework_zip_path)

    if os.environ.get("GITHUB_ACTIONS") == "true":
        print("Export output paths to GitHub")
        github_env = os.environ["GITHUB_ENV"]
        with open(github_env, "a") as f:
            f.write(f"XCFRAMEWORK_PATH={xcframework_path}\n")
            f.write(f"XCFRAMEWORK_ZIP_OUTPUT={xcframework_zip_path}\n")
            f.write(f"XCFRAMEWORK_ZIP_CHECKSUM={xcframework_zip_checksum}\n")

    print(f"XCFramework created successfully at {xcframework_path}")
    print(f"XCFramework zip: {xcframework_zip_path}")


if __name__ == "__main__":
    main()
