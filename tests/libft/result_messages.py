"""Translate harness output for people, after the original byte-for-byte check.

These helpers never decide whether a case passes. Unknown/malformed output is
kept visible, and range failures identify the first differing input.
"""
import re
from itertools import groupby, zip_longest

from utils.ui import CasePresentation, display_str

RANGE_RULES = {
    'ft_isalpha': 'letters return 1, other values return 0',
    'ft_isdigit': 'digits return 1, other values return 0',
    'ft_isalnum': 'letters and digits return 1, other values return 0',
    'ft_isascii': 'values 0..127 return 1, other values return 0',
    'ft_isprint': 'printable ASCII characters return 1, other values return 0',
    'ft_toupper': 'lowercase letters become uppercase; other values stay unchanged',
    'ft_tolower': 'uppercase letters become lowercase; other values stay unchanged',
}
MEMORY_RETURNS = {'ft_memset', 'ft_memcpy', 'ft_memmove'}
STRING_COPIES = {'ft_strlcpy', 'ft_strlcat'}
POINTER_SEARCHES = {'ft_strchr', 'ft_strrchr', 'ft_memchr', 'ft_strnstr'}


def range_description(function, args):
    start, end = map(int, args)
    bounds = f'EOF and 0..{end}' if start == -1 else f'{start}..{end}'
    return f'{function}: {end-start+1} inputs ({bounds}); {RANGE_RULES[function]}'


def _buffer(hexadecimal):
    if not re.fullmatch(r'(?:[0-9a-f]{2})+', hexadecimal):
        return hexadecimal
    runs = []
    for byte, values in groupby(bytes.fromhex(hexadecimal)):
        count = sum(1 for _ in values)
        shown = display_str(chr(byte)) if 32 <= byte <= 126 else f'0x{byte:02X}'
        runs.append(f'{shown} x {count}' if count > 1 else shown)
    return 'buffer bytes: [' + ', '.join(runs) + ']'


def readable_result(function, value):
    """Decode only the known protocol of this function's ordinary harness."""
    if function in MEMORY_RETURNS:
        match = re.fullmatch(r'([0-9a-f]{32})\|R([01])', value)
        if match:
            pointer = 'destination pointer' if match[2] == '1' else 'a different pointer'
            return _buffer(match[1]) + '; returns ' + pointer
    if function in STRING_COPIES:
        match = re.fullmatch(r'(\d+)\|([0-9a-f]{32})', value)
        if match:
            return f'return {match[1]}; ' + _buffer(match[2])
    if function in ('ft_bzero', 'ft_calloc') and re.fullmatch(r'[0-9a-f]{32}', value):
        return _buffer(value)
    if function == 'ft_calloc' and value == 'NONNULL':
        return 'allocated pointer (not NULL)'
    if function in POINTER_SEARCHES and re.fullmatch(r'\d+', value):
        return f'pointer at byte {value}'
    if function == 'ft_lstlast' and re.fullmatch(r'\d+', value):
        return f'original node at index {value}'
    if function in ('ft_strncmp', 'ft_memcmp'):
        return {'+': 'positive (first input is greater)',
                '-': 'negative (first input is smaller)', '0': '0 (equal)'}.get(value, value)
    if function == 'ft_lstnew':
        match = re.fullmatch(r'(\[.*\])\|(SAMEPTR|COPIED)\|(NEXTNULL|NEXTSET)', value, re.S)
        if match:
            pointer = 'original content pointer' if match[2] == 'SAMEPTR' else 'different content pointer'
            tail = 'NULL' if match[3] == 'NEXTNULL' else 'not NULL'
            return f'content {display_str(match[1][1:-1])}; {pointer}; next = {tail}'
    if function == 'ft_lstdelone':
        match = re.fullmatch(r'(\d+)\|(\d+)\|(\d+)\|(\d+)', value)
        if match:
            return (f'del calls: {match[1]}; frees: node {match[2]}, '
                    f'content {match[3]}, next node {match[4]}')
    if function == 'ft_lstclear':
        match = re.fullmatch(r'(\d+)\|(\d+)\|(HEADNULL|HEADSET)', value)
        if match:
            head = 'NULL' if match[3] == 'HEADNULL' else 'not NULL'
            return f'del calls: {match[1]}; allocations not freed: {match[2]}; head = {head}'
    if function == 'ft_lstmap':
        if value == 'EMPTY':
            return 'empty list; no nodes allocated'
        suffix = '|NEW|SOURCEOK|FREED'
        if value.endswith(suffix):
            return f'contents {display_str(value[:-len(suffix)])}; new nodes; source unchanged; no leaks'
    if function == 'ft_split':
        match = re.fullmatch(r'((?:\[.*\])?)\|(\d+)', value, re.S)
        if match:
            unit = 'word' if match[2] == '1' else 'words'
            return f'{match[2]} {unit}: {display_str(match[1]) if match[1] else "empty array"}'
    return value


