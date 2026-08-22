import os
import subprocess

from utils.compiler import compile_source
from utils.functions import check_allowed_functions
from utils.norminette import check_norminette
from utils.runner import run_test_case
from utils.ui import (
    display_str,
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

SIBLINGS = ["ft_putchar.c", "ft_swap.c", "ft_putstr.c", "ft_strlen.c", "ft_strcmp.c"]


def run_C09_ex00(student_file):
    student_dir = os.path.dirname(student_file)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex00_harness.c")

    sibling_paths = [os.path.join(student_dir, name) for name in SIBLINGS]
    missing = [name for name, path in zip(SIBLINGS, sibling_paths) if not os.path.exists(path)]
    if missing:
        print()
        print_test_fail(1, f"missing required file(s): {', '.join(missing)}")
        print_exercise_result("ex00/libft_creator.sh", 0, 1)
        return False

    norm_ok = all(check_norminette(path) for path in sibling_paths)
    fns_ok = all(check_allowed_functions(path, ["write"]) for path in sibling_paths)

    lib_path = os.path.join(student_dir, "libft.a")
    if os.path.exists(lib_path):
        os.remove(lib_path)

    print_command_execution("sh libft_creator.sh")
    try:
        script_result = subprocess.run(
            ["sh", "libft_creator.sh"],
            cwd=student_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        print_test_fail(1, "libft_creator.sh timed out")
        print_exercise_result("ex00/libft_creator.sh", 0, 1)
        return False

    if not os.path.exists(lib_path):
        print_test_fail(
            1,
            f"libft_creator.sh did not produce libft.a "
            f"(stderr: {display_str(script_result.stderr)})",
        )
        print_exercise_result("ex00/libft_creator.sh", 0, 1)
        return False

    exe_path = "./libft_link_test"
    compiled = compile_source([harness_path, lib_path], exe_path)

    for name in os.listdir(student_dir):
        if name.endswith(".o"):
            os.remove(os.path.join(student_dir, name))

    if not compiled:
        os.remove(lib_path)
        return False

    print_command_execution(exe_path)

    expected = "ABCSWAPOK5CMPOK"
    actual, err, code = run_test_case(exe_path, input_data="")
    desc = "libft.a linked against a harness (ft_putchar/ft_swap/ft_putstr/ft_strlen/ft_strcmp)"

    passed = actual == expected
    if passed:
        print_test_pass(1, f"{desc}: behaved correctly, output {display_str(actual)} as expected")
    else:
        print_test_fail(
            1, f"{desc}: output not as expected", expected=expected, actual=actual
        )

    print_exercise_result("ex00/libft_creator.sh", 1 if passed else 0, 1)

    if os.path.exists(exe_path):
        os.remove(exe_path)
    if os.path.exists(lib_path):
        os.remove(lib_path)

    return passed and norm_ok and fns_ok
