import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

FREE_TRACKER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "free_tracker.c",
)


C12_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNESS_UTILS = os.path.join(C12_DIR, "harness_utils.c")


def run_C12_ex00(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex00_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./create_elem"

    flags = ["-Wall", "-Wextra", "-Werror", "-I", student_dir]
    if not compile_source(
        [student_file, harness_path, HARNESS_UTILS, FREE_TRACKER], exe_path, flags=flags
    ):
        return False

    print_command_execution(exe_path)

    test_cases = [42, -17, 0, 1000000]

    passed_count = 0
    total_count = len(test_cases)

    for i, value in enumerate(test_cases, 1):
        actual, err, code = run_test_case(exe_path, input_data=str(value))
        desc = f"ft_create_elem(data={value})"

        if not actual.startswith("A"):
            print_test_fail(
                i, f"{desc}: returned NULL", expected=f"data={value}, next=NULL", actual="NULL"
            )
            continue

        body = actual[1:]
        if "|" not in body:
            print_test_fail(i, f"{desc}: unparseable output", actual=actual)
            continue

        data_str, _, next_str = body.partition("|")
        try:
            actual_data = int(data_str)
        except ValueError:
            actual_data = None

        if actual_data == value and next_str == "1":
            print_test_pass(i, f"{desc}: data={actual_data}, next==NULL as expected")
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: data/next not as expected",
                expected=f"data={value}, next=NULL",
                actual=f"data={actual_data}, next==NULL:{next_str == '1'}",
            )

    print_exercise_result("ex00/ft_create_elem.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
