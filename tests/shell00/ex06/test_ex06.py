import os
import shutil
import subprocess
import tempfile

from utils.ui import (
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

from ...shell_utils import run_sh


def _build_fixture_repo(scratch):
    env = {**os.environ}
    subprocess.run(["git", "init", "-q"], cwd=scratch, env=env, check=True)

    with open(f"{scratch}/.gitignore", "w") as f:
        # "nothere.log" matches nothing on disk - must NOT be reported,
        # since the exercise asks for *existing* ignored files only.
        f.write("*.log\nbuild/\nnothere.log\n")

    with open(f"{scratch}/tracked.txt", "w") as f:
        f.write("kept\n")
    subprocess.run(["git", "add", "tracked.txt", ".gitignore"], cwd=scratch, env=env, check=True)

    with open(f"{scratch}/debug.log", "w") as f:
        f.write("ignored file that exists\n")
    os.mkdir(f"{scratch}/build")
    with open(f"{scratch}/build/out.o", "w") as f:
        f.write("ignored via directory pattern\n")

    return env


def run_shell00_ex06(student_file):
    abs_file = os.path.abspath(student_file)
    i = 0
    passed = 0

    def check(condition, description, expected=None, actual=None, show_value=None):
        nonlocal i, passed
        i += 1
        if condition:
            if show_value is not None:
                print_test_pass(i, f"{description} {show_value} as expected")
            else:
                print_test_pass(i, f"{description} as expected")
            passed += 1
        else:
            print_test_fail(
                i, f"{description} not as expected", expected=expected, actual=actual
            )

    scratch = tempfile.mkdtemp(prefix="claudenette_shell00_ex06_")
    try:
        env = _build_fixture_repo(scratch)
        expected_raw = subprocess.run(
            ["git", "ls-files", "--others", "--ignored", "--exclude-standard"],
            cwd=scratch,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        expected = set(line for line in expected_raw.splitlines() if line)

        actual, err, code = run_sh(abs_file, interpreter="bash", cwd=scratch, env=env)
        actual_set = set(line for line in actual.splitlines() if line)

        check(
            actual_set == expected,
            "listed ignored files (as a set)",
            expected=sorted(expected),
            actual=sorted(actual_set),
            show_value=sorted(actual_set),
        )
        check(
            "nothere.log" not in actual_set,
            "does not list a .gitignore pattern that matches no real file",
        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    print_exercise_result(student_file, passed, i)
    return passed == i
