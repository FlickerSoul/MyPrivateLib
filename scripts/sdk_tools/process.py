"""Process execution utilities."""

import subprocess
import sys
from pathlib import Path
from typing import Tuple

from sdk_tools import REPO_ROOT


def xcbeautify_piped(cmd: list[str], cwd: Path = REPO_ROOT) -> Tuple[int, int, bool]:
    """Run a command piped through xcbeautify.

    Args:
        cmd: Command and arguments to execute.
        cwd: Working directory for the command. Defaults to ``REPO_ROOT``.
    """
    p1 = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd
    )
    p2 = subprocess.Popen(
        ["xcbeautify", "--renderer", "github-actions"], stdin=p1.stdout
    )
    assert p1.stdout
    p1.stdout.close()
    p2.communicate()
    p1.wait()

    return p1.returncode, p2.returncode, p1.returncode == 0 and p2.returncode == 0


def xcbeautify_piped_exit_on_failure(cmd: list[str], cwd: Path = REPO_ROOT) -> None:
    """Run a command piped through xcbeautify, exiting on failure.

    Args:
        cmd: Command and arguments to execute.
        cwd: Working directory for the command. Defaults to ``REPO_ROOT``.
    """
    returncode_cmd, returncode_xcbeautify, success = xcbeautify_piped(cmd, cwd)
    if not success:
        print(f"Command failed with exit code {returncode_cmd}, xcbeautify exit code {returncode_xcbeautify}")
        sys.exit(1)