def success_message(function, args, description, actual, stderr=None, campaign=False):
    if campaign:
        return description
    if function in RANGE_RULES:
        return range_description(function, args)
    if stderr is not None:
        stdout = '' if actual == '[]' else actual
        return f'{description} output {display_str(stdout)} on stdout, {display_str(stderr)} on stderr'
    if function in MEMORY_RETURNS:
        return f'{description}; returns the destination pointer'
    if function in ('ft_bzero', 'ft_lstdelone', 'ft_lstclear'):
        return description
    if function == 'ft_lstnew':
        return (f'ft_lstnew({display_str(args[0])}) output a new node; '
                'original content pointer; next = NULL')
    if function in STRING_COPIES:
        returned, dump = actual.split('|')
        string = bytes.fromhex(dump).split(b'\0', 1)[0].decode('latin-1')
        return f'{description} output {display_str(string)}; return {returned}; other bytes unchanged'
    if function == 'ft_calloc':
        result = '16 zeroed bytes' if actual == '00' * 16 else readable_result(function, actual)
    elif function in ('ft_substr', 'ft_strjoin', 'ft_strtrim') and actual.startswith('['):
        result = display_str(actual[1:-1])
    elif function in POINTER_SEARCHES | {
        'ft_lstlast', 'ft_lstmap', 'ft_split', 'ft_strncmp', 'ft_memcmp'
    }:
        result = readable_result(function, actual)
    elif function in ('ft_strlen', 'ft_atoi', 'ft_lstsize'):
        result = actual
    else:
        # A string of digits (itoa, strmapi, putstr...) is still a string.
        result = display_str(actual)
    return f'{description} output {result}'


def failure_values(function, args, description, expected, actual, campaign=False):
    if campaign:
        return description, expected, actual
    if function in RANGE_RULES:
        description = range_description(function, args)
        if '[killed by signal ' in actual:
            return description, 'all inputs handled without a crash', actual[actual.index('[killed by signal '):]
        conversion = function in ('ft_toupper', 'ft_tolower')
        wanted = expected.split(',') if conversion else list(expected)
        got = actual.split(',') if conversion and actual else list(actual)
        for offset, (left, right) in enumerate(zip_longest(wanted, got)):
            if left == right:
                continue
            if left is None:
                return description, 'no extra output', display_str(''.join(got[offset:]), limit=80)
            value = int(args[0]) + offset
            label = 'EOF' if value == -1 else str(value)
            if 32 <= value <= 126:
                label += ' (' + display_str(chr(value)) + ')'
            right = ('missing result' if right is None else
                     'value other than 0 or 1' if right == '?' and not conversion else right)
            return f'{description}; first mismatch at input {label}', left, right
    return description, readable_result(function, expected), readable_result(function, actual)


