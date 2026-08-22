from .ex00.test_ex00 import run_C03_ex00
from .ex01.test_ex01 import run_C03_ex01
from .ex02.test_ex02 import run_C03_ex02
from .ex03.test_ex03 import run_C03_ex03
from .ex04.test_ex04 import run_C03_ex04
from .ex05.test_ex05 import run_C03_ex05


def get_mapping():
    return {
        "ex00/ft_strcmp.c": ("ex00", run_C03_ex00, []),
        "ex01/ft_strncmp.c": ("ex01", run_C03_ex01, []),
        "ex02/ft_strcat.c": ("ex02", run_C03_ex02, []),
        "ex03/ft_strncat.c": ("ex03", run_C03_ex03, []),
        "ex04/ft_strstr.c": ("ex04", run_C03_ex04, []),
        "ex05/ft_strlcat.c": ("ex05", run_C03_ex05, []),
    }
