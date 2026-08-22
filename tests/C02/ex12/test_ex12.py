import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def format_line(addr, chunk):
    hex_groups = []
    for g in range(8):
        idx0 = g * 2
        idx1 = g * 2 + 1
        if idx1 < len(chunk):
            hex_groups.append(f"{chunk[idx0]:02x}{chunk[idx1]:02x}")
        elif idx0 < len(chunk):
            hex_groups.append(f"{chunk[idx0]:02x}  ")
        else:
            hex_groups.append("    ")
    hex_col = " ".join(hex_groups)
    ascii_col = "".join(chr(b) if 0x20 <= b <= 0x7E else "." for b in chunk)
    return f"{addr:016x}: {hex_col} {ascii_col}"


def expected_lines(mem_bytes, base_addr):
    lines = []
    for offset in range(0, len(mem_bytes), 16):
        chunk = mem_bytes[offset : offset + 16]
        lines.append(format_line(base_addr + offset, chunk))
    return lines


def run_C02_ex12(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex12_harness.c")
    exe_path = "./print_memory"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        list(b"Hello, World!"),
        list(range(20)),
        list(b"A" * 32),
        [],
        [0x00, 0x01, 0x02, 0xFF, 0xFE, 0x7F, 0x20, 0x7E],
        list(b"X" * 100),
        list(b"Y" * 17),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, mem_bytes in enumerate(test_cases, 1):
        size = len(mem_bytes)
        content_str = "".join(chr(b) for b in mem_bytes)
        input_str = f"{size}\n{content_str}"
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_print_memory(addr, size={size})"

        marker = actual[-2] if len(actual) >= 2 else ""
        dump = actual[:-2] if len(actual) >= 2 else actual
        ptr_ok = marker == "1"

        expected_display = "(nothing, size=0)"
        if size == 0:
            content_ok = dump == ""
        else:
            lines = dump.split("\n")
            if lines and lines[-1] == "":
                lines = lines[:-1]
            content_ok = False
            expected_display = "(unparseable - no 16-hex-digit address on the first line)"
            if lines and len(lines[0]) >= 16:
                try:
                    base_addr = int(lines[0][:16], 16)
                except ValueError:
                    base_addr = None
                if base_addr is not None:
                    expected = expected_lines(mem_bytes, base_addr)
                    content_ok = lines == expected
                    expected_display = "\n".join(expected)

        if ptr_ok and content_ok:
            print_test_pass(i, f"{desc}: return value and memory dump as expected")
            passed_count += 1
        elif not ptr_ok:
            print_test_fail(i, f"{desc}: did not return addr (return value mismatch)")
        else:
            print_test_fail(
                i,
                f"{desc}: memory dump not as expected",
                expected=expected_display,
                actual=dump,
            )

    print_exercise_result("ex12/ft_print_memory.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
