"""NULL policy for custom functions. Manual-backed libc domains stay untouched.

Each probe changes one pointer argument; other arguments remain valid. The
house rule checks termination, not an invented return value for unspecified
NULL behavior. Shell programs are tested through their real CLI, not main(NULL).
"""
from pathlib import Path
import os
import re
import tempfile

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import print_exercise_result, print_test_fail, print_test_pass

ROOT = Path(__file__).resolve().parent
CALLS = {}


def add(module, name, *args):
    CALLS[(module, name)] = [(f'NULL safety: {name}({arguments})', f'{name}({arguments});')
                             for arguments in args]


for name in ['ft_str_is_alpha', 'ft_str_is_numeric', 'ft_str_is_lowercase',
             'ft_str_is_uppercase', 'ft_str_is_printable', 'ft_strupcase',
             'ft_strlowcase', 'ft_strcapitalize', 'ft_putstr_non_printable']:
    add('C02', name, 'NULL')
add('C02', 'ft_print_memory', 'NULL, 1')
for name in ['ft_strlen', 'ft_putstr', 'ft_atoi']:
    add('C04', name, 'NULL')
add('C04', 'ft_putnbr_base', '1, NULL')
add('C04', 'ft_atoi_base', 'NULL, str', 'str, NULL')
add('C07', 'ft_ultimate_range', 'NULL, 0, 2')
add('C07', 'ft_strjoin', '1, NULL, str', '1, words, NULL')
add('C07', 'ft_convert_base', 'NULL, str, str', 'str, NULL, str', 'str, str, NULL')
add('C07', 'ft_split', 'NULL, str', 'str, NULL')
add('C08', 'ft_strs_to_tab', '1, NULL')
add('C08', 'ft_show_tab', 'NULL')
add('C09', 'ft_split', 'NULL, str', 'str, NULL')
add('C11', 'ft_foreach', 'NULL, 1, p_void_int', 'numbers, 1, NULL')
add('C11', 'ft_map', 'NULL, 1, p_int', 'numbers, 1, NULL')
add('C11', 'ft_any', 'NULL, p_str', 'words, NULL')
add('C11', 'ft_count_if', 'NULL, 1, p_str', 'words, 1, NULL')
add('C11', 'ft_is_sort', 'NULL, 2, p_int_cmp', 'numbers, 2, NULL')
add('C11', 'ft_sort_string_tab', 'NULL')
add('C11', 'ft_advanced_sort_string_tab', 'NULL, p_str_cmp', 'words, NULL')
add('C12', 'ft_create_elem', 'NULL')
for name in ['ft_list_push_front', 'ft_list_push_back']:
    add('C12', name, 'NULL, &value', '&list, NULL')
for name in ['ft_list_size', 'ft_list_last', 'ft_list_reverse_fun']:
    add('C12', name, 'NULL')
add('C12', 'ft_list_push_strs', '1, NULL')
add('C12', 'ft_list_clear', 'NULL, p_void', 'list, NULL')
add('C12', 'ft_list_at', 'NULL, 0')
add('C12', 'ft_list_reverse', 'NULL')
add('C12', 'ft_list_foreach', 'NULL, p_void', 'list, NULL')
add('C12', 'ft_list_foreach_if', 'NULL, p_void, &value, p_cmp',
    'list, NULL, &value, p_cmp', 'list, p_void, NULL, p_cmp', 'list, p_void, &value, NULL')
add('C12', 'ft_list_find', 'NULL, &value, p_cmp', 'list, NULL, p_cmp', 'list, &value, NULL')
add('C12', 'ft_list_remove_if', 'NULL, &value, p_cmp, p_void', '&list, NULL, p_cmp, p_void',
    '&list, &value, NULL, p_void', '&list, &value, p_cmp, NULL')
