"""Shared OOM and ownership checks for Piscine constructors."""
from pathlib import Path
import tempfile

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import print_exercise_result, print_test_pass, print_test_fail

ROOT = Path(__file__).resolve().parent
# C07/ex05 and C09/ex02 permit only malloc, and specify neither per-word
# freeability nor partial-allocation cleanup. Their behavior harnesses still
# check contents, NULL termination, source preservation and redzones.
CASES = {
    ('C07', 'ft_strdup'): 'DUP', ('C07', 'ft_range'): 'RANGE',
    ('C07', 'ft_ultimate_range'): 'ULTIMATE', ('C07', 'ft_strjoin'): 'JOIN',
    ('C07', 'ft_convert_base'): 'CONVERT',
    ('C08', 'ft_strs_to_tab'): 'STOCK',
    ('C11', 'ft_map'): 'MAP', ('C12', 'ft_create_elem'): 'NODE',
    ('C12', 'ft_list_push_front'): 'FRONT', ('C12', 'ft_list_push_back'): 'BACK',
    ('C12', 'ft_list_push_strs'): 'LIST', ('C13', 'btree_create_node'): 'TREE',
    ('C13', 'btree_insert_data'): 'INSERT',
}


def run_memory_contracts(module, student_file, options=None):
    name = Path(student_file).stem
    selector = CASES.get((module, name))
    if selector is None:
        return True
    options = options or {}
    sources = [str(Path(student_file).resolve()), str(ROOT/'piscine_allocation_harness.c'),
               str(ROOT/'free_tracker.c')]
    flags = ['-Wall', '-Wextra', '-Werror', '-I', str(Path(student_file).resolve().parent),
             '-DTEST_' + selector] + options.get('compile_flags', [])
    if selector in ('FRONT', 'BACK', 'LIST'):
        sources.append(str(ROOT/'C12/ft_create_elem_ref.c'))
    if selector == 'INSERT':
        sources.append(str(ROOT/'C13/btree_create_node_ref.c'))
    if selector == 'CONVERT':
        sources += [str(p.resolve()) for p in Path(student_file).parent.glob('*.c')
                    if p.resolve() != Path(student_file).resolve()]
    with tempfile.TemporaryDirectory(prefix='claudenette-memory-') as directory:
        exe = str(Path(directory)/'allocation_contract')
        if not compile_source(sources, exe, flags=flags):
            print_exercise_result(name + ' allocation safety', 0, 1)
            return False
        actual, err, code = run_test_case(exe)
        ok = code == 0 and actual == 'OK'
        if ok:
            print_test_pass(1, 'handles each malloc failure; returned memory can be freed without leaks')
        else:
            print_test_fail(1, 'allocation failure/ownership contract', expected='OK',
                            actual=actual or err or f'exit {code}')
        print_exercise_result(name + ' allocation safety', int(ok), 1)
        return ok
