from .ex00.test_ex00 import run_C06_ex00
from .ex01.test_ex01 import run_C06_ex01
from .ex02.test_ex02 import run_C06_ex02
from .ex03.test_ex03 import run_C06_ex03


def get_mapping():
    return {
        "ex00/ft_print_program_name.c": ("ex00", run_C06_ex00, ["write"]),
        "ex01/ft_print_params.c": ("ex01", run_C06_ex01, ["write"]),
        "ex02/ft_rev_params.c": ("ex02", run_C06_ex02, ["write"]),
        "ex03/ft_sort_params.c": ("ex03", run_C06_ex03, ["write"]),
    }
