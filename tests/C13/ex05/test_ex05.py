import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

from ..tree_utils import build_tree, infix, wire

C13_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNESS_UTILS = os.path.join(C13_DIR, "harness_utils.c")


def run_C13_ex05(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex05_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./search_item"

    flags = ["-Wall", "-Wextra", "-Werror", "-I", student_dir]
    if not compile_source(
        [student_file, harness_path, HARNESS_UTILS], exe_path, flags=flags
    ):
        return False

    print_command_execution(exe_path)

    # (data_ref, tree values). [5, 9, 1] is deliberately NOT a valid BST
    # (left child 9 > root 5) - the subject mandates search via infix
    # traversal, not a BST shortcut, so a solution that "optimizes" into a
    # binary-search-style descent (go left/right based on comparison,
    # assuming sorted structure) fails to find 9 or 1 in this shape, while a
    # genuine linear infix scan finds them trivially.
    test_cases = [
        (5, [4, 2, 6, 1, 3, 5, 7]),
        (99, [4, 2, 6, 1, 3, 5, 7]),
        (4, [4, 2, 6, 1, 3, 5, 7]),
        (1, [4, 2, 6, 1, 3, 5, 7]),
        (9, [5, 9, 1]),
        (1, [5, 9, 1]),
        (7, []),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (ref, values) in enumerate(test_cases, 1):
        seq = infix(build_tree(values))
        matches = [x for x in seq if x == ref]
        expected = matches[0] if matches else None
        input_str = f"{ref}\n" + wire(values)
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"btree_search_item(tree={values}, data_ref={ref})"

        if expected is None:
            if actual == "N":
                print_test_pass(i, f"{desc}: returned NULL as expected")
                passed_count += 1
            else:
                print_test_fail(i, f"{desc}: expected NULL", expected="NULL", actual=actual)
            continue

        if actual == f"A{expected}":
            print_test_pass(i, f"{desc}: returned item as expected")
            passed_count += 1
        else:
            print_test_fail(
                i, f"{desc}: returned item not as expected", expected=f"item={expected}", actual=actual
            )

    total_count += 1
    actual, err, code = run_test_case(exe_path, args=["nullcb"], timeout=2)
    if err == "TIMEOUT":
        print_test_fail(total_count, "cmpf=NULL on a non-empty tree: hung (timed out)")
    elif code < 0:
        print_test_fail(
            total_count, "cmpf=NULL on a non-empty tree: crashed", actual=f"signal {-code}"
        )
    else:
        print_test_pass(total_count, "cmpf=NULL on a non-empty tree: did not crash or hang")
        passed_count += 1

    print_exercise_result("ex05/btree_search_item.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
