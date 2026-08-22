import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def run_C11_ex00(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex00_harness.c")
    exe_path = "./foreach"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        [],
        [42],
        [1, 2, 3, 4, 5],
        [-5, 0, 5, -10, 10],
        [7, 7, 7],
        list(range(-20, 20)),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, tab in enumerate(test_cases, 1):
        expected = list(tab)
        input_str = f"{len(tab)}\n" + ",".join(str(x) for x in tab)
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_foreach(tab={tab}, length={len(tab)}, f=record)"

        actual_vals = None
        if actual == "" and not expected:
            actual_vals = []
        else:
            try:
                actual_vals = [int(x) for x in actual.split(",")]
            except ValueError:
                actual_vals = None

        if actual_vals == expected:
            print_test_pass(i, f"{desc}: call order as expected")
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: call order not as expected",
                expected=expected,
                actual=actual_vals if actual_vals is not None else actual,
            )

    print_exercise_result("ex00/ft_foreach.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
