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

# -r--r-xr-x
EXPECTED_MODE = 0o455
EXPECTED_SIZE = 40


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
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    print_exercise_result(student_file, passed, i)
    return passed == i
