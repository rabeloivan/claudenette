import os
import shutil
import subprocess
import tempfile

from utils.ui import print_exercise_result, print_test_fail, print_test_pass

from ...shell_utils import run_sh

GIT_ENV_NAME = {
    "GIT_AUTHOR_NAME": "Claudenette",
    "GIT_AUTHOR_EMAIL": "test@student.42.fr",
    "GIT_COMMITTER_NAME": "Claudenette",
    "GIT_COMMITTER_EMAIL": "test@student.42.fr",
}


def _build_fixture_repo(scratch):
    env = {**os.environ, **GIT_ENV_NAME}
    subprocess.run(["git", "init", "-q"], cwd=scratch, env=env, check=True)
    for n in range(7):
        with open(f"{scratch}/file{n}.txt", "w") as f:
            f.write(f"content {n}\n")
        subprocess.run(["git", "add", f"file{n}.txt"], cwd=scratch, env=env, check=True)
        subprocess.run(
            ["git", "commit", "-q", "-m", f"commit {n}"], cwd=scratch, env=env, check=True
        )
    return env


def run_shell00_ex05(student_file):
    abs_file = os.path.abspath(student_file)
    i = 0
    passed = 0

    def check(condition, description, expected=None, actual=None):
        nonlocal i, passed
        i += 1
        if condition:
            print_test_pass(i, f"{description} as expected")
            passed += 1
        else:
            print_test_fail(
                i, f"{description} not as expected", expected=expected, actual=actual
            )

    scratch = tempfile.mkdtemp(prefix="claudenette_shell00_ex05_")
    try:
        env = _build_fixture_repo(scratch)
        expected = subprocess.run(
            ["git", "log", "-n", "5", "--format=%H"],
            cwd=scratch,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip("\n")

        actual, err, code = run_sh(abs_file, interpreter="bash", cwd=scratch, env=env)
        actual_stripped = actual.rstrip("\n")
        check(
            actual_stripped == expected,
            "output (last 5 commit ids, newest first)",
            expected=expected,
            actual=actual_stripped,
        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    print_exercise_result(student_file, passed, i)
    return passed == i
