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

from ..tree_utils import NONE, build_tree, levels, wire

C13_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNESS_UTILS = os.path.join(C13_DIR, "harness_utils.c")


def run_C13_ex07(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex07_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./apply_by_level"

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
        [1, 2, NONE, 3, NONE, NONE, NONE, 4],
        [1, 2, 3, NONE, NONE, NONE, 4],
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, values in enumerate(test_cases, 1):
        expected = levels(build_tree(values))
        expected_str = ",".join(
            f"{v}:{lvl}:{1 if first else 0}" for v, lvl, first in expected
        )
        actual, err, code = run_test_case(exe_path, input_data=wire(values))
        desc = f"btree_apply_by_level(tree={values})"

        if actual == expected_str:
            print_test_pass(
                i,
                f"{desc}: (item,level,is_first) sequence {display_str(expected_str)} "
                "as expected",
            )
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: (item,level,is_first) sequence not as expected",
                expected=expected_str,
                actual=actual,
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

    print_exercise_result("ex07/btree_apply_by_level.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