def case_presentation(function, args, description, expected, actual,
                      stderr=None, campaign=False):
    """Describe an existing harness case without changing its comparison."""
    message, wanted, got = failure_values(function, args, description, expected, actual,
                                         campaign=campaign)
    string_results = {'ft_strdup', 'ft_itoa', 'ft_strmapi', 'ft_striteri',
                      'ft_putchar_fd', 'ft_putstr_fd', 'ft_putendl_fd', 'ft_putnbr_fd'}
    if not campaign and function in string_results:
        wanted, got = display_str(expected, 100), display_str(actual, 100)
    if not campaign and function in ('ft_substr', 'ft_strjoin', 'ft_strtrim'):
        wanted = display_str(expected[1:-1], 100) if expected.startswith('[') else expected
        got = display_str(actual[1:-1], 100) if actual.startswith('[') and actual.endswith(']') else display_str(actual, 100)
    call = function + '(...)'
    title = description.removeprefix(function + ': ')
    result = ''
    if function in RANGE_RULES and not campaign:
        start, end = map(int, args)
        title = ('EOF and unsigned char range' if start == -1 else
                 'ASCII range' if (start, end) == (0, 127) else 'Integer range')
        bounds = f'EOF and 0..{end}' if start == -1 else f'{start}..{end}'
        result = f'{end - start + 1} inputs ({bounds})'
        call = f'{function}(c), for c in {bounds}'
    elif not campaign:
        direct = {'ft_strlen', 'ft_strdup', 'ft_atoi', 'ft_itoa', 'ft_substr',
                  'ft_strjoin', 'ft_strtrim', 'ft_split', 'ft_strchr', 'ft_strrchr',
                  'ft_strncmp', 'ft_strnstr'}
        if function in direct:
            numeric = {'ft_itoa': (0,), 'ft_substr': (1, 2), 'ft_strchr': (1,),
                       'ft_strrchr': (1,), 'ft_strncmp': (2,), 'ft_strnstr': (2,)}
            call = function + '(' + ', '.join(
                str(arg) if i in numeric.get(function, ()) else display_str(arg, 64)
                for i, arg in enumerate(args)) + ')'
        if description.startswith(function + '('):
            shown = [display_str(arg, 12) for arg in args]
            if function in ('ft_strlen', 'ft_strdup'):
                title = ('Empty string' if not args[0] else 'Single character' if len(args[0]) == 1
                         else f'Long string — {len(args[0])} characters' if len(args[0]) > 64
                         else 'String ' + shown[0])
            elif function == 'ft_substr':
                title = f'Source {shown[0]}, start {args[1]}, len {args[2]}'
            elif function in ('ft_strjoin', 'ft_strtrim', 'ft_split'):
                verb = {'ft_strjoin': 'Join', 'ft_strtrim': 'Trim', 'ft_split': 'Split'}[function]
                title = f'{verb} {shown[0]} / {shown[1]}'
            elif function in ('ft_strncmp', 'ft_strnstr'):
                title = f'{shown[0]} / {shown[1]}, limit {args[2]}'
            elif function in ('ft_strchr', 'ft_strrchr'):
                title = f'String {shown[0]}, byte {args[1]}'
            elif function == 'ft_itoa':
                title = 'Integer ' + args[0]
            else:
                title = 'Input ' + ', '.join(shown)
        success = success_message(function, args, description, actual, stderr=stderr) \
            if actual == expected else description
        result = success[len(description):].lstrip(' ;') if success.startswith(description) else ''
        if function == 'ft_lstnew':
            result = 'new node, original content, next NULL'
    elif ': ' in title:
        title, result = title.split(': ', 1)
    if campaign and not args:
        title = 'Allocation failure positions handled'
    if campaign and title.startswith(function + '('):
        match = re.fullmatch(re.escape(function) + r'\((.*?)\)(?: output (.*))?', title)
        if match:
            title = match[1]
            result = 'output ' + match[2] if match[2] is not None else result
    if not campaign and actual == expected:
        if function in ('ft_strdup', 'ft_itoa', 'ft_strmapi', 'ft_striteri'):
            result = 'output ' + display_str(actual, 16)
        elif function in ('ft_substr', 'ft_strjoin', 'ft_strtrim') and actual.startswith('['):
            result = 'output ' + display_str(actual[1:-1], 16)
        elif function == 'ft_lstmap':
            result = 'new nodes, source preserved, no leaks'
        elif function == 'ft_split':
            result = 'output ' + actual.rsplit('|', 1)[-1] + ' words'
    title = title[:1].upper() + title[1:]
    return CasePresentation(title, result, call, str(wanted), str(got), (('Scenario', message),))
