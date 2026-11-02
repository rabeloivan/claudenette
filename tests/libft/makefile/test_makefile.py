import os
import shutil

from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

from ..build_utils import (
    archive_defines,
    archive_is_ar,
    mentions_libtool,
    run_make,
    seeded_copy,
)

NAME = "libft.a"


def _turned_in(student_dir):
    """Every ft_*.c file belongs in the normal library build (subject 19.3)."""
    return [
        name[:-2] for name in sorted(os.listdir(student_dir))
        if name.startswith("ft_") and name.endswith(".c")
    ]


def run_libft_makefile(student_file):
    student_dir = os.path.dirname(os.path.abspath(student_file)) or "."
    build_dir = seeded_copy(student_dir)
    lib_path = os.path.join(build_dir, NAME)

    passed_count = 0
    total_count = 0

    def check(condition, description, detail=None):
        nonlocal passed_count, total_count
        total_count += 1
        if condition:
            print_test_pass(total_count, description)
            passed_count += 1
        else:
            print_test_fail(total_count, description, actual=detail)

    try:
        print_command_execution("make (in a scratch copy of the sources)")

        # The flags are read from `make -n` on the untouched tree, which lists
        # every command the build would run - @-silenced recipes included - and
        # compared token by token, so -Walloc-zero is not taken for -Wall. The
        # subject asks for "-Wall, -Wextra, and -Werror, using cc", nothing
        # more: printing the commands and that exact order are C09 ex01's own
        # rules ("in that order"), and holding libft to them graded a silent
        # Makefile, or `-Werror -Wall -Wextra`, KO.
        dry_output, _ = run_make(build_dir, ["-n"])
        dry_tokens = set(dry_output.split())

        # 1. bare `make` - the default target must build the library
        output, code = run_make(build_dir)
        check(code == 0, "bare `make` exits successfully", detail=output.strip()[-300:])
        check(os.path.exists(lib_path), f"bare `make` produces {NAME} at the root")
        check(
            {"-Wall", "-Wextra", "-Werror"} <= dry_tokens,
            "compile commands use -Wall, -Wextra and -Werror",
            detail=dry_output.strip()[:300],
        )
        # "it is forbidden [...] to compile your code with the -std=c99 flag"
        check(
            "-std=c99" not in dry_tokens,
            "compile commands do not use -std=c99, which the subject forbids",
            detail=dry_output.strip()[:300],
        )

        # 2. the library is an ar archive, not a libtool one
        check(
            archive_is_ar(lib_path),
            f"{NAME} is an ar archive whose members can be listed",
        )
        check(
            not mentions_libtool(os.path.join(build_dir, "Makefile")),
            "the Makefile does not invoke libtool, which the subject forbids",
        )
        missing = sorted(set(_turned_in(student_dir)) - archive_defines(lib_path))
        check(
            not missing,
            f"{NAME} defines every mandatory function turned in",
            detail="missing from the archive: " + ", ".join(missing) if missing else None,
        )

        # 3. no unnecessary relinking - "your Makefile must not perform
        #    unnecessary relinking" is a Common Instruction, and a second
        #    `make` on an unchanged tree must not rebuild the archive.
        before = os.path.getmtime(lib_path) if os.path.exists(lib_path) else 0
        second_output, _ = run_make(build_dir)
        after = os.path.getmtime(lib_path) if os.path.exists(lib_path) else 0
        check(
            before == after,
            "a second `make` on an unchanged tree does not relink",
            detail=second_output.strip()[:300],
        )

        # 4. the four rules the subject names, checked by behaviour
        _, code = run_make(build_dir, ["clean"])
        objects = [n for n in os.listdir(build_dir) if n.endswith(".o")]
        check(code == 0, "`make clean` exits successfully")
        check(not objects, "`make clean` removes the .o files")
        check(os.path.exists(lib_path), f"`make clean` leaves {NAME} in place")

        _, code = run_make(build_dir, ["fclean"])
        check(code == 0, "`make fclean` exits successfully")
        check(not os.path.exists(lib_path), f"`make fclean` also removes {NAME}")

        output, code = run_make(build_dir, ["re"])
        check(code == 0, "`make re` exits successfully from a clean tree")
        check(os.path.exists(lib_path), f"`make re` rebuilds {NAME}")

        run_make(build_dir, ["fclean"])
        _, code = run_make(build_dir, ["all"])
        check(code == 0, "`make all` exits successfully")
        check(os.path.exists(lib_path), f"explicit `make all` also builds {NAME}")

        # "Your Makefile must contain at least the rules $(NAME), all, clean,
        # fclean and re" - $(NAME) is the one rule nothing above invokes.
        run_make(build_dir, ["fclean"])
        _, code = run_make(build_dir, [NAME])
        check(
            code == 0 and os.path.exists(lib_path),
            f"`make {NAME}` (the $(NAME) rule) builds the library",
        )

        print_exercise_result("Makefile", passed_count, total_count)
        return passed_count == total_count

    finally:
        shutil.rmtree(build_dir, ignore_errors=True)
