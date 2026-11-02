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

# Everything the subject's `ls -l` output fixes: type, permissions, link
# count, size (except a directory's) and date - "A year will be accepted
# instead of the time in the file's timestamp".
EXPECTED = {
    "test0": {"type": "dir", "mode": 0o715, "links": 2, "date": "Jun  1 20:47"},
    "test1": {"type": "file", "mode": 0o714, "size": 4, "links": 1, "date": "Jun  1 21:46"},
    "test2": {"type": "dir", "mode": 0o504, "links": 2, "date": "Jun  1 22:45"},
    "test3": {"type": "file", "mode": 0o404, "size": 1, "links": 2, "date": "Jun  1 23:44"},
    "test4": {"type": "file", "mode": 0o641, "size": 2, "links": 1, "date": "Jun  1 23:43"},
    "test5": {"type": "file", "mode": 0o404, "size": 1, "links": 2, "date": "Jun  1 23:44"},
    "test6": {"type": "symlink", "target": "test0", "links": 1, "date": "Jun  1 22:20"},
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
                # Dates come from the archive: tarfile never restores a
                # symlink's own mtime on extraction, while tar -xf - what
                # the evaluator runs before ls -l - does.
                mtimes = {os.path.normpath(m.name): m.mtime for m in tf.getmembers()}
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

                # Link counts and dates were never checked: a test5 copied
                # from test3 instead of linked to it, and an archive of
                # files still dated the day they were made, both scored OK.
                check(
                    st.st_nlink == spec["links"],
                    f"'{name}' link count",
                    expected=spec["links"],
                    actual=st.st_nlink,
                )
                date_ok, shown = ls_date_matches(mtimes.get(name, 0), spec["date"])
                check(
                    date_ok,
                    f"'{name}' date, as ls -l shows it",
                    expected=f"{spec['date']} (or Jun  1 and a year)",
                    actual=shown,
                )

            # Two links each is only half of it: they must be each other's.
            test3 = os.path.join(scratch, "test3")
            test5 = os.path.join(scratch, "test5")
            if os.path.isfile(test3) and os.path.isfile(test5):
                check(
                    os.stat(test3).st_ino == os.stat(test5).st_ino,
                    "'test3' and 'test5' are hard links to one file",
                )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    print_exercise_result(student_file, passed, i)
    return passed == i
