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


def run_C12_ex12(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex12_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./remove_if"

    # See test_ex11.py: cmp is prototyped `int (*cmp)()` per the subject,
    # which trips Clang's -Wdeprecated-non-prototype under -Werror.
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
        (2, [1, 2, 3, 2, 1]),
        (99, [1, 2, 3]),
        (1, [1, 1, 1]),
        (5, []),
        (1, [1, 2, 1, 3, 1]),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (ref, tab) in enumerate(test_cases, 1):
        expected_survivors = [x for x in tab if x != ref]
        expected_freed = sorted(x for x in tab if x == ref)
        input_str = f"{ref}\n{len(tab)}\n" + ",".join(str(x) for x in tab)
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_list_remove_if(list of {tab}, data_ref={ref}, cmp=int_eq)"

        # record_free writes (comma-joined) during the call itself, before
        # the harness's own post-call walk prints survivors - so the freed
        # sequence necessarily comes first in program-output order.
        parts = actual.split("\n", 1)
        freed_str = parts[0] if len(parts) >= 1 else ""
        survivors_str = parts[1] if len(parts) >= 2 else ""

        def parse_ints(s, expected_list):
            if s == "" and not expected_list:
                return []
            try:
                return [int(x) for x in s.split(",")]
            except ValueError:
                return None

        actual_survivors = parse_ints(survivors_str, expected_survivors)
        actual_freed = parse_ints(freed_str, expected_freed)
        if actual_freed is not None:
            actual_freed = sorted(actual_freed)

        if actual_survivors == expected_survivors and actual_freed == expected_freed:
            summary = f"survivors={actual_survivors}, freed={actual_freed}"
            print_test_pass(i, f"{desc}: {summary} as expected")
            passed_count += 1
        elif actual_survivors != expected_survivors:
            print_test_fail(
                i, f"{desc}: survivors not as expected", expected=expected_survivors, actual=survivors_str
            )
        else:
            print_test_fail(
                i, f"{desc}: free_fct calls not as expected", expected=expected_freed, actual=freed_str
            )

    total_count += 1
    actual, err, code = run_test_case(exe_path, args=["nullcb"], timeout=2)
    if err == "TIMEOUT":
        print_test_fail(
            total_count, "cmp=NULL and free_fct=NULL on a non-empty list: hung (timed out)"
        )
    elif code < 0:
        print_test_fail(
            total_count,
            "cmp=NULL and free_fct=NULL on a non-empty list: crashed",
            actual=f"signal {-code}",
        )
    else:
        print_test_pass(
            total_count, "cmp=NULL and free_fct=NULL on a non-empty list: did not crash or hang"
        )
        passed_count += 1

    print_exercise_result("ex12/ft_list_remove_if.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
