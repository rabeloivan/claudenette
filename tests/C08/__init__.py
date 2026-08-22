import os

from .ex00.test_ex00 import run_C08_ex00
from .ex01.test_ex01 import run_C08_ex01
from .ex02.test_ex02 import run_C08_ex02
from .ex03.test_ex03 import run_C08_ex03
from .ex04.test_ex04 import run_C08_ex04
from .ex05.test_ex05 import run_C08_ex05

_DIR = os.path.dirname(os.path.abspath(__file__))


def get_mapping():
    return {
        "ex00/ft.h": ("ex00", run_C08_ex00, []),
        "ex01/ft_boolean.h": (
            "ex01", run_C08_ex01, [], {"norm_rules": ["CheckDefine"]}
        ),
        "ex02/ft_abs.h": (
            "ex02", run_C08_ex02, [], {"norm_rules": ["CheckDefine"]}
        ),
        "ex03/ft_point.h": ("ex03", run_C08_ex03, []),
        "ex04/ft_strs_to_tab.c": (
            "ex04",
            run_C08_ex04,
            ["malloc", "free"],
            {"compile_flags": ["-I", os.path.join(_DIR, "ex04")]},
        ),
        "ex05/ft_show_tab.c": (
            "ex05",
            run_C08_ex05,
            ["write"],
            {"compile_flags": ["-I", os.path.join(_DIR, "ex05")]},
        ),
    }
