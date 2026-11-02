from .ex00.test_ex00 import run_C00_ex00
from .ex01.test_ex01 import run_C00_ex01
from .ex02.test_ex02 import run_C00_ex02
from .ex03.test_ex03 import run_C00_ex03
from .ex04.test_ex04 import run_C00_ex04
from .ex05.test_ex05 import run_C00_ex05
from .ex06.test_ex06 import run_C00_ex06
from .ex07.test_ex07 import run_C00_ex07
from .ex08.test_ex08 import run_C00_ex08


def get_mapping():
    return {
        "ex00/ft_putchar.c": ("ex00", run_C00_ex00, ["write"]),
        "ex01/ft_print_alphabet.c": ("ex01", run_C00_ex01, ["write"]),
        "ex02/ft_print_reverse_alphabet.c": ("ex02", run_C00_ex02, ["write"]),
        "ex03/ft_print_numbers.c": ("ex03", run_C00_ex03, ["write"]),
        "ex04/ft_is_negative.c": ("ex04", run_C00_ex04, ["write"]),
        "ex05/ft_print_comb.c": ("ex05", run_C00_ex05, ["write"]),
        "ex06/ft_print_comb2.c": ("ex06", run_C00_ex06, ["write"]),
        "ex07/ft_putnbr.c": ("ex07", run_C00_ex07, ["write"]),
        "ex08/ft_print_combn.c": ("ex08", run_C00_ex08, ["write"]),
    }
