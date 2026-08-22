import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def run_C11_ex01(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex01_harness.c")
    exe_path = "./map"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        [1, 2, 3],
        [-5, 0, 5],
        [42],
        [10, -10, 20, -20, 30],
        [],
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, tab in enumerate(test_cases, 1):
        expected_mapped = [x * x for x in tab]
        input_str = f"{len(tab)}\n" + ",".join(str(x) for x in tab)
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_map(tab={tab}, length={len(tab)}, f=square)"

        if not tab:
            # The subject doesn't define length=0 behavior; accept either
            # NULL or a valid-but-empty array as correct.
            if actual == "N" or actual.startswith("A|"):
                print_test_pass(i, f"{desc}: empty-array case handled reasonably")
                passed_count += 1
            else:
                print_test_fail(i, f"{desc}: empty-array case not handled reasonably", actual=actual)
            continue

        if not actual.startswith("A"):
            print_test_fail(i, f"{desc}: returned NULL", expected=expected_mapped, actual="NULL")
            continue

        body = actual[1:]
        if "|" not in body:
            print_test_fail(i, f"{desc}: unparseable output", actual=actual)
            continue

        mapped_str, _, original_str = body.partition("|")
        try:
            actual_mapped = [int(x) for x in mapped_str.split(",")] if mapped_str else []
            actual_original = [int(x) for x in original_str.split(",")] if original_str else []
        except ValueError:
            actual_mapped = actual_original = None

        if actual_mapped == expected_mapped and actual_original == tab:
            print_test_pass(i, f"{desc}: mapped to {actual_mapped} as expected, original tab untouched")
            passed_count += 1
        elif actual_mapped == expected_mapped:
            print_test_fail(
                i,
                f"{desc}: mapped result correct but original tab was modified",
                expected=tab,
                actual=actual_original,
            )
        else:
            print_test_fail(
                i,
                f"{desc}: mapped result not as expected",
                expected=expected_mapped,
                actual=actual_mapped,
            )

    print_exercise_result("ex01/ft_map.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
