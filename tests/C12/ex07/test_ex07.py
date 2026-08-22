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


def run_C12_ex07(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex07_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./list_at"

    flags = ["-Wall", "-Wextra", "-Werror", "-I", student_dir]
    if not compile_source(
        [student_file, harness_path, HARNESS_UTILS], exe_path, flags=flags
    ):
        return False

    print_command_execution(exe_path)

    # (nbr, tab)
    test_cases = [
        (0, [10, 20, 30]),
        (1, [10, 20, 30]),
        (2, [10, 20, 30]),
        (3, [10, 20, 30]),
        (0, []),
        (5, [1, 2, 3]),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (nbr, tab) in enumerate(test_cases, 1):
        expected = tab[nbr] if nbr < len(tab) else None
        input_str = f"{nbr}\n{len(tab)}\n" + ",".join(str(x) for x in tab)
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_list_at(list of {tab}, nbr={nbr})"

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

    print_exercise_result("ex07/ft_list_at.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
