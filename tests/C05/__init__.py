from .ex00.test_ex00 import run_C05_ex00
from .ex01.test_ex01 import run_C05_ex01
from .ex02.test_ex02 import run_C05_ex02
from .ex03.test_ex03 import run_C05_ex03
from .ex04.test_ex04 import run_C05_ex04
from .ex05.test_ex05 import run_C05_ex05
from .ex06.test_ex06 import run_C05_ex06
from .ex07.test_ex07 import run_C05_ex07
from .ex08.test_ex08 import run_C05_ex08


def get_mapping():
    return {
        "ex00/ft_iterative_factorial.c": ("ex00", run_C05_ex00, []),
        "ex01/ft_recursive_factorial.c": ("ex01", run_C05_ex01, []),
        "ex02/ft_iterative_power.c": ("ex02", run_C05_ex02, []),
        "ex03/ft_recursive_power.c": ("ex03", run_C05_ex03, []),
        "ex04/ft_fibonacci.c": ("ex04", run_C05_ex04, []),
        "ex05/ft_sqrt.c": ("ex05", run_C05_ex05, []),
        "ex06/ft_is_prime.c": ("ex06", run_C05_ex06, []),
        "ex07/ft_find_next_prime.c": ("ex07", run_C05_ex07, []),
        "ex08/ft_ten_queens_puzzle.c": ("ex08", run_C05_ex08, ["write"]),
    }
