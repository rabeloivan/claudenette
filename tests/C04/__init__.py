from .ex00.test_ex00 import run_C04_ex00
from .ex01.test_ex01 import run_C04_ex01
from .ex02.test_ex02 import run_C04_ex02
from .ex03.test_ex03 import run_C04_ex03
from .ex04.test_ex04 import run_C04_ex04
from .ex05.test_ex05 import run_C04_ex05


def get_mapping():
    return {
        "ex00/ft_strlen.c": ("ex00", run_C04_ex00, []),
        "ex01/ft_putstr.c": ("ex01", run_C04_ex01, ["write"]),
        "ex02/ft_putnbr.c": ("ex02", run_C04_ex02, ["write"]),
        "ex03/ft_atoi.c": ("ex03", run_C04_ex03, []),
        "ex04/ft_putnbr_base.c": ("ex04", run_C04_ex04, ["write"]),
        "ex05/ft_atoi_base.c": ("ex05", run_C04_ex05, []),
    }
