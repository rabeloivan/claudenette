import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

FREE_TRACKER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "free_tracker.c",
)

C13_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNESS_UTILS = os.path.join(C13_DIR, "harness_utils.c")


def run_C13_ex00(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex00_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./create_node"

    flags = ["-Wall", "-Wextra", "-Werror", "-I", student_dir]
    if not compile_source(
        [student_file, harness_path, HARNESS_UTILS, FREE_TRACKER], exe_path, flags=flags
    ):
        return False

    print_command_execution(exe_path)

    test_cases = [0, 42, -17, 100]

    passed_count = 0
    total_count = len(test_cases)

    for i, item in enumerate(test_cases, 1):
        actual, err, code = run_test_case(exe_path, input_data=str(item))
        desc = f"btree_create_node({item})"

        expected_str = f"A{item},1,1"
        if actual == expected_str:
            print_test_pass(
                i, f"{desc}: node fields (item/left/right) {expected_str} as expected"
            )
            passed_count += 1
        else:
            print_test_fail(
                i, f"{desc}: node fields not as expected", expected=expected_str, actual=actual
            )

    print_exercise_result("ex00/btree_create_node.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
