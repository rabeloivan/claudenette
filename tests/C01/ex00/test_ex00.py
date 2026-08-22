import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def run_C01_ex00(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex00_harness.c")
    exe_path = "./ft"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        (0, "42"),
        (2147483647, "42"),
        (-2147483648, "42"),
        (42, "42"),
        (143, "42"),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (initial_val, expected) in enumerate(test_cases, 1):
        actual, err, code = run_test_case(exe_path, input_data=str(initial_val))
        desc = f"ft_ft(nbr={initial_val})"

        if actual == expected:
            print_test_pass(i, f"{desc}: nbr set to {actual} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i, f"{desc}: set nbr not as expected", expected=expected, actual=actual
            )

    total_count += 1
    actual, err, code = run_test_case(exe_path, args=["null_nbr"], timeout=2)
    if err == "TIMEOUT":
        print_test_fail(total_count, "nbr=NULL: hung (timed out)")
    elif code < 0:
        print_test_fail(total_count, "nbr=NULL: crashed", actual=f"signal {-code}")
    else:
        print_test_pass(total_count, "nbr=NULL: did not crash or hang")
        passed_count += 1

    print_exercise_result("ex00/ft_ft.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
