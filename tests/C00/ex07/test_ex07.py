import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def run_C00_ex07(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex07_harness.c")
    exe_path = "./putnbr"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        (-2147483648, "-2147483648"),
        (-269, "-269"),
        (-42, "-42"),
        (0, "0"),
        (42, "42"),
        (723, "723"),
        (2147483647, "2147483647"),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (num, expected) in enumerate(test_cases, 1):
        actual, err, code = run_test_case(exe_path, input_data=str(num))
        desc = f"ft_putnbr(nb={num})"

        if actual == expected:
            print_test_pass(i, f"{desc}: output {actual} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i, f"{desc}: output not as expected", expected=expected, actual=actual
            )

    print_exercise_result("ex07/ft_putnbr.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
