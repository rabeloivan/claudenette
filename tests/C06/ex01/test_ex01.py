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


def args_desc(params):
    if not params:
        return "(no args)"
    return "[" + ", ".join(display_str(p) for p in params) + "]"


def run_C06_ex01(student_file):
    exe_path = "./print_params"

    if not compile_source([student_file], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        [],
        ["test1", "test2", "test3"],
        ["hello"],
        ["hello world", "foo"],
        ["", "b"],
        ["a" * 100],
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, params in enumerate(test_cases, 1):
        expected = "".join(p + "\n" for p in params)
        actual, err, code = run_test_case(exe_path, input_data="", args=params)
        desc = f"ft_print_params(argv={args_desc(params)})"

        if actual == expected:
            print_test_pass(i, f"{desc}: output as expected")
            passed_count += 1
        else:
            print_test_fail(
                i, f"{desc}: output not as expected", expected=expected, actual=actual
            )

    print_exercise_result("ex01/ft_print_params.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
