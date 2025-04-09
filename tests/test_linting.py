import subprocess
import warnings

import pytest


def run_linter(name: str, cmd: list[str], warn_only: bool = False) -> None:
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=True,
    )

    msgs = []
    out, err = process.communicate()
    if process.returncode != 0:
        if err:
            msgs.append(
                f"{name} exited with code {process.returncode} and has unexpected output on stderr:\n{err.decode().rstrip()}",  # noqa: E501
            )
        if out:
            msgs.append(f"{name} found issues:\n{out.decode().rstrip()}")
        if not msgs:
            msgs.append(
                f"{name} exited with code {process.returncode} and has no output on stdout or stderr.",
            )
        if warn_only:
            warnings.warn("\n".join(msgs), stacklevel=2)
        else:
            pytest.fail("\n".join(msgs))


@pytest.mark.linting
def test_ruff() -> None:
    cmd = ["python3", "-m", "ruff", "check", "cinemabot", "tests"]
    run_linter("ruff", cmd)
