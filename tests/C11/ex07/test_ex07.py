import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def run_C11_ex07(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex07_harness.c")
    exe_path = "./advanced_sort_string_tab"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    # (tab, cmp_type) - cmp_type 0=ascending, 1=descending
    test_cases = [
        (["banana", "apple", "cherry"], 0),
        (["banana", "apple", "cherry"], 1),
        (["ab", "a", "abc"], 0),
        (["ab", "a", "abc"], 1),
        (["same", "same", "same"], 0),
        (["single"], 1),
        (["z", "y", "x", "w", "v"], 0),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (tab, cmp_type) in enumerate(test_cases, 1):
        cmp_name = "ascending" if cmp_type == 0 else "descending"
        expected = sorted(tab, reverse=(cmp_type == 1))
        input_str = f"{cmp_type}\n{len(tab)}\n" + "\n".join(tab)
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_advanced_sort_string_tab(tab={tab}, cmp={cmp_name})"

        actual_tab = actual.split("\x01") if actual else []

        if actual_tab == expected:
            print_test_pass(i, f"{desc}: sorted to {actual_tab} as expected")
            passed_count += 1
        else:
            print_test_fail(i, f"{desc}: sorted result not as expected", expected=expected, actual=actual_tab)

    print_exercise_result("ex07/ft_advanced_sort_string_tab.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
