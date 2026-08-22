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


def run_C12_ex13(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex13_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./list_merge"

    flags = ["-Wall", "-Wextra", "-Werror", "-I", student_dir]
    if not compile_source(
        [student_file, harness_path, HARNESS_UTILS], exe_path, flags=flags
    ):
        return False

    print_command_execution(exe_path)

    # (tab1, tab2)
    test_cases = [
        ([1, 2, 3], [4, 5]),
        ([], [1, 2, 3]),
        ([1, 2, 3], []),
        ([], []),
        ([5], [10]),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (tab1, tab2) in enumerate(test_cases, 1):
        expected = tab1 + tab2
        input_str = (
            f"{len(tab1)}\n" + ",".join(str(x) for x in tab1) + "\n"
            f"{len(tab2)}\n" + ",".join(str(x) for x in tab2)
        )
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_list_merge(list1={tab1}, list2={tab2})"

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

    print_exercise_result("ex13/ft_list_merge.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
