from .ex00.test_ex00 import run_C11_ex00
from .ex01.test_ex01 import run_C11_ex01
from .ex02.test_ex02 import run_C11_ex02
from .ex03.test_ex03 import run_C11_ex03
from .ex04.test_ex04 import run_C11_ex04
from .ex05.test_ex05 import run_C11_ex05
from .ex06.test_ex06 import run_C11_ex06
from .ex07.test_ex07 import run_C11_ex07


def get_mapping():
    return {
        "ex00/ft_foreach.c": ("ex00", run_C11_ex00, []),
        "ex01/ft_map.c": ("ex01", run_C11_ex01, ["malloc"]),
        "ex02/ft_any.c": ("ex02", run_C11_ex02, []),
        "ex03/ft_count_if.c": ("ex03", run_C11_ex03, []),
        "ex04/ft_is_sort.c": ("ex04", run_C11_ex04, []),
        "ex05/Makefile": (
            "ex05",
            run_C11_ex05,
            ["write"],
            {"allowed_files": ["*.c", "*.h", "*.o", "do-op"]},
        ),
        "ex06/ft_sort_string_tab.c": ("ex06", run_C11_ex06, []),
        "ex07/ft_advanced_sort_string_tab.c": ("ex07", run_C11_ex07, []),
    }
