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


def run_C12_ex17(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex17_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./sorted_merge"

    # cmp is prototyped `int (*cmp)()` per the subject (K&R unspecified-args
    # style), which trips Clang's -Wdeprecated-non-prototype under -Werror
    # even though the code is subject-compliant.
    flags = [
        "-Wall", "-Wextra", "-Werror", "-Wno-deprecated-non-prototype",
        "-I", student_dir,
    ]
    if not compile_source(
        [student_file, harness_path, HARNESS_UTILS], exe_path, flags=flags
    ):
        return False

    print_command_execution(exe_path)

    # (cmp_selector, tab1, tab2) - both already sorted per that comparator.
    # The "D" case only passes if the implementation genuinely delegates to
    # cmp instead of assuming ascending order.
    test_cases = [
        ("A", [1, 3, 5], [2, 4, 6]),
        ("A", [], [1, 2, 3]),
        ("A", [1, 2, 3], []),
        ("A", [], []),
        ("D", [5, 3, 1], [6, 4, 2]),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (sel, tab1, tab2) in enumerate(test_cases, 1):
        expected = sorted(tab1 + tab2, reverse=(sel == "D"))
        input_str = (
            f"{sel}\n{len(tab1)}\n" + ",".join(str(x) for x in tab1) + "\n"
            f"{len(tab2)}\n" + ",".join(str(x) for x in tab2)
        )
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        cmp_name = "desc" if sel == "D" else "asc"
        desc = f"ft_sorted_list_merge(list1={tab1}, list2={tab2}, cmp={cmp_name})"

        actual_vals = None
        if actual == "" and not expected:
            actual_vals = []
        else:
            try:
                actual_vals = [int(x) for x in actual.split(",")]
            except ValueError:
                actual_vals = None

        if actual_vals == expected:
            print_test_pass(i, f"{desc}: result {actual_vals} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: result not as expected",
                expected=expected,
                actual=actual_vals if actual_vals is not None else actual,
            )

    total_count += 1
    actual, err, code = run_test_case(exe_path, args=["nullcb"], timeout=2)
    if err == "TIMEOUT":
        print_test_fail(total_count, "cmp=NULL on two non-empty lists: hung (timed out)")
    elif code < 0:
        print_test_fail(
            total_count, "cmp=NULL on two non-empty lists: crashed", actual=f"signal {-code}"
        )
    else:
        print_test_pass(total_count, "cmp=NULL on two non-empty lists: did not crash or hang")
        passed_count += 1

    print_exercise_result("ex17/ft_sorted_list_merge.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
