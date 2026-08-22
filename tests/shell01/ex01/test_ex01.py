import os
import subprocess

from utils.ui import (
    display_str,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

from ...shell_utils import run_sh

# Real macOS accounts guaranteed to exist locally, rather than the
# subject's own Debian/Ubuntu-flavored example groups (adm, cdrom, sudo,
# dip, plugdev, lxd, lpadmin, libvirt) which don't exist on this machine.
TEST_USERS = ["daemon", os.environ.get("USER") or os.environ.get("LOGNAME") or "nobody"]


def run_shell01_ex01(student_file):
    i = 0
    passed = 0

    def check(condition, description, expected=None, actual=None, show_value=None):
        nonlocal i, passed
        i += 1
        if condition:
            if show_value is not None:
                print_test_pass(i, f"{description} {display_str(show_value)} as expected")
            else:
                print_test_pass(i, f"{description} as expected")
            passed += 1
        else:
            print_test_fail(
                i, f"{description} not as expected", expected=expected, actual=actual
            )

    for user in TEST_USERS:
        expected_groups = subprocess.run(
            ["id", "-Gn", user], capture_output=True, text=True, timeout=5
        ).stdout.split()
        expected = ",".join(expected_groups)

        env = {**os.environ, "FT_USER": user}
        actual, err, code = run_sh(student_file, env=env)
        actual_stripped = actual.rstrip("\n")

        check(
            actual_stripped == expected,
            f"FT_USER={user}: comma-separated groups",
            expected=expected,
            actual=actual_stripped,
            show_value=actual_stripped,
        )
        check(
            " " not in actual_stripped,
            f"FT_USER={user}: no spaces in the output",
        )

    print_exercise_result(student_file, passed, i)
    return passed == i
