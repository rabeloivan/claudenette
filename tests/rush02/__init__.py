from .ex00.test_ex00 import run_rush02_ex00


def get_mapping():
    return {
        "ex00/Makefile": (
            "rush02",
            run_rush02_ex00,
            ["write", "malloc", "free", "open", "read", "close"],
            {"allowed_files": ["*.c", "*.h", "*.o", "rush-02", "*.dict"]},
        ),
    }
