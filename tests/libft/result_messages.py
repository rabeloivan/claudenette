"""Translate harness output for people, after the original byte-for-byte check.

These helpers never decide whether a case passes. Unknown/malformed output is
kept visible, and range failures identify the first differing input.
"""
import re
from itertools import groupby, zip_longest

from utils.ui import display_str

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
