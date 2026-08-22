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


def run_C12_ex11(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex11_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./list_find"

    # The subject prototypes cmp as `int (*cmp)()` (K&R unspecified-args
    # style) rather than `int (*cmp)(void *, void *)` - calling through that
    # exact mandated prototype trips Clang's -Wdeprecated-non-prototype under
    # -Werror, even though the code is subject-compliant. Real campus
    # Linux/gcc grading doesn't have this diagnostic at all.
    flags = [
        "-Wall", "-Wextra", "-Werror", "-Wno-deprecated-non-prototype",
        "-I", student_dir,
    ]
    if not compile_source(
        [student_file, harness_path, HARNESS_UTILS], exe_path, flags=flags
    ):
        return False

    print_command_execution(exe_path)

    # (ref, tab)
    test_cases = [
        (2, [1, 2, 3]),
        (99, [1, 2, 3]),
        (5, [5, 5, 5]),
        (1, [3, 1, 1, 2]),
        (1, []),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (ref, tab) in enumerate(test_cases, 1):
        matches = [x for x in tab if x == ref]
        expected = matches[0] if matches else None
        input_str = f"{ref}\n{len(tab)}\n" + ",".join(str(x) for x in tab)
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_list_find(list of {tab}, data_ref={ref}, cmp=int_eq)"

        if expected is None:
            if actual == "N":
                print_test_pass(i, f"{desc}: returned NULL as expected")
                passed_count += 1
            else:
                print_test_fail(i, f"{desc}: expected NULL", expected="NULL", actual=actual)
            continue

        if actual.startswith("A") and actual[1:] == str(expected):
            print_test_pass(i, f"{desc}: returned element data={expected} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: returned element data not as expected",
                expected=f"data={expected}",
                actual=actual,
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

    print_exercise_result("ex11/ft_list_find.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
