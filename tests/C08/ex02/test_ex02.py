import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def run_C08_ex02(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex02_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./abs_test"

    flags = ["-Wall", "-Wextra", "-Werror", "-I", student_dir]
    if not compile_source([harness_path], exe_path, flags=flags):
        return False

    print_command_execution(exe_path)

    # (a, b) -> ABS(a - b); b != 0 cases catch a macro missing outer parens
    # around its argument (classic ABS(Value) vs ABS((Value)) macro bug).
    test_cases = [
        (5, 0),
        (-5, 0),
        (0, 0),
        (2147483647, 0),
        (-2147483647, 0),
        (3, 10),
        (10, 3),
        (0, 5),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (a, b) in enumerate(test_cases, 1):
        expected = abs(a - b)
        input_str = f"{a}\n{b}"
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ABS({a} - {b})"

        try:
            actual_val = int(actual)
        except ValueError:
            actual_val = None

        if actual_val == expected:
            print_test_pass(i, f"{desc}: evaluated to {actual_val} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: evaluated not as expected",
                expected=expected,
                actual=actual_val,
            )

    print_exercise_result("ex02/ft_abs.h", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
