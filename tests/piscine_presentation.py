"""Display metadata for existing Piscine messages; never evaluate a test case.

The original messages and values are recorded before this adapter runs. Only
known separators outside quoted inputs are decoded; unfamiliar text stays visible.
"""
import re
from pathlib import Path

from utils.reporting import defer_stage_blank
from utils.ui import (
    CasePresentation, begin_stage, display_str, print_command_execution, print_test_section,
)

PISCINE_MODULES = frozenset(
    [f'C{index:02}' for index in range(14)]
    + ['shell00', 'shell01', 'rush00', 'rush01', 'rush02', 'bsq', 'piscine_reloaded']
)


def _split_message(message):
    """Separate a scenario from its diagnostic without splitting input strings."""
    quote = None
    escaped = False
    depth = 0
    for index, char in enumerate(message):
        if escaped:
            escaped = False
            continue
        if quote:
            if char == '\\':
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in "'\"`" and (index == 0 or not message[index - 1].isalnum()):
            quote = char
        elif char in '([{':
            depth += 1
        elif char in ')]}':
            depth = max(0, depth - 1)
        elif depth == 0:
            if message.startswith(': ', index):
                return message[:index], message[index + 2:]
            if message.startswith(' output ', index):
                return message[:index], message[index + 1:]
    return message, ''


def _short_string(match):
    value = match[0]
    return value if len(value) <= 18 else value[:14].rstrip('\\') + "...'"


def _title(scenario):
    match = re.fullmatch(r'(?:ft_\w+|btree_\w+)\((.*)\)', scenario)
    if match:
        arguments = match[1]
        function = scenario.partition('(')[0]
        if arguments in ("str=''", "src=''", "s=''", "nbr=''", "''"):
            return 'Empty string'
        if scenario.startswith(('ft_strlen(', 'ft_putstr(', 'ft_strdup(')):
            text = re.fullmatch(r"(?:str=|src=|s=)?('(?:\\.|[^'\\])*')(?: \(\d+ chars total\))?", arguments)
            if text:
                return 'String ' + re.sub(r"'(?:\\.|[^'\\])*'", _short_string, text[1])
        if function in ('ft_strcmp', 'ft_strncmp', 'ft_strcat', 'ft_strncat', 'ft_strstr', 'ft_strlcat'):
            strings = re.findall(r"'(?:\\.|[^'\\])*'", arguments)
            if len(strings) == 2:
                title = ' / '.join(re.sub(r"'(?:\\.|[^'\\])*'", _short_string, s) for s in strings)
                limit = re.search(r'\b(?:n|nb|size)=(\d+)', arguments)
                return title + (', limit ' + limit[1] if limit else '')
        scalar = re.fullmatch(r'(?:c|nb|nbr|n|index)=(-?\d+|\'(?:\\.|[^\'\\])*\')', arguments)
        if scalar:
            return ('Character ' if arguments.startswith('c=') else 'Integer ') + scalar[1]
        return re.sub(r"'(?:\\.|[^'\\])*'", _short_string, arguments) or 'No arguments'
    return scenario[:1].upper() + scenario[1:]


def _value(value):
    if value is None:
        return None
    return display_str(value, 100) if isinstance(value, str) else str(value)


