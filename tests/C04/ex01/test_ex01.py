import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    display_str,
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def run_C04_ex01(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex01_harness.c")
    exe_path = "./putstr"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        "",
        "Hello, World!",
        "line1\nline2\ttab",
        "42",
        "x" * 300,
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, s in enumerate(test_cases, 1):
        expected = s
        actual, err, code = run_test_case(exe_path, input_data=s)
        desc = f"ft_putstr(str={display_str(s)})"

        if actual == expected:
            print_test_pass(i, f"{desc}: output as expected")
            passed_count += 1
        else:
            print_test_fail(
                i, f"{desc}: output not as expected", expected=expected, actual=actual
            )

    print_exercise_result("ex01/ft_putstr.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
