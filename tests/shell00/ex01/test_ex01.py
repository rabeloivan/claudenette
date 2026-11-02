import os
import shutil
import tarfile
import tempfile

from utils.ui import (
    display_str,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

from ...shell_utils import ls_date_matches

# -r--r-xr-x
EXPECTED_MODE = 0o455
EXPECTED_SIZE = 40
# "-r--r-xr-x 1 XX XX 40 Jun 1 23:42 testShell00", with "A year will be
# accepted instead of the time in the file's timestamp".
EXPECTED_DATE = "Jun  1 23:42"


def run_shell00_ex01(student_file):
    i = 0
    passed = 0

    def check(condition, description, expected=None, actual=None):
        nonlocal i, passed
        i += 1
        if condition:
            if expected is not None:
                print_test_pass(i, f"{description} {display_str(str(expected))} as expected")
            else:
                print_test_pass(i, f"{description} as expected")
            passed += 1
        else:
            print_test_fail(
                i, f"{description} not as expected", expected=expected, actual=actual
            )

    scratch = tempfile.mkdtemp(prefix="claudenette_shell00_ex01_")
    try:
        try:
            with tarfile.open(student_file) as tf:
                # "fully_trusted": Python's newer default extraction filter
                # (PEP 706) silently strips/alters permission bits on
                # extraction - confirmed empirically (0o715 came back as
                # 0o755). This is a local tool testing the student's own
                # trusted tar, not an untrusted archive from the internet,
                # so exact-bit preservation is what's actually needed here.
                tf.extractall(scratch, filter="fully_trusted")
                # Read from the archive, not the extracted file: tar -xf
                # restores these, and so the evaluator's ls -l shows them.
                mtimes = {os.path.normpath(m.name): m.mtime for m in tf.getmembers()}
            extracted_ok = True
        except Exception as e:
            check(False, "testShell00.tar extracting cleanly", actual=str(e))
            extracted_ok = False

        if extracted_ok:
            target = os.path.join(scratch, "testShell00")
            check(os.path.exists(target), "extracted archive contains a file named 'testShell00'")

            if os.path.exists(target):
                st = os.lstat(target)
                check(
                    not os.path.islink(target) and os.path.isfile(target),
                    "'testShell00' is a regular file (not a symlink or directory)",
                )
                actual_mode = st.st_mode & 0o777
                check(
                    actual_mode == EXPECTED_MODE,
                    "permissions (r--r-xr-x)",
                    expected=oct(EXPECTED_MODE),
                    actual=oct(actual_mode),
                )
                check(
                    st.st_size == EXPECTED_SIZE,
                    "file size",
                    expected=f"{EXPECTED_SIZE} bytes",
                    actual=f"{st.st_size} bytes",
                )
                # The date was never checked, so a testShell00 still
                # stamped with the day it was made scored OK.
                date_ok, shown = ls_date_matches(mtimes["testShell00"], EXPECTED_DATE)
                check(
                    date_ok,
                    "date, as ls -l shows it",
                    expected=f"{EXPECTED_DATE} (or Jun  1 and a year)",
                    actual=shown,
                )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    print_exercise_result(student_file, passed, i)
    return passed == i
