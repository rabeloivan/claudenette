import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def run_C11_ex04(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex04_harness.c")
    exe_path = "./is_sort"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    # (tab, cmp_type, expected) - cmp_type 0=ascending, 1=descending
    test_cases = [
        ([1, 2, 3, 4, 5], 0, 1),
        ([5, 3, 1, 4, 2], 0, 0),
        ([5, 4, 3, 2, 1], 0, 0),
        ([5, 4, 3, 2, 1], 1, 1),
        ([1, 2, 3, 4, 5], 1, 0),
        ([3, 3, 3, 3], 0, 1),
        ([1, 2, 2, 3, 3, 4], 0, 1),
        ([42], 0, 1),
        ([], 0, 1),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (tab, cmp_type, expected) in enumerate(test_cases, 1):
        cmp_name = "ascending" if cmp_type == 0 else "descending"
        input_str = f"{cmp_type}\n{len(tab)}\n" + ",".join(str(x) for x in tab)
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_is_sort(tab={tab}, length={len(tab)}, f={cmp_name})"

        try:
            actual_val = int(actual)
        except ValueError:
            actual_val = None

        if actual_val == expected:
            print_test_pass(i, f"{desc}: returned {actual_val} as expected")
            passed_count += 1
        else:
            print_test_fail(i, f"{desc}: return value not as expected", expected=expected, actual=actual)

    print_exercise_result("ex04/ft_is_sort.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
