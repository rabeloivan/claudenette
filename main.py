import importlib
import os
import re
import sys
import time

from rich.console import Console

from utils.extra_files import check_no_extra_files
from utils.functions import check_allowed_functions
from utils.norminette import check_norminette
from utils.ui import BANNER_WIDTH, print_final_summary, print_header

console = Console(width=BANNER_WIDTH)


def get_current_exercise_mapping():
    current_dir = os.path.basename(os.getcwd())

    project_names = {"rush00", "rush01", "rush02", "bsq", "shell00", "shell01"}

    if re.match(r"^C(0[0-9]|1[0-3])$", current_dir):
        package_name = current_dir
    elif current_dir.lower() in project_names:
        # Project directories (unlike C00-C13) aren't consistently cased
        # across campuses/students (e.g. "Rush00") - the package on disk is
        # lowercase, so normalize for the import while still reporting the
        # user's actual directory name everywhere else.
        package_name = current_dir.lower()
    else:
        return None, current_dir

    try:
        module = importlib.import_module(f"tests.{package_name}")
        mapping = module.get_mapping()
        return mapping, current_dir

    except ImportError:
        error_msg = f"Error: Could not load configuration for '{current_dir}'."
        fix_msg = f"Make sure '~/Claudenette/tests/{package_name}/__init__.py' exists."
        console.print(f"[deep_pink2]{error_msg:^{BANNER_WIDTH}s}[/deep_pink2]")
        console.print(f"[white]{fix_msg:^{BANNER_WIDTH}s}[/white]")
        sys.exit(1)

    except AttributeError:
        error_msg = f"Error: {current_dir} module is missing 'get_mapping()' function."
        console.print(f"[deep_pink2]{error_msg:^{BANNER_WIDTH}s}[/deep_pink2]")
        sys.exit(1)


if __name__ == "__main__":
    print_header()

    test_map, dir_name = get_current_exercise_mapping()

    if test_map is None:
        error_msg = (
            f"Current directory '{dir_name}' does not match expected pattern "
            "(C00~13, rush00, rush01, bsq, shell00, shell01)."
        )
        fix_msg = "Please navigate to an appropriate directory to run tests."
        console.print(f"[deep_pink2]{error_msg:^{BANNER_WIDTH}s}[/deep_pink2]")
        console.print(f"[white]{fix_msg:^{BANNER_WIDTH}s}[/white]")
        sys.exit(1)

    if re.match(r"^C(0[0-9]|1[0-3])$", dir_name):
        display_name = f"{dir_name[0]} {dir_name[1:]}"
    else:
        display_name = dir_name
    targets = sys.argv[1:]
    sorted_paths = sorted(test_map.keys())

    if targets:
        filtered_paths = []

        for path in sorted_paths:
            if any(t in path for t in targets):
                filtered_paths.append(path)

        if not filtered_paths:
            error_msg = f"No exercises matched '{' '.join(targets)}'."
            console.print(f"[deep_pink2]{error_msg:^{BANNER_WIDTH}s}[/deep_pink2]")
            sys.exit(1)

        sorted_paths = filtered_paths

    console.print(
        f"[sea_green2]{'Generating test for ' + display_name + '...':^{BANNER_WIDTH}s}[/sea_green2]",
        highlight=False,
    )
    print()

    start_time = time.time()
    results = []
    last_was_grouped = False

    for student_file_path in sorted_paths:
        mapping_entry = test_map[student_file_path]
        if len(mapping_entry) == 4:
            ex_name, run_func, allowed_fns, options = mapping_entry
        else:
            ex_name, run_func, allowed_fns = mapping_entry
            options = {}
        extra_norm_rules = options.get("norm_rules")
        extra_compile_flags = options.get("compile_flags")
        skip_precheck = options.get("skip_precheck", False)
        extra_allowed_files = options.get("allowed_files")

        if not os.path.exists(student_file_path):
            if not last_was_grouped:
                console.print("-" * BANNER_WIDTH, style="bright_black")
                print()

            console.print(f"[deep_pink2]Missing file: {student_file_path}[/deep_pink2]")
            results.append((ex_name, "ABSENT"))
            print()
            last_was_grouped = True
            continue

        if run_func is None:
            if not last_was_grouped:
                console.print("-" * BANNER_WIDTH, style="bright_black")
                print()

            console.print(
                f"[yellow]Test for {student_file_path} not implemented yet.[/yellow]"
            )
            results.append((ex_name, "TODO"))
            print()
            last_was_grouped = True
            continue

        last_was_grouped = False
        console.print("-" * BANNER_WIDTH, style="bright_black")
        print()

        # "You must not leave any additional files..." applies regardless
        # of whether this exercise is C at all, so this check is entirely
        # independent of skip_precheck. Directory-keyed mappings (rush01's
        # "ex00", bsq's ".") have no single "the primary file" to default
        # to, so they rely entirely on an explicit allowed_files pattern
        # list; a file-keyed mapping always at least allows itself.
        if os.path.isdir(student_file_path):
            check_dir = student_file_path
            allowed_set = extra_allowed_files
        else:
            check_dir = os.path.dirname(student_file_path) or "."
            allowed_set = [os.path.basename(student_file_path)] + list(extra_allowed_files or [])

        files_passed = check_no_extra_files(check_dir, allowed_set) if allowed_set else True

        if skip_precheck:
            # Norminette and "allowed functions" are C-specific concepts
            # (style rules, nm -u on a compiled object) - for an exercise
            # whose deliverable isn't C at all (a shell one-liner, a
            # filesystem artifact), running them isn't just unnecessary,
            # it's a category error, even though they happen to no-op
            # harmlessly rather than misfire. Real moulinette doesn't apply
            # either check to these exercises, so this tester shouldn't
            # either - skip both entirely instead of relying on the no-op.
            norm_passed = True
            fns_passed = True
        else:
            norm_passed = check_norminette(student_file_path, extra_rules=extra_norm_rules)
            fns_passed = check_allowed_functions(
                student_file_path, allowed_fns, extra_flags=extra_compile_flags
            )
        tests_passed = run_func(student_file_path)

        if not files_passed:
            results.append((ex_name, "EXTRA FILES"))
        elif not norm_passed:
            results.append((ex_name, "NORM ERR"))
        elif not fns_passed:
            results.append((ex_name, "FORBIDDEN FN"))
        elif not tests_passed:
            results.append((ex_name, "KO"))
        else:
            results.append((ex_name, "OK"))

    # rush00 prints its own multi-variant Result/Final score/Status block
    # inline (see run_C_rush00) since its real grading - a per-team random
    # draw across 5 variants with a >100% bonus mechanic - doesn't fit the
    # generic one-name-per-mapping-key summary below. That only happens if
    # run_func actually ran though (not on the "ABSENT"/"TODO" early-exit
    # paths above, which never call it) - fall back to the generic summary
    # in those cases so a totally-empty submission still gets one.
    if dir_name.lower() == "rush00" and results and results[0][1] not in ("ABSENT", "TODO"):
        pass
    else:
        print_final_summary(results)

    elapsed = time.time() - start_time
    console.print(
        f"\n[bright_black]Test completed. Total elapsed time: {elapsed:.2f}s.[/bright_black]",
        highlight=False,
    )
    trailer = "Claudenette is a test automation tool and may make mistakes. Rely on your own tests."
    console.print(f"\n[orange3]{trailer:^{BANNER_WIDTH}s}[/orange3]", highlight=False)
