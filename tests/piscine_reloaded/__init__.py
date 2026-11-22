"""Piscine Reloaded 2.2: a best-of of the Piscine, graded with the Piscine's own tests.

Each entry names the Piscine module its test comes from (`source_module`), so the
presentation and the NULL, boundary and memory campaigns are the ones that module
already applies.
"""
from pathlib import Path

from tests.C00.ex01.test_ex01 import run_C00_ex01
from tests.C00.ex03.test_ex03 import run_C00_ex03
from tests.C00.ex04.test_ex04 import run_C00_ex04
from tests.C01.ex00.test_ex00 import run_C01_ex00
from tests.C01.ex02.test_ex02 import run_C01_ex02
from tests.C01.ex03.test_ex03 import run_C01_ex03
from tests.C01.ex05.test_ex05 import run_C01_ex05
from tests.C01.ex06.test_ex06 import run_C01_ex06
from tests.C03.ex00.test_ex00 import run_C03_ex00
from tests.C05.ex00.test_ex00 import run_C05_ex00
from tests.C05.ex01.test_ex01 import run_C05_ex01
from tests.C05.ex05.test_ex05 import run_C05_ex05
from tests.C06.ex01.test_ex01 import run_C06_ex01
from tests.C06.ex03.test_ex03 import run_C06_ex03
from tests.C07.ex00.test_ex00 import run_C07_ex00
from tests.C07.ex01.test_ex01 import run_C07_ex01
from tests.C08.ex02.test_ex02 import run_C08_ex02
from tests.C08.ex03.test_ex03 import run_C08_ex03
from tests.C09.ex01.test_ex01 import run_C09_ex01
from tests.C10.ex00.test_ex00 import run_C10_ex00
from tests.C11.ex00.test_ex00 import run_C11_ex00
from tests.shell00.ex00.test_ex00 import run_shell00_ex00
from tests.shell00.ex02.test_ex02 import run_shell00_ex02
from tests.shell00.ex08.test_ex08 import run_shell00_ex08
from tests.shell01.ex02.test_ex02 import run_shell01_ex02
from tests.shell01.ex04.test_ex04 import run_shell01_ex04
from tests.shell01.ex05.test_ex05 import FILENAME as MARVIN, run_shell01_ex05
from .ex26.test_ex26 import run_reloaded_ex26

# "If ft_putchar() is an authorized function, we will compile your code with our
# ft_putchar.c": the student neither submits it nor may call write directly.
REFERENCE_PUTCHAR = Path(__file__).resolve().parent / 'ft_putchar.c'


def _from(runner, **options):
    """Options for a reused Piscine test: its module and exercise come from its runner."""
    module, exercise = runner.__name__.split('_')[1:3]
    return {'source_module': module, 'source_exercise': exercise, **options}


def _putchar(runner):
    return _from(runner, link_sources=[REFERENCE_PUTCHAR])


def _shell(source):
    return {'skip_precheck': True, 'source_module': source}


def run_reloaded_ex16(student_file):
    # "Reproduce the behavior of the function strlen (man strlen)": NULL is
    # outside that domain, unlike C01's self-defined ft_strlen.
    return run_C01_ex06(student_file, null_probe=False)


# Reloaded asks for 0 on "an error" and, unlike C05, never excuses overflow.
def run_reloaded_ex12(student_file):
    return run_C05_ex00(student_file, overflow_is_error=True)


def run_reloaded_ex13(student_file):
    return run_C05_ex01(student_file, overflow_is_error=True)


def get_mapping():
    return {
        'ex00/exo.tar': ('ex00', run_shell00_ex02, [], _shell('shell00')),
        'ex01/z': ('ex01', run_shell00_ex00, [], _shell('shell00')),
        'ex02/clean': ('ex02', run_shell00_ex08, [], _shell('shell00')),
        'ex03/find_sh.sh': ('ex03', run_shell01_ex02, [], _shell('shell01')),
        'ex04/MAC.sh': ('ex04', run_shell01_ex04, [], _shell('shell01')),
        'ex05/' + MARVIN: ('ex05', run_shell01_ex05, [], _shell('shell01')),
        'ex06/ft_print_alphabet.c': ('ex06', run_C00_ex01, ['ft_putchar'], _putchar(run_C00_ex01)),
        'ex07/ft_print_numbers.c': ('ex07', run_C00_ex03, ['ft_putchar'], _putchar(run_C00_ex03)),
        'ex08/ft_is_negative.c': ('ex08', run_C00_ex04, ['ft_putchar'], _putchar(run_C00_ex04)),
        'ex09/ft_ft.c': ('ex09', run_C01_ex00, [], _from(run_C01_ex00)),
        'ex10/ft_swap.c': ('ex10', run_C01_ex02, [], _from(run_C01_ex02)),
        'ex11/ft_div_mod.c': ('ex11', run_C01_ex03, [], _from(run_C01_ex03)),
        'ex12/ft_iterative_factorial.c': ('ex12', run_reloaded_ex12, [], _from(run_C05_ex00)),
        'ex13/ft_recursive_factorial.c': ('ex13', run_reloaded_ex13, [], _from(run_C05_ex01)),
        'ex14/ft_sqrt.c': ('ex14', run_C05_ex05, [], _from(run_C05_ex05)),
        'ex15/ft_putstr.c': ('ex15', run_C01_ex05, ['ft_putchar'], _putchar(run_C01_ex05)),
        'ex16/ft_strlen.c': ('ex16', run_reloaded_ex16, [], _from(run_C01_ex06)),
        'ex17/ft_strcmp.c': ('ex17', run_C03_ex00, [], _from(run_C03_ex00)),
        'ex18/ft_print_params.c': ('ex18', run_C06_ex01, ['ft_putchar'], _putchar(run_C06_ex01)),
        'ex19/ft_sort_params.c': ('ex19', run_C06_ex03, ['ft_putchar'], _putchar(run_C06_ex03)),
        'ex20/ft_strdup.c': ('ex20', run_C07_ex00, ['malloc'], _from(run_C07_ex00)),
        'ex21/ft_range.c': ('ex21', run_C07_ex01, ['malloc'], _from(run_C07_ex01)),
        'ex22/ft_abs.h': ('ex22', run_C08_ex02, [],
                          _from(run_C08_ex02, norm_rules=['CheckDefine'])),
        'ex23/ft_point.h': ('ex23', run_C08_ex03, [], _from(run_C08_ex03)),
        'ex24/Makefile': ('ex24', run_C09_ex01, [], _from(run_C09_ex01, allowed_files=[])),
        'ex25/ft_foreach.c': ('ex25', run_C11_ex00, [], _from(run_C11_ex00)),
        # Its own prototype, so its NULL campaign is Reloaded's, not C11's.
        'ex26/ft_count_if.c': ('ex26', run_reloaded_ex26, [], {'source_module': 'piscine_reloaded'}),
        'ex27/Makefile': ('ex27', run_C10_ex00, ['close', 'open', 'read', 'write'],
                          _from(run_C10_ex00, allowed_files=['*.c', '*.h'],
                                presentation_name='ft_display_file')),
    }
