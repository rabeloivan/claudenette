"""Typed, deterministic cases within the current subject's printf domain."""
from dataclasses import dataclass
import random
import re


@dataclass(frozen=True)
class Case:
    format: str
    arguments: tuple = ()
    note: str = ''
    string_size: int | None = None
    terminated: bool = True


def c_string(value):
    data = value.encode('utf-8')
    return '"' + ''.join(chr(byte) if 32 <= byte < 127 and chr(byte) not in '\\"'
                         else f'\\{byte:03o}' for byte in data) + '"'


def oracle_call(case):
    """Use glibc's NULL %p spelling in typed oracle calls, never student calls."""
    arguments = list(case.arguments)
    parts = []
    end = index = 0
    for match in re.finditer(r'%([-+ #0]*)(\d*)(\.\d*)?([cspdiuxX%])', case.format):
        conversion = match.group(4)
        if conversion == '%':
            continue
        if conversion == 'p' and arguments[index] == '(void *)0':
            if match.group(1).replace('-', '') or match.group(3):
                raise ValueError('NULL %p oracle supports field width and left alignment only')
            parts.append(case.format[end:match.end() - 1] + 's')
            end = match.end()
            arguments[index] = c_string('(nil)')
        index += 1
    parts.append(case.format[end:])
    return ''.join(parts), tuple(arguments)


def mandatory_cases():
    cases = [Case(''), Case('hello world'), Case('\t\n\r\v\f\a\b'),
             Case('a' * 4096, note='4096 literal bytes')]
    for value in (0, 48, 65, 32, 9, 10, 127, 128, 255, -1, -208, 304, 2147483647):
        cases.append(Case('%c', (str(value),)))
    cases += [Case(' %c %c %c ', ('48', '0', '49')),
              Case('%cc%cc%c', ('97', '9', '98')),
              Case('%c', ('INT_MIN',)),
              Case('%c' * 256, tuple(map(str, range(256))), 'all 256 character byte values')]
    for value in ('', 'a', 'hello world', 'some string with %s hehe', 'a\tb\nc',
                  'ação été 終わり', 'x' * 4096):
        cases.append(Case('%s', (c_string(value),)))
    cases += [Case('%s%s%s%s%s', tuple(c_string(s) for s in ('And ', '', 'some', ' ', 'joined')))]
    for size in (0, 1, 7, 42, 4096):
        cases.append(Case('%s', ('h_string',),
                          f'ft_printf("%s", {size}-byte string at buffer end)', size))
    for pointer in ('(void *)0', '(void *)h_objects', '(void *)(h_objects + 1)',
                    '(void *)(h_objects + 31)'):
        cases.append(Case('%p', (pointer,)))
    cases.append(Case('%p %p %p', ('(void *)h_objects', '(void *)0', '(void *)(h_objects + 7)')))
    signed = [0, 1, 9, 10, 11, 15, 16, 17, 99, 100, 101, 999, 1000,
              -1, -9, -10, -11, -14, -15, -16, -99, -100, -101, -200000, -6000023,
              2147483647, -2147483648]
    unsigned = [0, 1, 9, 10, 15, 16, 17, 99, 100, 255, 256, 4095, 4096,
                0xabcdef, 0x7fedcba1, 2147483647, 2147483648, 4294967295,
                (-10) % 2**32, (-6000023) % 2**32]
    for conversion in 'diuxX':
        values = signed if conversion in 'di' else unsigned
        for value in values:
            arg = ('INT_MIN' if value == -2**31 else str(value)) if conversion in 'di' else f'{value}u'
            cases.append(Case('%' + conversion, (arg,)))
        args = ('1', '2', '-3') if conversion in 'di' else ('1u', '2u', '4294967293u')
        cases.append(Case(f'%{conversion}%{conversion}{conversion}%{conversion}', args))
    cases += [Case('%%'), Case(' %% '), Case('%%c'), Case('%%%%%%'),
              Case('%%%c', ('120',)), Case('%c%%s%s%d%i%u%x%X%p%%',
              ('0', '"%d"', '-42', '2147483647', '4294967295u', '0xabcdefu',
               '0xabcdefu', '(void *)h_objects'))]
    # Alelievr/Cacharle generation properties, with a fixed seed and exact types.
    rng = random.Random(421201)
    for _ in range(48):
        signed_value = rng.randrange(-2**31, 2**31)
        unsigned_value = rng.randrange(2**32)
        cases.append(Case('value=%d/%i hex=%x/%X unsigned=%u text=%s char=%c %%',
                          (str(signed_value), str(-1 - signed_value), f'{unsigned_value}u',
                           f'{unsigned_value}u', f'{unsigned_value}u', '"edge%case"',
                           str(rng.randrange(256)))))
    return list(dict.fromkeys(cases))


def width_cases():
    cases = []
    for conversion in 'cspdiuxX':
        args = {'c': ('0', '65'), 's': ('""', '"hello"'),
                'p': ('(void *)0', '(void *)h_objects'),
                'd': ('0', '-42', '2147483647', 'INT_MIN'),
                'i': ('0', '42', '-42'), 'u': ('0u', '42u', '4294967295u'),
                'x': ('0u', '42u', '4294967295u'), 'X': ('0u', '42u', '4294967295u')}[conversion]
        specs = ['1', '5', '20', '-1', '-5', '-20']
        if conversion in 'diuxX':
            specs += ['.0', '.', '.1', '.8', '05', '020', '-05', '0-20',
                      '5.0', '20.8', '020.8', '-20.8', '-020.8']
        elif conversion == 's':
            specs += ['.0', '.', '.1', '.4', '10.3', '-10.3']
        for spec in specs:
            for arg in args:
                cases.append(Case('[' + '%' + spec + conversion + ']', (arg,)))
    cases += [Case('[%1000.512d]', ('-42',)), Case('[%-1000.512x]', ('0xabcdefu',)),
              Case('%-8s|%08d|%.0u|%10p|%5c',
                   ('"text"', '-42', '0u', '(void *)h_objects', '0'))]
    # A precision-bounded %s need not contain a terminating zero. These arrays
    # end at a protected page, so strlen-before-clamping is a detectable defect.
    for size in (1, 7, 42, 4096):
        for precision in (0, size):
            cases.append(Case(f'[%10.{precision}s]', ('h_string',),
                              f'ft_printf("[%10.{precision}s]", {size} bytes without a terminator)',
                              size, False))
    return list(dict.fromkeys(cases))


def sign_cases():
    cases = []
    for conversion in 'di':
        for flags in ('+', ' ', '+ ', ' +'):
            for arg in ('0', '42', '-42', '2147483647', 'INT_MIN'):
                cases.append(Case('%' + flags + conversion, (arg,)))
    for conversion in 'xX':
        for arg in ('0u', '1u', '15u', '16u', '0xabcdefu', '4294967295u'):
            cases.append(Case('%#' + conversion, (arg,)))
    cases.append(Case('%+d|% i|%#x|%#X', ('42', '-42', '0xabcdefu', '0u')))
    return list(dict.fromkeys(cases))


def describe(case):
    if case.note:
        return case.note
    shown = case.format.encode('unicode_escape').decode('ascii')
    if len(shown) > 55:
        shown = shown[:52] + '...'
    args = ', '.join(arg if len(arg) <= 32 else arg[:29] + '...' for arg in case.arguments)
    return f'ft_printf("{shown}"' + (', ' + args if args else '') + ')'
