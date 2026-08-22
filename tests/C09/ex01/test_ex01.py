import os
import shutil
import subprocess
import tempfile

from utils.ui import print_command_execution, print_exercise_result, print_test_fail, print_test_pass

SRCS = ["ft_putchar.c", "ft_swap.c", "ft_putstr.c", "ft_strlen.c", "ft_strcmp.c"]


def run_make(cwd, args=None, timeout=10):
    try:
        result = subprocess.run(
            ["make"] + (args or []),
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout + result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", -1


def has_fresh_compile(output):
    return "cc" in output and "-c" in output


def flags_in_order(output):
    idx_wall = output.find("-Wall")
    idx_wextra = output.find("-Wextra")
    idx_werror = output.find("-Werror")
    return 0 <= idx_wall < idx_wextra < idx_werror


def run_C09_ex01(student_file):
    fixture_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixture")
    test_env = tempfile.mkdtemp(prefix="claudenette_c09_ex01_")

    try:
        shutil.copytree(os.path.join(fixture_dir, "srcs"), os.path.join(test_env, "srcs"))
        shutil.copytree(os.path.join(fixture_dir, "includes"), os.path.join(test_env, "includes"))
        shutil.copy(student_file, os.path.join(test_env, "Makefile"))

        print_command_execution(f"make (in a scratch dir seeded with our own srcs/+includes/)")

        lib_path = os.path.join(test_env, "libft.a")
        obj_paths = [os.path.join(test_env, "srcs", n.replace(".c", ".o")) for n in SRCS]

        passed_count = 0
        total_count = 0

        def check(condition, description):
            nonlocal passed_count, total_count
            total_count += 1
            if condition:
                print_test_pass(total_count, description)
                passed_count += 1
            else:
                print_test_fail(total_count, description)

        # 1. fresh build via bare `make`
        output, code = run_make(test_env)
        check(code == 0, "bare `make` exits successfully")
        check(os.path.exists(lib_path), "bare `make` produces libft.a at the exercise root")
        check(
            all(os.path.exists(p) for p in obj_paths),
            "bare `make` produces .o files inside srcs/ (near their .c files)",
        )
        check(has_fresh_compile(output), "`make` prints the compile commands it runs (not @-silenced)")
        check(flags_in_order(output), "compile commands show -Wall, -Wextra, -Werror in that order")

        # 2. no-op rebuild
        output2, code2 = run_make(test_env)
        check(code2 == 0, "a second `make` (nothing changed) exits successfully")
        check(
            not has_fresh_compile(output2),
            "a second `make` (nothing changed) runs no unnecessary compile commands",
        )

        # 3. make clean
        run_make(test_env, ["clean"])
        check(
            not any(os.path.exists(p) for p in obj_paths),
            "`make clean` removes the .o files",
        )
        check(os.path.exists(lib_path), "`make clean` leaves libft.a untouched")

        # 4. make fclean
        run_make(test_env, ["fclean"])
        check(not os.path.exists(lib_path), "`make fclean` also removes libft.a")

        # 5. make re (from a fully-clean state)
        output5, code5 = run_make(test_env, ["re"])
        check(code5 == 0, "`make re` exits successfully")
        check(os.path.exists(lib_path), "`make re` rebuilds libft.a from a clean state")

        # 6. explicit `make all` after another fclean, confirming the stated equivalence
        run_make(test_env, ["fclean"])
        run_make(test_env, ["all"])
        check(os.path.exists(lib_path), "explicit `make all` also (re)builds libft.a")

        # 7. targeted incremental rebuild: touching one .c file should rebuild only its .o
        mtimes_before = {p: os.path.getmtime(p) for p in obj_paths}
        touched = obj_paths[0].replace(".o", ".c")
        # Set an explicitly future mtime rather than sleeping - a real sleep
        # can still land within the same mtime granularity window as the
        # just-finished build on some filesystems, which would make `make`
        # wrongly see the touched file as not newer than its .o.
        future = max(mtimes_before.values()) + 5
        os.utime(touched, (future, future))
        output7, code7 = run_make(test_env)
        mtimes_after = {p: os.path.getmtime(p) for p in obj_paths}
        only_first_rebuilt = (
            mtimes_after[obj_paths[0]] != mtimes_before[obj_paths[0]]
            and all(mtimes_after[p] == mtimes_before[p] for p in obj_paths[1:])
        )
        check(
            only_first_rebuilt,
            "touching a single .c file rebuilds only its own .o, not the others",
        )

        print_exercise_result("ex01/Makefile", passed_count, total_count)
        return passed_count == total_count

    finally:
        shutil.rmtree(test_env, ignore_errors=True)
