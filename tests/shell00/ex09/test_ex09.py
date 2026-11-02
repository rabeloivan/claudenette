import shutil
import subprocess
import tempfile

from utils.ui import print_exercise_result, print_test_fail, print_test_pass

# Verified empirically against the real `file` command: a magic file's
# offset field is 0-indexed, so "at the 42nd byte" means 42 bytes of
# anything, then the literal string "42" starting right there.
MATCHING = b"x" * 42 + b"42"
NON_MATCHING_WRONG_OFFSET = b"x" * 41 + b"42" + b"x" * 5
NON_MATCHING_ABSENT = b"y" * 50


def run_shell00_ex09(student_file):
    i = 0
    passed = 0

    def check(condition, description, expected=None, actual=None):
        nonlocal i, passed
        i += 1
        if condition:
            print_test_pass(i, f"{description} as expected")
            passed += 1
        else:
            print_test_fail(
                i, f"{description} not as expected", expected=expected, actual=actual
            )

    scratch = tempfile.mkdtemp(prefix="claudenette_shell00_ex09_")
    try:
        cases = {
            "match.bin": (MATCHING, True),
            "wrong_offset.bin": (NON_MATCHING_WRONG_OFFSET, False),
            "absent.bin": (NON_MATCHING_ABSENT, False),
        }
        for name, (content, should_match) in cases.items():
            path = f"{scratch}/{name}"
            with open(path, "wb") as f:
                f.write(content)

            # file(1) runs the student's magic file, so a hang is theirs: it
            # fails the case - both kinds, since "said nothing" would
            # otherwise pass the two that must NOT report '42 file' - where
            # the TimeoutExpired used to escape as a CRASH blaming claudenette.
            try:
                output = subprocess.run(
                    ["file", "-m", student_file, path],
                    capture_output=True,
                    text=True,
                    timeout=30,
                ).stdout.strip()
            except subprocess.TimeoutExpired:
                output = None
            reports_42 = output is not None and "42 file" in output
            shown = output if output is not None else "no answer within 30s"

            if should_match:
                check(
                    reports_42,
                    f"'{name}' (has '42' at byte 42): detected as '42 file'",
                    actual=shown,
                )
            else:
                check(
                    output is not None and not reports_42,
                    f"'{name}' (does not have '42' at byte 42): NOT detected as '42 file'",
                    actual=shown,
                )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    print_exercise_result(student_file, passed, i)
    return passed == i
