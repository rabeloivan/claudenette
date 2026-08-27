import re
import subprocess

from utils.ui import (
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

from ...shell_utils import run_sh

MAC_RE = re.compile(r"^[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5}$")


def run_shell01_ex04(student_file):
    i = 0
    passed = 0

    def check(condition, description, expected=None, actual=None, show_value=None):
        nonlocal i, passed
        i += 1
        if condition:
            if show_value is not None:
                print_test_pass(i, f"{description} {show_value} as expected")
            else:
                print_test_pass(i, f"{description} as expected")
            passed += 1
        else:
            print_test_fail(
                i, f"{description} not as expected", expected=expected, actual=actual
            )

    # The real machine's own MAC addresses as ground truth (same
    # real-tool-as-oracle approach as C10's hexdump) - not a fixture, since
    # there's nothing to fake here, only this machine's real interfaces.
    #
    # Take the field immediately AFTER "ether", not the last field on the
    # line. macOS prints
    #     ether 7e:66:1b:f3:93:f4
    # where those happen to be the same token, but Linux prints
    #     ether 7e:66:1b:f3:93:f4  txqueuelen 0  (Ethernet)
    # so the last field is "(Ethernet)". Comparing against that made this test
    # fail every correct submission on Linux - i.e. on the platform 42's own
    # moulinette runs - while passing on the author's Mac.
    ifconfig_out = subprocess.run(
        ["ifconfig"], capture_output=True, text=True, timeout=5
    ).stdout

    expected = set()
    for line in ifconfig_out.splitlines():
        fields = line.split()
        if "ether" in fields:
            at = fields.index("ether")
            if at + 1 < len(fields):
                expected.add(fields[at + 1])

    actual, err, code = run_sh(student_file)
    actual_lines = [line for line in actual.splitlines() if line]
    actual_set = set(actual_lines)

    check(
        actual_set == expected,
        "this machine's real MAC addresses (as a set)",
        expected=sorted(expected),
        actual=sorted(actual_set),
        show_value=sorted(actual_set),
    )
    check(
        all(MAC_RE.match(line) for line in actual_lines),
        "every line is a well-formed MAC address (xx:xx:xx:xx:xx:xx), nothing extra",
    )

    print_exercise_result(student_file, passed, i)
    return passed == i
