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

FREE_TRACKER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "free_tracker.c",
)


def run_C08_ex04(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex04_harness.c")
    exe_path = "./strs_to_tab"

    flags = ["-Wall", "-Wextra", "-Werror", "-I", test_dir]
    if not compile_source([student_file, harness_path, FREE_TRACKER], exe_path, flags=flags):
        return False

    print_command_execution(exe_path)

    test_cases = [
        [],
        ["hello"],
        ["a", "b", "c"],
        ["hello", "world", "foo", "bar"],
        [""],
        ["42", "is", "the", "answer"],
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, strs in enumerate(test_cases, 1):
        ac = len(strs)
        input_str = f"{ac}\n" + "\n".join(strs)
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_strs_to_tab(ac={ac}, av={strs})"

        if not actual.startswith("A"):
            print_test_fail(
                i,
                f"{desc}: returned NULL",
                expected="a valid table",
                actual="NULL",
            )
            continue

        body = actual[1:]
        records = body.split("\x02")
        term_flag = records[-1] if len(records) == ac + 1 else None
        records = records[:ac]

        ok = len(records) == ac and term_flag == "1"
        details = []
        if ok:
            for j, (record, expected_str) in enumerate(zip(records, strs)):
                fields = record.split("\x01")
                if len(fields) != 4:
                    ok = False
                    details.append(f"element {j}: unparseable record {display_str(record)}")
                    continue
                size_str, str_content, copy_content, same_ptr = fields
                if (
                    size_str != str(len(expected_str))
                    or str_content != expected_str
                    or copy_content != expected_str
                    or same_ptr != "0"
                ):
                    ok = False
                    details.append(
                        f"element {j}: size={size_str}, str={display_str(str_content)}, "
                        f"copy={display_str(copy_content)}, str==copy ptr:{same_ptr == '1'} "
                        f"(expected size={len(expected_str)}, str/copy={display_str(expected_str)}, "
                        f"str==copy ptr:False)"
                    )

        if ok:
            print_test_pass(i, f"{desc}: table content and termination as expected")
            passed_count += 1
        else:
            if term_flag != "1" and len(records) == ac:
                details.append("terminator element's str was not NULL")
            print_test_fail(
                i,
                f"{desc}: table not as expected"
                + ("" if not details else " - " + "; ".join(details)),
            )

    print_exercise_result("ex04/ft_strs_to_tab.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
