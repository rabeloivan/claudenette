from .ex00.test_ex00 import run_C_bsq


def get_mapping():
    return {
        # Unlike rush00/rush01, the subject's own table has no "Turn-in
        # directory" row at all - files sit at the project root, not in an
        # ex00/ subdirectory. "." is the current directory itself, a valid
        # relative path main.py's existence check and run_func both handle
        # the same as any other mapping value.
        ".": (
            "bsq",
            run_C_bsq,
            ["open", "close", "read", "write", "malloc", "free", "exit"],
            {"allowed_files": ["Makefile", "*.c", "*.h", "*.o", "bsq"]},
        ),
    }
