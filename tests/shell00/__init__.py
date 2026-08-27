from .ex00.test_ex00 import run_shell00_ex00
from .ex01.test_ex01 import run_shell00_ex01
from .ex02.test_ex02 import run_shell00_ex02
from .ex03.test_ex03 import run_shell00_ex03
from .ex04.test_ex04 import run_shell00_ex04
from .ex05.test_ex05 import run_shell00_ex05
from .ex06.test_ex06 import run_shell00_ex06
from .ex07.test_ex07 import run_shell00_ex07
from .ex08.test_ex08 import run_shell00_ex08
from .ex09.test_ex09 import run_shell00_ex09

# Every shell00 exercise turns in shell content or a raw filesystem
# artifact, never C - norminette and "allowed functions" are both
# C-specific concepts (style rules, nm -u on a compiled object) that real
# moulinette never applies here, so main.py's automatic pre-check is
# skipped outright for all of them rather than left to harmlessly no-op.
SKIP_PRECHECK = {"skip_precheck": True}


def get_mapping():
    return {
        "ex00/z": ("Z", run_shell00_ex00, [], SKIP_PRECHECK),
        "ex01/testShell00.tar": ("testShell00", run_shell00_ex01, [], SKIP_PRECHECK),
        "ex02/exo2.tar": ("exo2", run_shell00_ex02, [], SKIP_PRECHECK),
        "ex03/id_ed25519_pub": ("SSH me!", run_shell00_ex03, [], SKIP_PRECHECK),
        "ex04/midLS": ("midLS", run_shell00_ex04, [], SKIP_PRECHECK),
        "ex05/git_commit.sh": ("GiT commit", run_shell00_ex05, [], SKIP_PRECHECK),
        "ex06/git_ignore.sh": ("gitignore", run_shell00_ex06, [], SKIP_PRECHECK),
        # The subject only says "Create a file named b, so that: diff a b >
        # sw.diff" - b's content is defined entirely by 42's own `a` and
        # `sw.diff`, which the PDF never prints. Those two files now sit in
        # tests/shell00/ex07/fixture/, so the expected b is reconstructed by
        # applying the diff rather than guessed. Without them the test says
        # so plainly instead of failing the student.
        "ex07/b": ("diff", run_shell00_ex07, [], SKIP_PRECHECK),
        "ex08/clean": ("clean", run_shell00_ex08, [], SKIP_PRECHECK),
        "ex09/ft_magic": ("ft_magic", run_shell00_ex09, [], SKIP_PRECHECK),
    }
