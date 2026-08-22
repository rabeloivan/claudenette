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

EVEN_TEXT = "I have an even number of arguments.\n"
ODD_TEXT = "I have an odd number of arguments.\n"


def run_C08_ex01(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex01_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./boolean_test"

    flags = ["-Wall", "-Wextra", "-Werror", "-I", student_dir]
    if not compile_source([harness_path], exe_path, flags=flags):
        return False

    print_command_execution(exe_path)

    test_cases = [
        ([], EVEN_TEXT),
        (["a"], ODD_TEXT),
        (["a", "b"], EVEN_TEXT),
        (["a", "b", "c"], ODD_TEXT),
        (["a", "b", "c", "d"], EVEN_TEXT),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (args, expected) in enumerate(test_cases, 1):
        actual, err, code = run_test_case(exe_path, input_data="", args=args)
        desc = f"program run with {len(args)} argument(s)"

        if actual == expected:
            print_test_pass(i, f"{desc}: output {display_str(actual)} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i, f"{desc}: output not as expected", expected=expected, actual=actual
            )

    print_exercise_result("ex01/ft_boolean.h", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
