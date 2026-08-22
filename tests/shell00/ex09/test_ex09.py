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

            result = subprocess.run(
                ["file", "-m", student_file, path],
                capture_output=True,
                text=True,
                timeout=5,
            )
            reports_42 = "42 file" in result.stdout

            if should_match:
                check(
                    reports_42,
                    f"'{name}' (has '42' at byte 42): detected as '42 file'",
                    actual=result.stdout.strip(),
                )
            else:
                check(
                    not reports_42,
                    f"'{name}' (does not have '42' at byte 42): NOT detected as '42 file'",
                    actual=result.stdout.strip(),
                )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    print_exercise_result(student_file, passed, i)
    return passed == i
