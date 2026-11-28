"""get_next_line 14.3, with its optional multiple-descriptor bonus."""
from pathlib import Path

from .runner import BUFFER_SIZES, run_mandatory, run_bonus

PRESERVE_ORDER = True


def get_mapping():
    allowed = [
        'get_next_line.c', 'get_next_line_utils.c', 'get_next_line.h',
        'get_next_line_bonus.c', 'get_next_line_utils_bonus.c', 'get_next_line_bonus.h',
        'README.md', '.git',
    ]
    mapping = {}
    for suffix, run in [('', run_mandatory), ('_bonus', run_bonus)]:
        sources = [f'get_next_line{suffix}.c', f'get_next_line_utils{suffix}.c',
                   f'get_next_line{suffix}.h']
        if suffix and not any(Path(source).exists() for source in sources):
            continue
        mapping[sources[0]] = (
            f'get_next_line{suffix}', run, ['read', 'malloc', 'free'],
            {'allowed_files': allowed, 'source_files': sources,
             'runner_checks_norm': True, 'runner_checks_functions': True,
             'bonus': bool(suffix), 'requires_mandatory': bool(suffix),
             'compile_variants': [([] if size is None else [f'-DBUFFER_SIZE={size}'])
                                  for size in BUFFER_SIZES]},
        )
    return mapping
