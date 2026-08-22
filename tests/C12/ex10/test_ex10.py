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


def run_C12_ex10(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex10_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./foreach_if"

    flags = ["-Wall", "-Wextra", "-Werror", "-I", student_dir]
    if not compile_source(
        [student_file, harness_path, HARNESS_UTILS], exe_path, flags=flags
    ):
        return False

    print_command_execution(exe_path)

    # (ref, tab)
    test_cases = [
        (2, [1, 2, 3, 2, 1]),
        (99, [1, 2, 3]),
        (1, [1, 1, 1]),
        (5, []),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (ref, tab) in enumerate(test_cases, 1):
        expected = [x for x in tab if x == ref]
        input_str = f"{ref}\n{len(tab)}\n" + ",".join(str(x) for x in tab)
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_list_foreach_if(list of {tab}, data_ref={ref}, cmp=int_eq)"

        actual_vals = None
        if actual == "" and not expected:
            actual_vals = []
        else:
            try:
                actual_vals = [int(x) for x in actual.split(",")]
            except ValueError:
                actual_vals = None

        if actual_vals == expected:
            print_test_pass(i, f"{desc}: call order {actual_vals} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: call order not as expected",
                expected=expected,
                actual=actual_vals if actual_vals is not None else actual,
            )

    total_count += 1
    actual, err, code = run_test_case(exe_path, args=["nullcb"], timeout=2)
    if err == "TIMEOUT":
        print_test_fail(total_count, "f=NULL and cmp=NULL on a non-empty list: hung (timed out)")
    elif code < 0:
        print_test_fail(
            total_count,
            "f=NULL and cmp=NULL on a non-empty list: crashed",
            actual=f"signal {-code}",
        )
    else:
        print_test_pass(
            total_count, "f=NULL and cmp=NULL on a non-empty list: did not crash or hang"
        )
        passed_count += 1

    print_exercise_result("ex10/ft_list_foreach_if.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
