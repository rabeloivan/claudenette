"""Scratch Makefile builds and checks against the archive actually submitted."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile

from tests.libft.build_utils import archive_defines, archive_is_ar, mentions_libtool, run_make
from utils.functions import COMPILER_ARTIFACTS, SYMBOL_ALIASES
from utils.ui import CasePresentation


NAME = 'libftprintf.a'


def find_header(root):
    headers = [path for path in root.rglob('ft_printf.h') if '.git' not in path.parts]
    return min(headers, key=lambda path: (len(path.parts), str(path))) if headers else root / 'ft_printf.h'


def copy_project(root, destination):
    shutil.copytree(root, destination,
                    ignore=shutil.ignore_patterns('.git', '*.o', '*.a', '__pycache__'))
    return destination


def has_bonus_rule(root):
    if not (root / 'Makefile').is_file() or not shutil.which('make'):
        return False
    # Let make expand target variables and conditionals. Even query mode can
    # evaluate shell expressions/remake includes, so discovery uses a copy too.
    with tempfile.TemporaryDirectory(prefix='claudenette-printf-targets-') as directory:
        project = copy_project(root, Path(directory) / 'project')
        try:
            result = subprocess.run(['make', '-qp', 'bonus'], cwd=project,
                                    capture_output=True, text=True, timeout=10,
                                    env={**os.environ, 'LC_ALL': 'C'})
        except subprocess.TimeoutExpired:
            return False
    # Recursive make prints child databases first. Only the final root database
    # decides whether this project offers a bonus, including MAKECMDGOALS rules.
    database = result.stdout.rsplit('# Make data base,', 1)[-1]
    lines = database.split('\n# Files\n', 1)[-1].splitlines()
    return any(re.match(r'^bonus\s*:(?!=)', line)
               and (index == 0 or lines[index - 1] != '# Not a target:')
               for index, line in enumerate(lines))


def check_makefile(project, check):
    archive = project / NAME
    dry, dry_code = run_make(str(project), ['-n'])
    output, code = run_make(str(project))
    check(code == 0, 'bare make completes successfully', output[-1200:],
          presentation=CasePresentation('Default target', 'build succeeded', actual=output[-1200:]))
    check(archive.exists(), 'make creates libftprintf.a at the repository root',
          presentation=CasePresentation('Library output', 'libftprintf.a created',
                                        expected='libftprintf.a at the repository root', actual='archive missing'))
    check(dry_code == 0 and {'-Wall', '-Wextra', '-Werror'} <= set(dry.split()),
          'compile commands use -Wall, -Wextra and -Werror', dry[-1200:],
          presentation=CasePresentation('Compilation flags', '-Wall -Wextra -Werror',
                                        expected='-Wall -Wextra -Werror', actual=dry[-1200:]))
    check(all(not mentions_libtool(str(path)) for path in project.rglob('Makefile')),
          'Makefile follows the subject restriction on libtool',
          presentation=CasePresentation('Archive tool', 'libtool absent', actual='libtool invoked'))
    check(archive_is_ar(str(archive)), 'libftprintf.a is a readable ar archive',
          presentation=CasePresentation('Archive format', 'readable ar archive', actual='invalid archive'))
    check('ft_printf' in archive_defines(str(archive)), 'the archive defines ft_printf',
          presentation=CasePresentation('Archive symbols', 'ft_printf defined', actual='ft_printf missing'))
    before = archive.stat().st_mtime_ns if archive.exists() else None
    output, code = run_make(str(project))
    after = archive.stat().st_mtime_ns if archive.exists() else None
    check(code == 0 and before == after and before is not None,
          'a second make succeeds without rebuilding the archive', output[-1200:],
          presentation=CasePresentation('Repeated make', 'no unnecessary relinking', actual=output[-1200:]))
    output, code = run_make(str(project), ['clean'])
    check(code == 0 and not list(project.rglob('*.o')),
          'make clean removes object files, including nested objects', output[-1200:],
          presentation=CasePresentation('clean — object files', 'removed, including subdirectories',
                                        actual=output[-1200:] or 'clean failed or object files remain'))
    check(archive.exists(), 'make clean preserves libftprintf.a',
          presentation=CasePresentation('clean — library', 'preserved', actual='libftprintf.a missing'))
    output, code = run_make(str(project), ['fclean'])
    check(code == 0 and not archive.exists(), 'make fclean removes libftprintf.a', output[-1200:],
          presentation=CasePresentation('fclean', 'library removed',
                                        actual=output[-1200:] or 'fclean failed or archive remains'))
    output, code = run_make(str(project), ['re'])
    check(code == 0 and archive_is_ar(str(archive)), 'make re rebuilds libftprintf.a', output[-1200:],
          presentation=CasePresentation('re', 'library rebuilt', actual=output[-1200:] or 'invalid archive'))
    for target in ('all', NAME):
        run_make(str(project), ['fclean'])
        output, code = run_make(str(project), [target])
        check(code == 0 and archive_is_ar(str(archive)), f'make {target} builds the archive', output[-1200:],
              presentation=CasePresentation('all' if target == 'all' else 'Library target',
                                            'libftprintf.a created', actual=output[-1200:] or 'invalid archive'))
    # Reuse these generic archive helpers, without Libft's 43-function or c99 rules.
    return archive


def check_archive_symbols(archive):
    result = subprocess.run(['nm', '-g', str(archive)], capture_output=True, text=True, timeout=30)
    if result.returncode:
        return False, result.stderr.strip() or 'nm could not inspect the archive'
    defined = set()
    undefined = set()
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[-2] == 'U':
            name = parts[-1].lstrip('_')
            undefined.add(SYMBOL_ALIASES.get(name, name))
        elif len(parts) >= 3 and re.fullmatch('[A-Za-z]', parts[-2]):
            defined.add(parts[-1].lstrip('_'))
    forbidden = undefined - defined - {'malloc', 'free', 'write'} - COMPILER_ARTIFACTS
    return not forbidden, 'forbidden external symbols: ' + ', '.join(sorted(forbidden))


def source_files_ok(root, check):
    unexpected = []
    for directory, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name != '.git']
        for name in files:
            path = Path(directory) / name
            if name != 'Makefile' and path != root / 'README.md' and path.suffix not in ('.c', '.h'):
                unexpected.append(str(path.relative_to(root)))
    detail = ', '.join(unexpected)
    if unexpected:
        detail += '; keep local test logs outside the submission tree; review the files intended for delivery'
    check(not unexpected, 'submission files follow the subject file list', detail)
