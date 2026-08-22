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

EXPECTED = {
    "test0": {"type": "dir", "mode": 0o715},
    "test1": {"type": "file", "mode": 0o714, "size": 4},
    "test2": {"type": "dir", "mode": 0o504},
    "test3": {"type": "file", "mode": 0o404, "size": 1},
    "test4": {"type": "file", "mode": 0o641, "size": 2},
    "test5": {"type": "file", "mode": 0o404, "size": 1},
    "test6": {"type": "symlink", "target": "test0"},
}


def run_shell00_ex02(student_file):
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

    scratch = tempfile.mkdtemp(prefix="claudenette_shell00_ex02_")
    try:
        try:
            with tarfile.open(student_file) as tf:
                # See ex01's identical fix: the default extraction filter
                # silently alters permission bits, confirmed empirically.
                tf.extractall(scratch, filter="fully_trusted")
            extracted_ok = True
        except Exception as e:
            check(False, "exo2.tar extracting cleanly", actual=str(e))
            extracted_ok = False

        if extracted_ok:
            for name, spec in EXPECTED.items():
                path = os.path.join(scratch, name)
                exists = os.path.lexists(path)
                check(exists, f"'{name}' exists after extraction")
                if not exists:
                    continue

                st = os.lstat(path)

                if spec["type"] == "dir":
                    check(os.path.isdir(path) and not os.path.islink(path), f"'{name}' is a directory")
                    mode = st.st_mode & 0o777
                    check(
                        mode == spec["mode"],
                        f"'{name}' permissions",
                        expected=oct(spec["mode"]),
                        actual=oct(mode),
                    )
                elif spec["type"] == "file":
                    check(
                        os.path.isfile(path) and not os.path.islink(path),
                        f"'{name}' is a regular file",
                    )
                    mode = st.st_mode & 0o777
                    check(
                        mode == spec["mode"],
                        f"'{name}' permissions",
                        expected=oct(spec["mode"]),
                        actual=oct(mode),
                    )
                    check(
                        st.st_size == spec["size"],
                        f"'{name}' size",
                        expected=f"{spec['size']} bytes",
                        actual=f"{st.st_size} bytes",
                    )
                elif spec["type"] == "symlink":
                    check(os.path.islink(path), f"'{name}' is a symlink")
                    if os.path.islink(path):
                        target = os.readlink(path)
                        check(
                            target == spec["target"],
                            f"'{name}' symlink target",
                            expected=spec["target"],
                            actual=target,
                        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    print_exercise_result(student_file, passed, i)
    return passed == i
