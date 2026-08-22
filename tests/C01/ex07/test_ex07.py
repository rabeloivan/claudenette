import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def run_C01_ex07(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex07_harness.c")
    exe_path = "./rev_int_tab"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        [1, 2, 3, 4, 5],
        [1, 2],
        [42],
        [],
        [-3, 0, 7],
        [5, 5, 5],
        [-1, -2, -3, -4],
        [2147483647, 0, -2147483648],
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, arr in enumerate(test_cases, 1):
        size = len(arr)
        input_str = f"{size} " + " ".join(map(str, arr))
        expected = " ".join(map(str, reversed(arr))) if size > 0 else ""
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_rev_int_tab(tab={arr}, size={size})"

        if actual == expected:
            print_test_pass(i, f"{desc}: tab set to {list(reversed(arr))} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i, f"{desc}: set tab not as expected", expected=expected, actual=actual
            )

    total_count += 1
    actual, err, code = run_test_case(exe_path, args=["null_tab"], timeout=2)
    if err == "TIMEOUT":
        print_test_fail(total_count, "tab=NULL (size=3): hung (timed out)")
    elif code < 0:
        print_test_fail(total_count, "tab=NULL (size=3): crashed", actual=f"signal {-code}")
    else:
        print_test_pass(total_count, "tab=NULL (size=3): did not crash or hang")
        passed_count += 1

    print_exercise_result("ex07/ft_rev_int_tab.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
