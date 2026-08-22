from .ex00.test_ex00 import run_C13_ex00
from .ex01.test_ex01 import run_C13_ex01
from .ex02.test_ex02 import run_C13_ex02
from .ex03.test_ex03 import run_C13_ex03
from .ex04.test_ex04 import run_C13_ex04
from .ex05.test_ex05 import run_C13_ex05
from .ex06.test_ex06 import run_C13_ex06
from .ex07.test_ex07 import run_C13_ex07


def get_mapping():
    # Every harness here #includes "ft_btree.h" and compiles with
    # -I <student_dir> (verified directly, not assumed - no ft_btree.h
    # fixture exists anywhere under tests/C13/), so a correct submission
    # legitimately includes it alongside the .c file for every exercise,
    # unlike C12 which has one grader-provided-header exception (ex08).
    HEADER = {"allowed_files": ["ft_btree.h"]}
    return {
        "ex00/btree_create_node.c": ("ex00", run_C13_ex00, ["malloc"], HEADER),
        "ex01/btree_apply_prefix.c": ("ex01", run_C13_ex01, [], HEADER),
        "ex02/btree_apply_infix.c": ("ex02", run_C13_ex02, [], HEADER),
        "ex03/btree_apply_suffix.c": ("ex03", run_C13_ex03, [], HEADER),
        "ex04/btree_insert_data.c": ("ex04", run_C13_ex04, ["btree_create_node"], HEADER),
        "ex05/btree_search_item.c": ("ex05", run_C13_ex05, [], HEADER),
        "ex06/btree_level_count.c": ("ex06", run_C13_ex06, [], HEADER),
        "ex07/btree_apply_by_level.c": ("ex07", run_C13_ex07, ["malloc", "free"], HEADER),
    }
