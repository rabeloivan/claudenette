import base64
import struct

from utils.ui import print_exercise_result, print_test_fail, print_test_pass


def _parse_ssh_ed25519_pub(line):
    # Returns the raw 32-byte public key, or None if the line isn't a
    # well-formed "ssh-ed25519 <base64>" key per the SSH wire format
    # (RFC 4253/8709): a length-prefixed "ssh-ed25519" string, then a
    # length-prefixed 32-byte key, and nothing else.
    parts = line.strip().split(None, 2)
    if len(parts) < 2 or parts[0] != "ssh-ed25519":
        return None
    try:
        blob = base64.b64decode(parts[1], validate=True)
    except Exception:
        return None
    if len(blob) < 4:
        return None
    (type_len,) = struct.unpack(">I", blob[:4])
    if 4 + type_len > len(blob) or blob[4:4 + type_len] != b"ssh-ed25519":
        return None
    rest = blob[4 + type_len:]
    if len(rest) < 4:
        return None
    (key_len,) = struct.unpack(">I", rest[:4])
    if key_len != 32 or len(rest) != 4 + key_len:
        return None
    return rest[4:4 + key_len]


def run_shell00_ex03(student_file):
    i = 0
    passed = 0

    def check(condition, description, expected=None, actual=None):
        nonlocal i, passed
        i += 1
        if condition:
            print_test_pass(i, f"{description} as expected")
            passed += 1
        else:
            print_test_fail(
                i, f"{description} not as expected", expected=expected, actual=actual
            )

    with open(student_file, "rb") as f:
        raw = f.read()
    content = raw.decode("latin-1")
    lines = [line for line in content.splitlines() if line.strip()]

    check(
        len(lines) == 1,
        "file contains exactly one non-blank line",
        expected="1",
        actual=str(len(lines)),
    )

    key_bytes = _parse_ssh_ed25519_pub(lines[0]) if lines else None
    check(
        key_bytes is not None,
        "line is a well-formed 'ssh-ed25519 <base64>' public key",
        actual=lines[0] if lines else "<empty file>",
    )
    if key_bytes is not None:
        check(
            len(key_bytes) == 32,
            "decoded key length (ed25519) 32 bytes",
            expected="32 bytes",
            actual=f"{len(key_bytes)} bytes",
        )

    print_exercise_result(student_file, passed, i)
    return passed == i
