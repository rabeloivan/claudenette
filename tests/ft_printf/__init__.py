"""ft_printf 12.1, with independent optional bonus groups."""
from pathlib import Path

from ..libft import get_advisories as readme_advisories
from .runner import run_mandatory, run_width_bonus, run_sign_bonus
from .build import find_header, has_bonus_rule

PRESERVE_ORDER = True


def get_advisories():
    return ['ft_printf target: Linux/glibc (64-bit), tested natively.'] + readme_advisories()


def get_mapping():
    allowed = ['Makefile', '*.c', '*.h', '*/Makefile', 'README.md', '.git']
    allowed += [path.as_posix() for path in Path('.').rglob('*')
                if '.git' not in path.parts and path.is_dir()
                and (any(path.rglob('*.c')) or any(path.rglob('*.h')))]
    sources = list(dict.fromkeys(['Makefile', str(find_header(Path('.')))] + [str(path)
        for path in sorted(Path('.').rglob('*'))
        if path.suffix in ('.c', '.h') and '.git' not in path.parts]))
    options = {'allowed_files': allowed,
               'turn_in_files': ['Makefile', '*.h', '*/*.h', '*.c', '*/*.c', 'README.md'],
               'runner_checks_norm': True,
               'recursive_extra_files': True,
               'source_files': sources,
               'runner_checks_symbols': True, 'requires_tools': ['cc', 'make', 'ar', 'nm']}
    mapping = {'.': ('ft_printf', run_mandatory, [], options)}
    if has_bonus_rule(Path('.')):
        bonus = {**options, 'bonus': True, 'requires_mandatory': True}
        mapping['Makefile'] = ('ft_printf_bonus_width', run_width_bonus, [], bonus)
        mapping['./Makefile'] = ('ft_printf_bonus_signs', run_sign_bonus, [], bonus)
    return mapping
