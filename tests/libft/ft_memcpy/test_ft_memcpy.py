from ..harness_runner import run_harness_cases

FUNCTION = "ft_memcpy"

SRC = list(range(16))


def _dump(byte_values):
    return "".join(f"{b:02x}" for b in byte_values)


def _after(dst_start, src_start, n):
    buf = [0xAA] * 16
    for i in range(n):
        buf[dst_start + i] = SRC[src_start + i]
    return _dump(buf) + "|R1"


def run_libft_ft_memcpy(student_file):
    cases = [
        (["0"], None, _after(0, 0, 16),
         "copying 16 bytes, including the NUL at src[0]"),
        (["1"], None, _after(4, 8, 4),
         "copying a 4-byte slice into the middle of dst"),
        (["2"], None, _dump([0xAA] * 16) + "|R1", "n of 0 copies nothing"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
