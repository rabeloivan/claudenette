"""Short case labels and diagnostic fields for the printf report."""
import re
from itertools import zip_longest

from utils.ui import CasePresentation, display_str
from .cases import describe


def case_title(case):
    if case.string_size is not None:
        ending = 'at buffer end' if case.terminated else 'without a terminator'
        unit = 'byte' if case.string_size == 1 else 'bytes'
        return f'%s — {case.string_size} {unit} {ending}'
    specs = re.findall(r'%[-+ #0]*\d*(?:\.\d*)?[cspdiuxX%]', case.format)
    conversions = [spec for spec in specs if spec[-1] != '%']
    if not conversions:
        if not case.format:
            return 'Empty format'
        if specs:
            return 'Percent literal'
        if all(ord(char) < 32 or ord(char) == 127 for char in case.format):
            return 'Control characters'
        return 'Long literal' if len(case.format) > 64 else 'Literal text'
    if len(conversions) > 1:
        kinds = {spec[-1] for spec in conversions}
        if len(kinds) == 1:
            return {'c': 'Multiple characters', 's': 'Joined strings',
                    'p': 'Multiple pointers'}.get(next(iter(kinds)), 'Mixed conversions')
        return 'Mixed conversions'
    spec, argument = conversions[0], case.arguments[0]
    kind = spec[-1]
    if kind == 'c':
        value = 'null byte' if argument == '0' else 'value ' + argument
    elif kind == 's':
        value = 'empty string' if argument == '""' else 'string'
    elif kind == 'p':
        value = 'null pointer' if argument == '(void *)0' else 'pointer'
    else:
        value = {'INT_MIN': 'minimum integer', '-2147483648': 'minimum integer',
                 '2147483647': 'maximum integer'}.get(argument, argument)
    return f'{spec} — {value}'


def output_value(data, limit=60):
    return display_str(data.decode('latin-1'), limit)


def result_presentation(case, actual, expected, actual_return, expected_return,
                        live, mode, failure, attempts, problems, tracked=False):
    title = case_title(case)
    wanted = f'output {output_value(expected)}, return {expected_return}'
    got = f'output {output_value(actual)}, return {actual_return}'
    details = []
    shown = 'output ' + output_value(actual, 16)
    if len(shown) > 27:
        shown = f'{len(actual)} bytes'
    result = f'{shown:<28}return {actual_return}'
    if mode in ('write_error', 'late_write_error'):
        partial = mode == 'late_write_error'
        title += ' — failure after partial output' if partial else ' — closed stdout'
        wanted = f'output {output_value(expected[:1] if partial else b"")}, negative return'
        details.append(('Normal', f'output {output_value(expected)}, return {expected_return}'))
        result = 'negative return'
    elif failure >= 0:
        title += f' — allocation failure {failure + 1}'
        wanted = 'negative return with partial output, or complete recovery'
        details.extend((('Normal', f'output {output_value(expected)}, return {expected_return}'),
                        ('Allocations', f'{attempts} attempts, failure at position {failure + 1}')))
        result = 'failure handled, no live allocations'
    elif tracked:
        result = 'output, return and live allocations checked'
    if tracked or live:
        details.append(('Live allocations', f'{live} (expected 0)'))
    compared = expected[:1] if mode == 'late_write_error' else expected
    if failure < 0 and mode in ('normal', 'late_write_error') and actual != compared:
        for offset, (wanted_byte, got_byte) in enumerate(zip_longest(compared, actual)):
            if wanted_byte != got_byte:
                wanted_byte = 'end of output' if wanted_byte is None else f'0x{wanted_byte:02x}'
                got_byte = 'end of output' if got_byte is None else f'0x{got_byte:02x}'
                details.append(('Difference', f'byte {offset}: expected {wanted_byte}, got {got_byte}'))
                break
    if problems:
        details.append(('Reason', '\n'.join(problems)))
    return CasePresentation(title, result, describe(case), wanted, got, tuple(details))
