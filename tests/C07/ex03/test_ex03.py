import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    display_str,
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def run_C07_ex03(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex03_harness.c")
    exe_path = "./strjoin"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        (0, [], ", "),
        (1, ["hello"], ", "),
        (3, ["a", "b", "c"], ", "),
        (3, ["a", "b", "c"], ""),
        (2, ["", "b"], "-"),
        (2, ["hello", "world"], " | "),
        (4, ["1", "2", "3", "4"], "+"),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (size, strs, sep) in enumerate(test_cases, 1):
        expected = sep.join(strs)
        input_str = f"{size}\n{sep}\n" + "\n".join(strs)
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_strjoin(size={size}, strs={strs}, sep={display_str(sep)})"

        if actual.startswith("A"):
            content = actual[1:]
            if content == expected:
                print_test_pass(i, f"{desc}: returned {display_str(content)} as expected")
                passed_count += 1
            else:
                print_test_fail(
                    i,
                    f"{desc}: returned value not as expected",
                    expected=expected,
                    actual=content,
                )
        else:
            print_test_fail(
                i, f"{desc}: returned NULL", expected=expected, actual="NULL"
            )

    print_exercise_result("ex03/ft_strjoin.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
