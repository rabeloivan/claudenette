import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def run_C01_ex04(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex04_harness.c")
    exe_path = "./ultimate_div_mod"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        (10, 3, "3 1"),
        (42, 10, "4 2"),
        (100, 25, "4 0"),
        (0, 42, "0 0"),
        (-10, 3, "-3 -1"),
        (10, -3, "-3 1"),
        (-45, -7, "6 -3"),
        (2147483647, 10, "214748364 7"),
        (-2147483648, 10, "-214748364 -8"),
        (42, 2147483647, "0 42"),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (a, b, expected) in enumerate(test_cases, 1):
        input_str = f"{a} {b}"
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_ultimate_div_mod(a={a}, b={b})"

        if actual == expected:
            print_test_pass(i, f"{desc}: a and b set to {actual} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: set a and b not as expected",
                expected=expected,
                actual=actual,
            )

    for flag, label in [("null_a", "a=NULL"), ("null_b", "b=NULL")]:
        total_count += 1
        actual, err, code = run_test_case(exe_path, args=[flag], timeout=2)
        if err == "TIMEOUT":
            print_test_fail(total_count, f"{label}: hung (timed out)")
        elif code < 0:
            print_test_fail(total_count, f"{label}: crashed", actual=f"signal {-code}")
        else:
            print_test_pass(total_count, f"{label}: did not crash or hang")
            passed_count += 1

    print_exercise_result("ex04/ft_ultimate_div_mod.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
