import os

from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

# a.txt and sw.diff are 42's own resources for this exercise, and are the one
# piece of 42 material this repo deliberately ships (the subject PDFs are
# gitignored). Without them `b` has no defined content at all - the subject
# only says "create b so that diff a b > sw.diff" and never prints sw.diff -
# so the grader reads them on every run rather than using them as reference
# documentation. See README.md's "Subjects" section.
FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixture")
A_PATH = os.path.join(FIXTURE_DIR, "a.txt")
DIFF_PATH = os.path.join(FIXTURE_DIR, "sw.diff")


def apply_normal_diff(a_lines, diff_lines):
    """Rebuild `b` from `a` and a normal-format (not unified) diff.

    Implemented here rather than shelling out to patch(1) so the exercise has no
    tool dependency beyond what the grader already requires - and so the result
    is deterministic rather than subject to patch's fuzz/offset heuristics.

    Normal diff commands, all 1-indexed and referring to the ORIGINAL file on the
    left of the letter and the NEW file on the right:
        <r>a<r>   append the following '>' lines after that line of a
        <r>d<r>   delete those lines of a
        <r>c<r>   replace those lines of a with the following '>' lines
    where <r> is either `N` or `N,M`.
    """
    def parse_range(text):
        if "," in text:
            start, end = text.split(",", 1)
            return int(start), int(end)
        n = int(text)
        return n, n

    edits = []
    i = 0
    while i < len(diff_lines):
        line = diff_lines[i]
        op_at = None
        for k, ch in enumerate(line):
            if ch in "acd":
                op_at = k
                break
        if op_at is None or not line[:op_at]:
            i += 1
            continue

        op = line[op_at]
        a_start, a_end = parse_range(line[:op_at])
        i += 1

        added = []
        while i < len(diff_lines):
            nxt = diff_lines[i]
            if nxt.startswith("< ") or nxt == "<":
                i += 1
            elif nxt == "---":
                i += 1
            elif nxt.startswith("> "):
                added.append(nxt[2:])
                i += 1
            elif nxt == ">":
                added.append("")
                i += 1
            else:
                break
        edits.append((op, a_start, a_end, added))

    # Apply back-to-front so earlier edits don't shift later line numbers.
    out = list(a_lines)
    for op, a_start, a_end, added in reversed(edits):
        if op == "a":
            out[a_start:a_start] = added
        elif op == "d":
            del out[a_start - 1:a_end]
        elif op == "c":
            out[a_start - 1:a_end] = added
    return out


def run_shell00_ex07(student_file):
    if not os.path.exists(A_PATH) or not os.path.exists(DIFF_PATH):
        print_test_fail(
            1,
            "claudenette is missing its own reference files for this exercise "
            "(tests/shell00/ex07/fixture/{a.txt,sw.diff}) - this is a grader "
            "problem, not a problem with your submission",
        )
        print_exercise_result("ex07/b", 0, 1)
        return False

    with open(A_PATH, newline="") as fh:
        a_lines = fh.read().split("\n")
    with open(DIFF_PATH, newline="") as fh:
        diff_lines = fh.read().split("\n")

    expected = apply_normal_diff(a_lines, diff_lines)

    print_command_execution("diff a b  (compared against the subject's sw.diff)")

    with open(student_file, newline="") as fh:
        actual = fh.read().split("\n")

    passed = 0
    total = 2

    # 1. Line count. Reported separately because "your file has 9 lines, it
    #    should have 11" is far more actionable than the first differing line
    #    when a whole block is missing.
    if len(actual) == len(expected):
        print_test_pass(1, f"b has {len(expected)} lines as expected")
        passed += 1
    else:
        print_test_fail(
            1,
            "b does not have the expected number of lines",
            expected=f"{len(expected)} lines",
            actual=f"{len(actual)} lines",
        )

    # 2. Content, first difference reported precisely. Trailing whitespace
    #    matters here: sw.diff's second replacement line genuinely ends in a
    #    space, and `diff a b` would not match without it.
    first_bad = None
    for n, (want, got) in enumerate(zip(expected, actual), 1):
        if want != got:
            first_bad = (n, want, got)
            break

    if first_bad is None and len(actual) == len(expected):
        print_test_pass(2, "b matches the file sw.diff describes, byte for byte")
        passed += 1
    elif first_bad is None:
        print_test_fail(
            2,
            "b matches as far as it goes but is the wrong length",
            expected=f"{len(expected)} lines",
            actual=f"{len(actual)} lines",
        )
    else:
        n, want, got = first_bad
        print_test_fail(
            2,
            f"b differs from what sw.diff describes, first at line {n}",
            expected=want,
            actual=got,
        )

    print_exercise_result("ex07/b", passed, total)
    return passed == total
