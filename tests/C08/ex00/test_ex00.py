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


def run_C08_ex00(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex00_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./ft_h_test"

    flags = ["-Wall", "-Wextra", "-Werror", "-I", student_dir]
    if not compile_source([harness_path], exe_path, flags=flags):
        return False

    print_command_execution(exe_path)

    expected = "ABCSWAPOK5CMPOK"
    actual, err, code = run_test_case(exe_path, input_data="")
    desc = "ft.h prototypes (ft_putchar/ft_swap/ft_putstr/ft_strlen/ft_strcmp)"

    passed = actual == expected
    if passed:
        print_test_pass(1, f"{desc}: wired correctly, output {display_str(actual)} as expected")
    else:
        print_test_fail(
            1, f"{desc}: output not as expected", expected=expected, actual=actual
        )

    print_exercise_result("ex00/ft.h", 1 if passed else 0, 1)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed
