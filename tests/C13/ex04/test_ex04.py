import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

from ..tree_utils import Node, prefix

C13_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNESS_UTILS = os.path.join(C13_DIR, "harness_utils.c")
BTREE_CREATE_NODE_REF = os.path.join(C13_DIR, "btree_create_node_ref.c")


def insert(root, val, cmp):
    if root is None:
        return Node(val)
    if cmp(val, root.val) < 0:
        root.left = insert(root.left, val, cmp)
    else:
        root.right = insert(root.right, val, cmp)
    return root


def cmp_asc(a, b):
    return a - b


def cmp_mod10(a, b):
    return (a % 10) - (b % 10)


def run_C13_ex04(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex04_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./insert_data"

    flags = ["-Wall", "-Wextra", "-Werror", "-I", student_dir]
    if not compile_source(
        [student_file, harness_path, BTREE_CREATE_NODE_REF, HARNESS_UTILS],
        exe_path,
        flags=flags,
    ):
        return False

    print_command_execution(exe_path)

    # (cmp_selector, values inserted in order) - "M" uses a mod-10 comparator
    # so 10 and 20 (and 5 and 15) tie under it despite being visibly
    # different values, discriminating a solution that sends ties left
    # instead of the subject's mandated "higher or equal -> right".
    test_cases = [
        ("A", [1, 2, 3, 4, 5]),
        ("A", [5, 4, 3, 2, 1]),
        ("A", [4, 2, 6, 1, 3, 5, 7]),
        ("A", [42]),
        ("A", []),
        ("M", [10, 5, 15, 20]),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (sel, values) in enumerate(test_cases, 1):
        cmp = cmp_mod10 if sel == "M" else cmp_asc
        root = None
        for v in values:
            root = insert(root, v, cmp)
        expected = prefix(root)
        input_str = f"{sel}\n{len(values)}\n" + ",".join(str(x) for x in values)
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        cmp_name = "mod10" if sel == "M" else "asc"
        desc = f"btree_insert_data(insert {values} in order, cmp={cmp_name})"

        actual_vals = None
        if actual == "" and not expected:
            actual_vals = []
        else:
            try:
                actual_vals = [int(x) for x in actual.split(",")]
            except ValueError:
                actual_vals = None

        if actual_vals == expected:
            print_test_pass(
                i, f"{desc}: resulting tree's prefix order {actual_vals} as expected"
            )
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: resulting tree's prefix order not as expected",
                expected=expected,
                actual=actual_vals if actual_vals is not None else actual,
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

    print_exercise_result("ex04/btree_insert_data.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
