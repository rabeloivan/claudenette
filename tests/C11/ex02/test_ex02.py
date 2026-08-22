import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def has_digit(s):
    return any(c.isdigit() for c in s)


def run_C11_ex02(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex02_harness.c")
    exe_path = "./any"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        ["hello", "world", "foo"],
        ["hello", "wor1d", "foo"],
        ["4", "2"],
        ["abc"],
        [],
        ["a", "b", "c", "d", "e5"],
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, tab in enumerate(test_cases, 1):
        expected = 1 if any(has_digit(s) for s in tab) else 0
        input_str = f"{len(tab)}\n" + "\n".join(tab)
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_any(tab={tab}, f=has_digit)"

        try:
            actual_val = int(actual)
        except ValueError:
            actual_val = None

        if actual_val == expected:
            print_test_pass(i, f"{desc}: returned {actual_val} as expected")
            passed_count += 1
        else:
            print_test_fail(i, f"{desc}: return value not as expected", expected=expected, actual=actual)

    print_exercise_result("ex02/ft_any.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
