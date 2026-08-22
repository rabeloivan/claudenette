from .ex00.test_ex00 import run_C10_ex00
from .ex01.test_ex01 import run_C10_ex01
from .ex02.test_ex02 import run_C10_ex02
from .ex03.test_ex03 import run_C10_ex03


def get_mapping():
    return {
        "ex00/Makefile": (
            "ex00",
            run_C10_ex00,
            ["close", "open", "read", "write"],
            {"allowed_files": ["*.c", "*.h", "*.o", "ft_display_file"]},
        ),
        "ex01/Makefile": (
            "ex01",
            run_C10_ex01,
            ["close", "open", "read", "write", "strerror", "basename"],
            {"allowed_files": ["*.c", "*.h", "*.o", "ft_cat"]},
        ),
        "ex02/Makefile": (
            "ex02",
            run_C10_ex02,
            ["close", "open", "read", "write", "malloc", "free", "strerror", "basename"],
            {"allowed_files": ["*.c", "*.h", "*.o", "ft_tail"]},
        ),
        "ex03/Makefile": (
            "ex03",
            run_C10_ex03,
            ["close", "open", "read", "write", "malloc", "free", "strerror", "basename"],
            {"allowed_files": ["*.c", "*.h", "*.o", "ft_hexdump"]},
        ),
    }
