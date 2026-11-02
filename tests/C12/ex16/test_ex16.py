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
FT_CREATE_ELEM_REF = os.path.join(C12_DIR, "ft_create_elem_ref.c")
HARNESS_UTILS = os.path.join(C12_DIR, "harness_utils.c")


def run_C12_ex16(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex16_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./sorted_insert"

    # cmp is prototyped `int (*cmp)()` per the subject (K&R unspecified-args
    # style), which trips Clang's -Wdeprecated-non-prototype under -Werror
    # even though the code is subject-compliant.
    flags = [
        "-Wall", "-Wextra", "-Werror", "-Wno-deprecated-non-prototype",
        "-I", student_dir,
    ]
    if not compile_source(
        [student_file, harness_path, FT_CREATE_ELEM_REF, HARNESS_UTILS],
        exe_path,
        flags=flags,
    ):
        return False

    print_command_execution(exe_path)

    # (cmp_selector, new_value, tab) - tab is already sorted per that
    # comparator. Values are kept distinct so the expected result is
    # unambiguous (the subject doesn't specify tie-break placement). The "D"
    # cases only pass if the implementation genuinely delegates to cmp
    # instead of assuming ascending order.
    test_cases = [
        ("A", 3, [1, 2, 4, 5]),
        ("A", 0, [1, 2, 3]),
        ("A", 10, [1, 2, 3]),
        ("A", 5, []),
        ("D", 3, [5, 4, 2, 1]),
        ("D", 9, [5, 4, 2, 1]),
        ("D", 0, [5, 4, 2, 1]),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (sel, new_value, tab) in enumerate(test_cases, 1):
        expected = sorted(tab + [new_value], reverse=(sel == "D"))
        input_str = f"{sel}\n{new_value}\n{len(tab)}\n" + ",".join(str(x) for x in tab)
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        cmp_name = "desc" if sel == "D" else "asc"
        desc = f"ft_sorted_list_insert({new_value} into {tab}, cmp={cmp_name})"

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
        print_test_fail(total_count, "cmp=NULL on a non-empty list: hung (timed out)")
    elif code < 0:
        print_test_fail(
            total_count, "cmp=NULL on a non-empty list: crashed", actual=f"signal {-code}"
        )
    else:
        print_test_pass(total_count, "cmp=NULL on a non-empty list: did not crash or hang")
        passed_count += 1

    print_exercise_result("ex16/ft_sorted_list_insert.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