class PiscinePresentation:
    def __init__(self, module, student_file, name=None):
        self.module = module
        self.student_file = Path(student_file)
        self.header = Path(student_file).suffix == '.h'
        self.section = None
        if name is not None:
            # A reused test in another directory (Piscine Reloaded) names itself.
            self.name = name
        elif module in ('bsq', 'rush00', 'rush01', 'rush02'):
            self.name = module
        elif module == 'C10':
            self.name = {'ex00': 'ft_display_file', 'ex01': 'ft_cat',
                         'ex02': 'ft_tail', 'ex03': 'ft_hexdump'}[self.student_file.parent.name]
        elif module == 'C11' and self.student_file.name == 'Makefile':
            self.name = 'do-op'
        else:
            self.name = self.student_file.stem if self.student_file.suffix == '.c' else self.student_file.name
        self.test_name = re.sub(r'[^\w]+', '_', Path(self.name).stem).strip('_') + '_test'
        self.runtime_announced = False
        self.runtime_pending = False
        self.source_order = []
        self.allowed_results = {}
        self.grouped_sources = self._has_several_sources()

    def _has_several_sources(self):
        if self.module == 'bsq':
            return False
        directory = self.student_file if self.student_file.is_dir() else self.student_file.parent
        try:
            return sum(path.suffix in ('.c', '.h') for path in directory.iterdir()) > 1
        except OSError:
            return False

    def _source_command(self, command):
        if not self.grouped_sources:
            return command
        if command.startswith('nm -u '):
            return re.sub(r'^nm -u \S+ \(', f'nm -u {self.name} sources (', command)
        if command.startswith(('norminette ', 'python -m norminette ')):
            return command.rsplit(' ', 1)[0] + ' .'
        return command

    def command(self, command):
        """Render logical names; the actual subprocess commands are untouched."""
        if self.module == 'bsq' and command.startswith('nm -u ') and not command.startswith('nm -u . ('):
            return None
        if command.startswith(('checking ', 'norminette ', 'python -m norminette ', 'nm ')):
            return self._source_command(command.replace('nm -u . (', f'nm -u {self.name} sources ('))
        if command.startswith('cc '):
            target = re.search(r' -o (\S+)', command)
            name = self.test_name
            if target and self.module == 'rush00':
                variant = re.fullmatch(r'rush_([0-4])', Path(target[1]).name)
                name = f'rush0{variant[1]}_test' if variant else 'main_test'
            command = re.sub(r' -o \S+', ' -o ' + name, command)
            return re.sub(r'\bex\d\d_harness\.c\b', '(checking ' + self.name + ')', command)
        if command == 'make' or command.startswith('make '):
            return command
        if self.module == 'C09' and command == 'sh libft_creator.sh':
            return command
        if self.module == 'bsq' and command != self.test_name:
            # The existing runner announces this before its last Makefile case.
            # The first map case emits it below, without moving any test.
            self.runtime_pending = True
            return None
        if self.module == 'rush00':
            variant = re.search(r'(?:^|/)rush_([0-4])(?:\s|$)', command)
            if variant:
                self.runtime_announced = True
                return f'rush0{variant[1]}_test'
        self.runtime_announced = True
        return self.test_name

    def summary_name(self, original):
        if self.module == 'rush00':
            variant = re.search(r'(rush0[0-4])\.c', original)
            return variant[1] if variant else self.name
        suffix = original[original.index(' ['):] if ' [' in original else ''
        return self.name + suffix

    def flush_prechecks(self):
        """Print only recorded symbol-check successes in the source display order."""
        if not self.allowed_results:
            return
        from utils.ui import console
        for filename in dict.fromkeys([*self.source_order, *self.allowed_results]):
            if filename in self.allowed_results:
                console.print(filename + ': OK!', style='sea_green2', markup=False, highlight=False)
        self.allowed_results.clear()
        defer_stage_blank()

    def _campaign(self, message):
        if message.startswith(('handles each malloc failure;', 'allocation failure/ownership contract')):
            return 'Allocation failures'
        if message.startswith('NULL safety: ') or (
                'NULL' in message and re.search(r'no crash or hang|did not crash or hang|hung \(timed out\)|crashed', message)):
            return 'NULL safety'
        if re.match(r'\w+\(\d+(?:-byte string| bytes?).*buffer', message):
            return 'Boundary tests'
        if 'called twice' in message:
            return 'Repeated calls'
        if self.header:
            return 'Header validation'
        if self.name == 'Makefile':
            return 'Makefile checks'
        if message.startswith(('`make`', 'bare `make`', 'a second `make`', 'make ', 'Makefile')):
            return 'Makefile checks'
        if self.module.startswith('shell'):
            return 'Shell checks'
        if self.module == 'rush00':
            variant = re.search(r'\[(rush0\d)\]', message)
            return 'Shape output — ' + variant[1] if variant else 'Build and interface'
        if self.module == 'rush01':
            return 'Bonus grids' if message.startswith('[BONUS') else 'Grid solutions and errors'
        if self.module == 'rush02':
            return 'Bonus translations' if message.startswith('[BONUS') else 'Number translations and errors'
        if self.module == 'bsq':
            return 'Map errors' if message.startswith('invalid map [') else 'Maps and input handling'
        if self.module == 'C10':
            return 'Command behavior'
        return 'Functional tests'

    def __call__(self, description, passed, expected=None, actual=None):
        self.flush_prechecks()
        message = description.removesuffix(' as expected' if passed else ' not as expected')
        section = self._campaign(message)
        if (self.module.startswith('shell') or self.runtime_pending) and not self.runtime_announced \
                and section not in ('Makefile checks', 'Build and interface'):
            print_command_execution(self.test_name)
        if section != self.section:
            if section == 'Makefile checks':
                begin_stage('make')
            elif section == 'Build and interface':
                begin_stage('build')
            print_test_section(section)
            self.section = section
        message = message.removeprefix('NULL safety: ')
        scenario, diagnostic = _split_message(message)
        if not diagnostic and passed:
            trailing = re.fullmatch(r"(.*?) ('(?:\\.|[^'\\])*'(?: \(\d+ chars total\))?|\[.*\]|\d+)", scenario)
            if trailing:
                scenario, diagnostic = trailing.groups()
        title = _title(scenario)
        result = diagnostic
        call = scenario if re.match(r'^(?:ft_\w+|btree_\w+|rush\d*)\(', scenario) else ''
        if section == 'Allocation failures':
            title = 'Allocation failure positions handled'
            result = 'freeable memory, no leaks' if passed else ''
        elif section == 'NULL safety':
            result = 'no crash or hang' if passed else ''
        elif result == 'output':
            result = 'output matches'
        elif result == 'output value':
            result = 'return value matches'
        result = result.replace("output value's sign", 'return sign')
        details = []
        if not passed:
            if not call:
                details.append(('Scenario', scenario))
            if diagnostic and diagnostic not in ('output', 'shape', 'biggest square', 'output value'):
                details.append(('Reason', diagnostic.replace("output value's sign", 'return sign differs')))
        # Keep mismatches beyond a shortened value preview discoverable.
        if not passed and isinstance(expected, str) and isinstance(actual, str) and expected != actual:
            offset = next((i for i, (left, right) in enumerate(zip(expected, actual))
                           if left != right), min(len(expected), len(actual)))
            if offset >= 100:
                wanted = _value(expected[offset:offset + 1]) if offset < len(expected) else 'end of output'
                got = _value(actual[offset:offset + 1]) if offset < len(actual) else 'end of output'
                details.append(('Difference', f'offset {offset}: expected {wanted}, got {got}'))
        return CasePresentation(title, result if passed else '', call,
                                _value(expected), _value(actual), tuple(details))
