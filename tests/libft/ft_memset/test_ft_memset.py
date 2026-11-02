from ..harness_runner import run_harness_cases

FUNCTION = "ft_memset"

AA = "aa"


def _dump(byte_values):
    return "".join(f"{b:02x}" for b in byte_values)


def _case(prefix, fill_byte, start, length):
    buf = [0xAA] * 16
    for i in range(start, start + length):
        buf[i] = fill_byte
    return _dump(buf) + "|R1"


def run_libft_ft_memset(student_file):
    cases = [
        (["0"], None, _case(AA, 0x5A, 2, 10),
         "fills exactly len bytes from b, leaving the rest untouched"),
        (["1"], None, _dump([0xAA] * 16) + "|R1",
         "len of 0 writes nothing"),
        (["2"], None, _dump([0x41] * 16) + "|R1",
         "c is converted to unsigned char (0x141 writes 0x41)"),
        (["3"], None, _dump([0x00] * 16) + "|R1",
         "filling the whole buffer with 0"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
