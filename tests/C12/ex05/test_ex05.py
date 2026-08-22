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
FT_CREATE_ELEM_REF = os.path.join(C12_DIR, "ft_create_elem_ref.c")
HARNESS_UTILS = os.path.join(C12_DIR, "harness_utils.c")


def run_C12_ex05(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex05_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./push_strs"

    flags = ["-Wall", "-Wextra", "-Werror", "-I", student_dir]
    if not compile_source(
        [student_file, harness_path, FT_CREATE_ELEM_REF, HARNESS_UTILS],
        exe_path,
        flags=flags,
    ):
        return False

    print_command_execution(exe_path)

    test_cases = [
        [],
        ["hello"],
        ["a", "b", "c"],
        ["first", "second", "third", "fourth"],
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, strs in enumerate(test_cases, 1):
        # "the first element should be at the end of the list"
        expected = list(reversed(strs))
        input_str = f"{len(strs)}\n" + "\n".join(strs)
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_list_push_strs(size={len(strs)}, strs={strs})"

        actual_tab = actual.split("\x01") if actual else []

        if actual_tab == expected:
            print_test_pass(i, f"{desc}: resulting list {actual_tab} as expected (first string at the tail)")
            passed_count += 1
        else:
            print_test_fail(i, f"{desc}: resulting list not as expected", expected=expected, actual=actual_tab)

    print_exercise_result("ex05/ft_list_push_strs.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
