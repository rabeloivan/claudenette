import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def run_C06_ex00(student_file):
    exe_path = "./print_program_name"

    if not compile_source([student_file], exe_path):
        return False

    print_command_execution(exe_path)

    expected = exe_path + "\n"
    actual, err, code = run_test_case(exe_path, input_data="")
    desc = f"ft_print_program_name() invoked as {exe_path}"

    passed = actual == expected
    if passed:
        print_test_pass(1, f"{desc}: output as expected")
    else:
        print_test_fail(
            1, f"{desc}: output not as expected", expected=expected, actual=actual
        )

    print_exercise_result("ex00/ft_print_program_name.c", 1 if passed else 0, 1)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed
