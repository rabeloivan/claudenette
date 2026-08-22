import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

from ..tree_utils import NONE, build_tree, level_count, wire

C13_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNESS_UTILS = os.path.join(C13_DIR, "harness_utils.c")


def run_C13_ex06(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex06_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./level_count"

    flags = ["-Wall", "-Wextra", "-Werror", "-I", student_dir]
    if not compile_source(
        [student_file, harness_path, HARNESS_UTILS], exe_path, flags=flags
    ):
        return False

    print_command_execution(exe_path)

    # A pure left-chain (right totally absent) and a right-heavier tree
    # (left shallow, right deep) together confirm the real max() over BOTH
    # branches - a one-sided implementation fails one or the other.
    test_cases = [
        [],
        [5],
        [4, 2, 6, 1, 3, 5, 7],
        [1, 2, NONE, 3, NONE, NONE, NONE, 4],
        [1, 2, 3, NONE, NONE, NONE, 4],
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, values in enumerate(test_cases, 1):
        expected = level_count(build_tree(values))
        actual, err, code = run_test_case(exe_path, input_data=wire(values))
        desc = f"btree_level_count(tree={values})"

        try:
            actual_val = int(actual)
        except ValueError:
            actual_val = None

        if actual_val == expected:
            print_test_pass(i, f"{desc}: returned {actual_val} as expected")
            passed_count += 1
        else:
            print_test_fail(i, f"{desc}: return value not as expected", expected=expected, actual=actual)

    print_exercise_result("ex06/btree_level_count.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
