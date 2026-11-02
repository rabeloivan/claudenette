from .ex00.test_ex00 import run_C_rush01


def get_mapping():
    return {
        "ex00": (
            "rush01",
            run_C_rush01,
            ["write", "malloc", "free"],
            {"allowed_files": ["*.c", "*.h", "*.o", "rush01"]},
        ),
    }
