import os

from .ex00.test_ex00 import run_C12_ex00
from .ex01.test_ex01 import run_C12_ex01
from .ex02.test_ex02 import run_C12_ex02
from .ex03.test_ex03 import run_C12_ex03
from .ex04.test_ex04 import run_C12_ex04
from .ex05.test_ex05 import run_C12_ex05
from .ex06.test_ex06 import run_C12_ex06
from .ex07.test_ex07 import run_C12_ex07
from .ex08.test_ex08 import run_C12_ex08
from .ex09.test_ex09 import run_C12_ex09
from .ex10.test_ex10 import run_C12_ex10
from .ex11.test_ex11 import run_C12_ex11
from .ex12.test_ex12 import run_C12_ex12
from .ex13.test_ex13 import run_C12_ex13
from .ex14.test_ex14 import run_C12_ex14
from .ex15.test_ex15 import run_C12_ex15
from .ex16.test_ex16 import run_C12_ex16
from .ex17.test_ex17 import run_C12_ex17

_DIR = os.path.dirname(os.path.abspath(__file__))


def get_mapping():
    # Every harness here #includes "ft_list.h" and compiles with
    # -I <student_dir> (verified directly, not assumed) - meaning every
    # exercise except ex08 can only resolve that header from the student's
    # own directory, so a correct submission legitimately includes it
    # alongside the .c file. ex08 is the sole documented exception: its
    # subject explicitly omits ft_list.h from "Files to Submit" and this
    # test compiles against its own fixture copy (-I tests/C12/ex08/)
    # instead of the student's directory, so ex08 deliberately keeps the
    # default (no allowed_files override) rather than allowing it too.
    HEADER = {"allowed_files": ["ft_list.h"]}
    return {
        "ex00/ft_create_elem.c": ("ex00", run_C12_ex00, ["malloc"], HEADER),
        "ex01/ft_list_push_front.c": ("ex01", run_C12_ex01, ["ft_create_elem"], HEADER),
        "ex02/ft_list_size.c": ("ex02", run_C12_ex02, [], HEADER),
        "ex03/ft_list_last.c": ("ex03", run_C12_ex03, [], HEADER),
        "ex04/ft_list_push_back.c": ("ex04", run_C12_ex04, ["ft_create_elem"], HEADER),
        "ex05/ft_list_push_strs.c": ("ex05", run_C12_ex05, ["ft_create_elem"], HEADER),
        "ex06/ft_list_clear.c": ("ex06", run_C12_ex06, ["free"], HEADER),
        "ex07/ft_list_at.c": ("ex07", run_C12_ex07, [], HEADER),
        "ex08/ft_list_reverse.c": (
            "ex08",
            run_C12_ex08,
            [],
            {"compile_flags": ["-I", os.path.join(_DIR, "ex08")]},
        ),
        "ex09/ft_list_foreach.c": ("ex09", run_C12_ex09, [], HEADER),
        "ex10/ft_list_foreach_if.c": ("ex10", run_C12_ex10, [], HEADER),
        "ex11/ft_list_find.c": ("ex11", run_C12_ex11, [], HEADER),
        "ex12/ft_list_remove_if.c": ("ex12", run_C12_ex12, ["free"], HEADER),
        "ex13/ft_list_merge.c": ("ex13", run_C12_ex13, [], HEADER),
        "ex14/ft_list_sort.c": ("ex14", run_C12_ex14, [], HEADER),
        "ex15/ft_list_reverse_fun.c": ("ex15", run_C12_ex15, [], HEADER),
        "ex16/ft_sorted_list_insert.c": ("ex16", run_C12_ex16, ["ft_create_elem"], HEADER),
        "ex17/ft_sorted_list_merge.c": ("ex17", run_C12_ex17, [], HEADER),
    }
