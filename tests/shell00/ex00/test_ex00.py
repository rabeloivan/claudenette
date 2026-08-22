from utils.runner import run_test_case
from utils.ui import (
    display_str,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def run_shell00_ex00(student_file):
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

    # The timeout matters here specifically, not just as a generic safety
    # net: a FIFO with no active companion writer is a real, valid solution
    # technique for this exercise, and `cat` on one blocks forever with no
    # writer attached (see the check_allowed_functions/check_norminette fix
    # in CLAUDE.md - the same underlying risk, hit here for real).
    actual, err, code = run_test_case("cat", args=[student_file], timeout=5)

    if err == "TIMEOUT":
        check(
            False,
            "`cat z` completing within 5s (it may depend on a companion "
            "process that isn't running in this environment)",
        )
    else:
        check(
            actual == "Z\n",
            f"`cat z` output {display_str(actual)}",
            expected="Z\n",
            actual=actual,
        )

    print_exercise_result(student_file, passed, i)
    return passed == i
