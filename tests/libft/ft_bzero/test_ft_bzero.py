from ..harness_runner import run_harness_cases

FUNCTION = "ft_bzero"


def _dump(byte_values):
    return "".join(f"{b:02x}" for b in byte_values)


def _zeroed(start, length):
    buf = [0xAA] * 16
    for i in range(start, start + length):
        buf[i] = 0x00
    return _dump(buf)


def run_libft_ft_bzero(student_file):
    cases = [
        (["0"], None, _zeroed(3, 8),
         "zeroes exactly n bytes from s, leaving the rest untouched"),
        (["1"], None, _dump([0xAA] * 16), "n of 0 writes nothing"),
        (["2"], None, _zeroed(0, 16), "zeroing the whole buffer"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
