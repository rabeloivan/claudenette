from .ex00.test_ex00 import run_C07_ex00
from .ex01.test_ex01 import run_C07_ex01
from .ex02.test_ex02 import run_C07_ex02
from .ex03.test_ex03 import run_C07_ex03
from .ex04.test_ex04 import run_C07_ex04
from .ex05.test_ex05 import run_C07_ex05


def get_mapping():
    return {
        "ex00/ft_strdup.c": ("ex00", run_C07_ex00, ["malloc"]),
        "ex01/ft_range.c": ("ex01", run_C07_ex01, ["malloc"]),
        "ex02/ft_ultimate_range.c": ("ex02", run_C07_ex02, ["malloc"]),
        "ex03/ft_strjoin.c": ("ex03", run_C07_ex03, ["malloc"]),
        "ex04/ft_convert_base.c": (
            "ex04",
            run_C07_ex04,
            ["malloc", "free"],
            {"allowed_files": ["ft_convert_base2.c"]},
        ),
        "ex05/ft_split.c": ("ex05", run_C07_ex05, ["malloc"]),
    }
