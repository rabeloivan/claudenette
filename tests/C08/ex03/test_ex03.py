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


def run_C08_ex03(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex03_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./point_test"

    flags = ["-Wall", "-Wextra", "-Werror", "-I", student_dir]
    if not compile_source([harness_path], exe_path, flags=flags):
        return False

    print_command_execution(exe_path)

    expected = "42,21"
    actual, err, code = run_test_case(exe_path, input_data="")
    desc = "t_point set via set_point(&point) then read back as point.x/point.y"

    passed = actual == expected
    if passed:
        print_test_pass(1, f"{desc}: value {display_str(actual)} as expected")
    else:
        print_test_fail(
            1, f"{desc}: value not as expected", expected=expected, actual=actual
        )

    print_exercise_result("ex03/ft_point.h", 1 if passed else 0, 1)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed
