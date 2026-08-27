from .ex01.test_ex01 import run_shell01_ex01
from .ex02.test_ex02 import run_shell01_ex02
from .ex03.test_ex03 import run_shell01_ex03
from .ex04.test_ex04 import run_shell01_ex04
from .ex05.test_ex05 import FILENAME as EX05_FILENAME
from .ex05.test_ex05 import run_shell01_ex05
from .ex06.test_ex06 import run_shell01_ex06
from .ex07.test_ex07 import run_shell01_ex07
from .ex08.test_ex08 import run_shell01_ex08

SKIP_PRECHECK = {"skip_precheck": True}


def get_mapping():
    return {
        # ex00 ("Exam") has no file to turn in at all - just a reminder to
        # register for the exam event - so it has no mapping entry, unlike
        # shell00's ex07 which had a real (but underspecified) filename.
        "ex01/print_groups.sh": ("print_groups", run_shell01_ex01, [], SKIP_PRECHECK),
        "ex02/find_sh.sh": ("find_sh", run_shell01_ex02, [], SKIP_PRECHECK),
        "ex03/count_files.sh": ("count_files", run_shell01_ex03, [], SKIP_PRECHECK),
        "ex04/MAC.sh": ("MAC", run_shell01_ex04, [], SKIP_PRECHECK),
        "ex05/" + EX05_FILENAME: ("Can you create it?", run_shell01_ex05, [], SKIP_PRECHECK),
        "ex06/skip.sh": ("Skip", run_shell01_ex06, [], SKIP_PRECHECK),
        "ex07/r_dwssap.sh": ("r_dwssap", run_shell01_ex07, [], SKIP_PRECHECK),
        # An earlier attempt searched 24x120x2x2 base orderings and found no
        # decode consistent with either worked example, and left this a TODO.
        # That search was looking for a 4-digit first base (24 = 4!), but the
        # subject's is five digits - '\"?! - and with that reading the first
        # worked example (+ rcrdmddd -> "Salut") reproduces exactly, from the
        # base strings as printed. See tests/shell01/chelou.py, which also
        # records how the *second* example's input had to be recovered: its
        # dense run of escaped quotes really is unreadable from the rendered
        # PDF, and was solved for rather than transcribed.
        "ex08/add_chelou.sh": ("add_chelou", run_shell01_ex08, [], SKIP_PRECHECK),
    }
