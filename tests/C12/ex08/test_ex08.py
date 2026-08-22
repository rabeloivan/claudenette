import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

C12_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNESS_UTILS = os.path.join(C12_DIR, "harness_utils.c")


def run_C12_ex08(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex08_harness.c")
    exe_path = "./list_reverse"

    # ex08 is the one exercise whose "Files to Submit" list omits ft_list.h -
    # the subject explicitly says "we will use our own ft_list.h" here, so
    # this test provides its own copy (in this directory) instead of trusting
    # or even looking at whatever the student's directory might contain.
    flags = ["-Wall", "-Wextra", "-Werror", "-I", test_dir]
    if not compile_source(
        [student_file, harness_path, HARNESS_UTILS], exe_path, flags=flags
    ):
        return False

    print_command_execution(exe_path)

    test_cases = [[], [1], [1, 2, 3], [5, 5, 5], list(range(10))]

    passed_count = 0
    total_count = len(test_cases)

    for i, tab in enumerate(test_cases, 1):
        expected = list(reversed(tab))
        input_str = f"{len(tab)}\n" + ",".join(str(x) for x in tab)
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_list_reverse(list of {tab})"

        actual_vals = None
        if actual == "" and not expected:
            actual_vals = []
        else:
            try:
                actual_vals = [int(x) for x in actual.split(",")]
            except ValueError:
                actual_vals = None

        if actual_vals == expected:
            print_test_pass(i, f"{desc}: resulting list {actual_vals} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: resulting list not as expected",
                expected=expected,
                actual=actual_vals if actual_vals is not None else actual,
            )

    print_exercise_result("ex08/ft_list_reverse.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
