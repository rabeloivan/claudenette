import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


C12_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNESS_UTILS = os.path.join(C12_DIR, "harness_utils.c")


def run_C12_ex02(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex02_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./list_size"

    flags = ["-Wall", "-Wextra", "-Werror", "-I", student_dir]
    if not compile_source(
        [student_file, harness_path, HARNESS_UTILS], exe_path, flags=flags
    ):
        return False

    print_command_execution(exe_path)

    test_cases = [[], [1], [1, 2, 3], list(range(20))]

    passed_count = 0
    total_count = len(test_cases)

    for i, tab in enumerate(test_cases, 1):
        expected = len(tab)
        input_str = f"{len(tab)}\n" + ",".join(str(x) for x in tab)
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_list_size(list of {tab})"

        try:
            actual_val = int(actual)
        except ValueError:
            actual_val = None

        if actual_val == expected:
            print_test_pass(i, f"{desc}: returned {actual_val} as expected")
            passed_count += 1
        else:
            print_test_fail(i, f"{desc}: return value not as expected", expected=expected, actual=actual)

    print_exercise_result("ex02/ft_list_size.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
