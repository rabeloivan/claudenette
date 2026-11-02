import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

from ..tree_utils import NONE, build_tree, suffix, wire

C13_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNESS_UTILS = os.path.join(C13_DIR, "harness_utils.c")


def run_C13_ex03(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex03_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./apply_suffix"

    flags = ["-Wall", "-Wextra", "-Werror", "-I", student_dir]
    if not compile_source(
        [student_file, harness_path, HARNESS_UTILS], exe_path, flags=flags
    ):
        return False

    print_command_execution(exe_path)

    test_cases = [
        [],
        [5],
        [4, 2, 6, 1, 3, 5, 7],
        [1, 2, 3, NONE, NONE, NONE, 4],
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, values in enumerate(test_cases, 1):
        expected = suffix(build_tree(values))
        actual, err, code = run_test_case(exe_path, input_data=wire(values))
        desc = f"btree_apply_suffix(tree={values})"

        actual_vals = None
        if actual == "" and not expected:
            actual_vals = []
        else:
            try:
                actual_vals = [int(x) for x in actual.split(",")]
            except ValueError:
                actual_vals = None

        if actual_vals == expected:
            print_test_pass(i, f"{desc}: traversal order {actual_vals} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: traversal order not as expected",
                expected=expected,
                actual=actual_vals if actual_vals is not None else actual,
            )

    total_count += 1
    actual, err, code = run_test_case(exe_path, args=["nullcb"], timeout=2)
    if err == "TIMEOUT":
        print_test_fail(total_count, "applyf=NULL on a non-empty tree: hung (timed out)")
    elif code < 0:
        print_test_fail(
            total_count, "applyf=NULL on a non-empty tree: crashed", actual=f"signal {-code}"
        )
    else:
        print_test_pass(total_count, "applyf=NULL on a non-empty tree: did not crash or hang")
        passed_count += 1

    print_exercise_result("ex03/btree_apply_suffix.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
