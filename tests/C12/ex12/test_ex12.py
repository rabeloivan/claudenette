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
FREE_TRACKER = os.path.join(os.path.dirname(C12_DIR), "free_tracker.c")


def check_node_disposition(nodes_str, tab, ref):
    # nodes_str: "nodes:1=0,2=1,3=0" - value=times_that_link_was_freed, in
    # original list order. The subject's "the link is freed" obligation is
    # per-link: a link whose data matched data_ref must be freed exactly
    # once, and a link that stayed in the list must never be freed (that
    # would be a use-after-free, the opposite bug from leaking).
    #
    # Returns None when everything is right, otherwise (description, kwargs
    # for print_test_fail).
    nodes_str = nodes_str.strip()
    if not nodes_str.startswith("nodes:"):
        return (
            "could not read the harness's link-tracking line",
            {"expected": "nodes:<val>=<freed>,...", "actual": nodes_str},
        )

    body = nodes_str[len("nodes:") :]
    entries = []
    if body:
        for field in body.split(","):
            val, sep, times = field.partition("=")
            try:
                entries.append((int(val), int(times)))
            except ValueError:
                return (
                    "could not read the harness's link-tracking line",
                    {"expected": "nodes:<val>=<freed>,...", "actual": nodes_str},
                )

    if [v for v, _ in entries] != list(tab):
        return (
            "harness link snapshot didn't match the input list",
            {"expected": list(tab), "actual": [v for v, _ in entries]},
        )

    leaked = [v for v, times in entries if v == ref and times == 0]
    doubled = [v for v, times in entries if v == ref and times > 1]
    wrongly_freed = [v for v, times in entries if v != ref and times > 0]

    if leaked:
        return (
            f"removed {len(leaked)} matching element(s) but never freed their link(s)",
            {
                "expected": f"all {tab.count(ref)} matching link(s) freed",
                "actual": f"{len(leaked)} leaked",
            },
        )
    if doubled:
        return (
            f"freed {len(doubled)} removed link(s) more than once",
            {"expected": "each removed link freed exactly once", "actual": f"{len(doubled)} double-freed"},
        )
    if wrongly_freed:
        return (
            f"freed {len(wrongly_freed)} link(s) that should have stayed in the list",
            {"expected": "links kept in the list are not freed", "actual": f"freed {wrongly_freed}"},
        )
    return None


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
        [student_file, harness_path, HARNESS_UTILS, FREE_TRACKER], exe_path, flags=flags
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
        # sequence necessarily comes first in program-output order. The
        # third line is the free tracker's per-link disposition.
        parts = actual.split("\n")
        freed_str = parts[0] if len(parts) >= 1 else ""
        survivors_str = parts[1] if len(parts) >= 2 else ""
        nodes_str = parts[2] if len(parts) >= 3 else ""
        node_problem = check_node_disposition(nodes_str, tab, ref)

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

        if actual_survivors != expected_survivors:
            print_test_fail(
                i, f"{desc}: survivors not as expected", expected=expected_survivors, actual=survivors_str
            )
        elif actual_freed != expected_freed:
            print_test_fail(
                i, f"{desc}: free_fct calls not as expected", expected=expected_freed, actual=freed_str
            )
        elif node_problem is not None:
            print_test_fail(i, f"{desc}: {node_problem[0]}", **node_problem[1])
        else:
            summary = f"survivors={actual_survivors}, freed={actual_freed}"
            print_test_pass(i, f"{desc}: {summary}, removed links freed as expected")
            passed_count += 1

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
