from .ex00.test_ex00 import run_C09_ex00
from .ex01.test_ex01 import run_C09_ex01
from .ex02.test_ex02 import run_C09_ex02


def get_mapping():
    return {
        "ex00/libft_creator.sh": (
            "ex00",
            run_C09_ex00,
            ["write"],
            {
                "allowed_files": [
                    "ft_putchar.c",
                    "ft_swap.c",
                    "ft_putstr.c",
                    "ft_strlen.c",
                    "ft_strcmp.c",
                ]
            },
        ),
        # "We'll only fetch your Makefile": the Makefile is the whole turn-in, and
        # the test builds it against its own srcs/ and includes/ in a scratch dir.
        "ex01/Makefile": (
            "ex01",
            run_C09_ex01,
            [],
            {"allowed_files": []},
        ),
        "ex02/ft_split.c": ("ex02", run_C09_ex02, ["malloc"]),
    }