add('C12', 'ft_list_merge', 'NULL, list', '&list, NULL')
add('C12', 'ft_list_sort', 'NULL, p_cmp', '&list, NULL')
add('C12', 'ft_sorted_list_insert', 'NULL, &value, p_cmp', '&list, NULL, p_cmp', '&list, &value, NULL')
add('C12', 'ft_sorted_list_merge', 'NULL, list, p_cmp', '&list, NULL, p_cmp', '&list, otherlist, NULL')
add('C13', 'btree_create_node', 'NULL')
for name in ['btree_apply_prefix', 'btree_apply_infix', 'btree_apply_suffix']:
    add('C13', name, 'NULL, p_void', 'tree, NULL')
add('C13', 'btree_insert_data', 'NULL, &value, p_cmp', '&tree, NULL, p_cmp', '&tree, &value, NULL')
add('C13', 'btree_search_item', 'NULL, &value, p_cmp', 'tree, NULL, p_cmp', 'tree, &value, NULL')
add('C13', 'btree_level_count', 'NULL')
add('C13', 'btree_apply_by_level', 'NULL, p_level', 'tree, NULL')
add('libft', 'ft_substr', 'NULL, 0, 1')
add('libft', 'ft_strjoin', 'NULL, str', 'str, NULL')
add('libft', 'ft_strtrim', 'NULL, str', 'str, NULL')
add('libft', 'ft_split', "NULL, ' '")
add('libft', 'ft_strmapi', 'NULL, p_char', 'str, NULL')
add('libft', 'ft_striteri', 'NULL, p_char_ptr', 'str, NULL')
for name in ['ft_putstr_fd', 'ft_putendl_fd']:
    add('libft', name, 'NULL, 1')
add('libft', 'ft_lstnew', 'NULL')
for name in ['ft_lstadd_front', 'ft_lstadd_back']:
    add('libft', name, 'NULL, list', '&list, NULL')
for name in ['ft_lstsize', 'ft_lstlast']:
    add('libft', name, 'NULL')
add('libft', 'ft_lstdelone', 'NULL, p_void', 'list, NULL')
add('libft', 'ft_lstclear', 'NULL, p_void', '&list, NULL')
add('libft', 'ft_lstiter', 'NULL, p_void', 'list, NULL')
add('libft', 'ft_lstmap', 'NULL, p_ptr, p_void', 'list, NULL, p_void', 'list, p_ptr, NULL')

# The subjects explicitly require these man-page behaviors; NULL is outside
# their valid pointer domain. Do not infer exemptions merely from a familiar name.
MANUAL_EXEMPTIONS = {
    'C02': {'ft_strcpy', 'ft_strncpy', 'ft_strlcpy'},
    'C03': {'ft_strcmp', 'ft_strncmp', 'ft_strcat', 'ft_strncat', 'ft_strstr', 'ft_strlcat'},
    'C07': {'ft_strdup'},
    'libft': {'ft_strlen', 'ft_memset', 'ft_bzero', 'ft_memcpy', 'ft_memmove',
              'ft_strlcpy', 'ft_strlcat', 'ft_strchr', 'ft_strrchr', 'ft_strncmp',
              'ft_memchr', 'ft_memcmp', 'ft_strnstr', 'ft_atoi', 'ft_strdup'},
}

HELPERS = r'''
#include <stdlib.h>
#include <stdint.h>
#include <stddef.h>
int p_int(int n) { return n; }
void p_void_int(int n) { (void)n; }
int p_int_cmp(int a, int b) { return (a > b) - (a < b); }
int p_str(char *s) { return s != NULL; }
int p_str_cmp(char *a, char *b) { (void)a; (void)b; return 0; }
int p_cmp(void *a, void *b) { return ((uintptr_t)a > (uintptr_t)b) - ((uintptr_t)a < (uintptr_t)b); }
void p_void(void *p) { (void)p; }
void *p_ptr(void *p) { return p; }
void p_level(void *p, int level, int first) { (void)p; (void)level; (void)first; }
char p_char(unsigned int i, char c) { (void)i; return c; }
void p_char_ptr(unsigned int i, char *c) { (void)i; (void)c; }
'''
SETUP = '''
    int value = 1;
    int numbers[2] = {1, 2};
    char str[3] = "01";
    char *words[3] = {str, str, NULL};
    (void)value; (void)numbers; (void)str; (void)words;
'''


