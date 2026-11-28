"""Deterministic text inputs, from elementary cases to boundary cases."""


def file_cases(buffer_size):
    cases = [
        ('empty file returns NULL, including repeated EOF calls', b''),
        ('one character without a newline', b'x'),
        ('a newline by itself', b'\n'),
        ('one character followed by a newline', b'x\n'),
        ('five empty lines', b'\n' * 5),
        ('two lines and a final line without a newline', b'hello\nworld\nlast'),
        ('all lines include their final newline', b'hello\nworld\nlast\n'),
        ('empty lines mixed with text lines', b'\nalpha\n\nbeta\n\nend'),
        ('spaces, tabs and carriage returns are preserved', b' \t \r\n\tend\r'),
        ('UTF-8 bytes survive chunk boundaries', 'ação\nété\n終わり'.encode()),
    ]
    # Keep large buffers affordable. Small buffers exercise both sides of each
    # boundary, including newline placement across successive reads.
    sizes = sorted({9, 10, 11, 41, 42, 43, *(
        [buffer_size - 1, buffer_size, buffer_size + 1]
        if buffer_size is not None and buffer_size <= 9999 else []
    )} - {0})
    for size in sizes:
        text = bytes(65 + i % 26 for i in range(size))
        cases.append((f'{size}-byte line without a newline', text))
        cases.append((f'{size}-byte line, newline, then another line', text + b'\nz\n'))
    cases.extend([
        ('a 20,000-byte line ending at EOF', b'x' * 20000),
        ('a 20,000-byte line followed by short and empty lines', b'y' * 20000 + b'\nend\n\n'),
        ('256 lines of varying lengths', b''.join(
            bytes([65 + i % 26]) * (i % 80) + b'\n' for i in range(256))),
    ])
    return cases
