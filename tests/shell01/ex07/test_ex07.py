import os

from utils.ui import (
    display_str,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

from ...shell_utils import run_sh


def _expected_r_dwssap(passwd_text, line1, line2):
    # Verified character-by-character against the subject's own worked
    # example ("for lines 7 to 15"): reversed login names like
    # "sorebrek_brk_" decode back to real account names ("_krb_kerberos"),
    # and the shown order is descending-alphabetical on the *reversed*
    # strings themselves, confirming FT_LINE1/FT_LINE2 are a 1-indexed
    # inclusive *positional* slice of the sorted list, not a value filter.
    lines = passwd_text.splitlines()
    non_comment = [line for line in lines if not line.startswith("#")]
    every_other = non_comment[1::2]
    logins = [line.split(":")[0] for line in every_other]
    reversed_logins = [login[::-1] for login in logins]
    sorted_desc = sorted(reversed_logins, reverse=True)
    selected = sorted_desc[line1 - 1:line2]
    return ", ".join(selected) + "."


def run_shell01_ex07(student_file):
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

    with open("/etc/passwd", "r") as f:
        passwd_text = f.read()

    # Two different ranges - not just the subject's own "7 to 15" example -
    # to confirm the positional-slice logic generalizes rather than being
    # coincidentally right for one range.
    for line1, line2 in [(7, 15), (1, 5), (20, 20)]:
        expected = _expected_r_dwssap(passwd_text, line1, line2)
        env = {**os.environ, "FT_LINE1": str(line1), "FT_LINE2": str(line2)}
        actual, err, code = run_sh(student_file, env=env)
        actual_stripped = actual.rstrip("\n")
        check(
            actual_stripped == expected,
            f"FT_LINE1={line1} FT_LINE2={line2}: output",
            expected=expected,
            actual=actual_stripped,
            show_value=actual_stripped,
        )

    print_exercise_result(student_file, passed, i)
    return passed == i