def run_null_contracts(module, student_file, options=None):
    name = Path(student_file).stem
    cases = CALLS.get((module, name))
    if not cases:
        return True
    assert name not in MANUAL_EXEMPTIONS.get(module, set())
    options = options or {}
    if module == 'libft':
        from tests.libft.harness_runner import check_student_definition
        if not check_student_definition(student_file, name):
            return False
        harness = ROOT / 'libft' / name / f'{name}_harness.c'
    else:
        harness = ROOT / module / Path(student_file).parent / (Path(student_file).parent.name + '_harness.c')
    text = harness.read_text()
    match = re.search(r'(?m)^([A-Za-z_][^;{}]*?\b' + re.escape(name) + r'\s*\([^;{}]*\);)', text)
    if not match:
        raise ValueError(f'NULL contract has no prototype: {module}/{name}')
    prototype = match.group(1)
    includes = ''
    setup = SETUP
    sources = [str(Path(student_file).resolve())]
    flags = ['-Wall', '-Wextra', '-Werror', '-I', str(Path(student_file).resolve().parent)]
    flags += options.get('compile_flags', [])
    if module in ('C12', 'libft'):
        includes = '#include "' + ('libft.h' if module == 'libft' else 'ft_list.h') + '"\n'
        field = 'content' if module == 'libft' else 'data'
        setup += f'    t_list *list = malloc(sizeof(*list));\n    t_list *otherlist = malloc(sizeof(*otherlist));\n    if (!list || !otherlist) return 3;\n    list->{field} = &value; list->next = NULL;\n    otherlist->{field} = &value; otherlist->next = NULL;\n    (void)list; (void)otherlist;\n'
        if module == 'C12':
            # The subject mandates old-style comparator prototypes.
            flags.append('-Wno-deprecated-non-prototype')
        if module == 'C12' and name != 'ft_create_elem':
            sources.append(str(ROOT / 'C12/ft_create_elem_ref.c'))
    elif module == 'C13':
        includes = '#include "ft_btree.h"\n'
        setup += '    t_btree *tree = malloc(sizeof(*tree));\n    if (!tree) return 3;\n    tree->item = &value; tree->left = NULL; tree->right = NULL;\n    (void)tree;\n'
        if name == 'btree_insert_data':
            sources.append(str(ROOT / 'C13/btree_create_node_ref.c'))
    elif module == 'C08':
        includes = '#include "ft_stock_str.h"\n'
    elif name == 'ft_convert_base':
        sources = [str(p.resolve()) for p in Path(student_file).parent.glob('*.c')]
    if module == 'libft':
        from tests.libft.harness_runner import reference_archive
        sources.append(reference_archive())
    with tempfile.TemporaryDirectory(prefix='claudenette-null-') as directory:
        source = Path(directory) / 'null_contract.c'
        exe = str(Path(directory) / 'null_contract')
        body = '\n'.join(f'    if (which == {i}) {{ {call} }}' for i, (_, call) in enumerate(cases))
        source.write_text(HELPERS + includes + prototype + '\nint main(int argc, char **argv) {\n'
                          + setup + '    (void)argc; int which = atoi(argv[1]);\n' + body + '\n    return 0;\n}\n')
        # Put the reference archive last, after the harness's callback symbols.
        sources.insert(1, str(source))
        if not compile_source(sources, exe, flags=flags):
            print_exercise_result(name + ' NULL safety', 0, len(cases))
            return False
        passed = 0
        for index, (description, _) in enumerate(cases):
            _, err, code = run_test_case(exe, args=[str(index)])
            if code == 0:
                passed += 1
                print_test_pass(index + 1, description + ': no crash or hang')
            else:
                reason = 'timeout' if err == 'TIMEOUT' else f'exit {code}'
                print_test_fail(index + 1, description, actual=reason)
        print_exercise_result(name + ' NULL safety', passed, len(cases))
        return passed == len(cases)
