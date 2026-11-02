import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def run_C00_ex02(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex02_harness.c")
    exe_path = "./print_reverse_alphabet"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    expected = "zyxwvutsrqponmlkjihgfedcba" * 2
    actual, err, code = run_test_case(exe_path, input_data="")
    passed = False

    if actual == expected:
        print_test_pass(
            1, f"ft_print_reverse_alphabet() called twice: output {actual} as expected"
        )
        passed = True
    else:
        print_test_fail(
            1,
            "ft_print_reverse_alphabet() called twice: output not as expected",
            expected=expected,
            actual=actual,
        )

    print_exercise_result("ex02/ft_print_reverse_alphabet.c", 1 if passed else 0, 1)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed
