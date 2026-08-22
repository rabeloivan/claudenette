import time

from rich.console import Console
from rich.markup import escape
from rich.text import Text

# CLAUDENETTE_ART prints at 92 columns wide - used as the fixed delimiter for
# every centered/wrapped line in this file, so output looks the same
# regardless of the real terminal's width.
BANNER_WIDTH = 92

console = Console(width=BANNER_WIDTH)

CLAUDENETTE_ART = r"""
 ▄████▄   ██▓    ▄▄▄       █    ██ ▓█████▄ ▓█████  ███▄    █ ▓█████▄▄▄█████▓▄▄▄█████▓▓█████ 
▒██▀ ▀█  ▓██▒   ▒████▄     ██  ▓██▒▒██▀ ██▌▓█   ▀  ██ ▀█   █ ▓█   ▀▓  ██▒ ▓▒▓  ██▒ ▓▒▓█   ▀ 
▒▓█    ▄ ▒██░   ▒██  ▀█▄  ▓██  ▒██░░██   █▌▒███   ▓██  ▀█ ██▒▒███  ▒ ▓██░ ▒░▒ ▓██░ ▒░▒███   
▒▓▓▄ ▄██▒▒██░   ░██▄▄▄▄██ ▓▓█  ░██░░▓█▄   ▌▒▓█  ▄ ▓██▒  ▐▌██▒▒▓█  ▄░ ▓██▓ ░ ░ ▓██▓ ░ ▒▓█  ▄ 
▒ ▓███▀ ░░██████▒▓█   ▓██▒▒▒█████▓ ░▒████▓ ░▒████▒▒██░   ▓██░░▒████▒ ▒██▒ ░   ▒██▒ ░ ░▒████▒
░ ░▒ ▒  ░░ ▒░▓  ░▒▒   ▓▒█░░▒▓▒ ▒ ▒  ▒▒▓  ▒ ░░ ▒░ ░░ ▒░   ▒ ▒ ░░ ▒░ ░ ▒ ░░     ▒ ░░   ░░ ▒░ ░
  ░  ▒   ░ ░ ▒  ░ ▒   ▒▒ ░░░▒░ ░ ░  ░ ▒  ▒  ░ ░  ░░ ░░   ░ ▒░ ░ ░  ░   ░        ░     ░ ░  ░
░          ░ ░    ░   ▒    ░░░ ░ ░  ░ ░  ░    ░      ░   ░ ░    ░    ░        ░         ░   
░ ░          ░  ░     ░  ░   ░        ░       ░  ░         ░    ░  ░                    ░  ░
░                                   ░                                                       
"""


def print_header():
    lines = CLAUDENETTE_ART.strip("\n").split("\n")
    for line in lines:
        console.print(Text(line, style="orange3"))

    print()
    msg = "Claudenette version 1.0.0 (Aug 2026)"
    console.print(Text(f"{msg:^{BANNER_WIDTH}s}", style="italic bright_black"))
    print()
    console.print(Text("-" * BANNER_WIDTH, style="bright_black"))
    print()
    time.sleep(1)


def print_command_execution(command):
    console.print(f"[bright_black]Executing: {escape(command)}[/bright_black]", highlight=False)


def _wrap_styled_entries(prefix, entries, width):
    # entries: list of (plain, styled) pairs, e.g. ("ex00: OK",
    # "[sea_green2]ex00: OK[/sea_green2]") - a summary line's entries are
    # comma-joined, and some real status values (e.g. "FORBIDDEN FN",
    # "EXTRA FILES") contain their own internal space, so a generic
    # textwrap.wrap() over the joined text can split *inside* one entry
    # (confirmed empirically - "abaajdbjhfaf:" / "FORBIDDEN FN," landed on
    # two different lines). Wrapping is done here instead, entry-by-entry,
    # so a "name: status" pair can never be split across lines - and on the
    # *plain* text specifically, since rich markup tags would otherwise
    # count toward the measured width and wrap too early.
    if not entries:
        return [prefix.rstrip()]
    indent = " " * len(prefix)
    last = len(entries) - 1
    lines = []
    current_plain = prefix
    current_styled = prefix
    first_on_line = True
    for i, (plain, styled) in enumerate(entries):
        suffix = "," if i < last else ""
        plain_token = plain + suffix
        styled_token = styled + suffix
        add_plain = plain_token if first_on_line else f" {plain_token}"
        add_styled = styled_token if first_on_line else f" {styled_token}"
        if not first_on_line and len(current_plain) + len(add_plain) > width:
            lines.append(current_styled)
            current_plain = indent + plain_token
            current_styled = indent + styled_token
        else:
            current_plain += add_plain
            current_styled += add_styled
        first_on_line = False
    lines.append(current_styled)
    return lines


def print_rush00_summary(variant_results, score):
    # rush00's real grading is a per-team random draw across 5 variants
    # with a >100% bonus mechanic - the only project in the codebase with
    # either property - so it gets its own Result/Final score/Status
    # block (mirroring print_final_summary's layout) instead of folding
    # into the generic one-name-per-mapping-key summary, which can only
    # ever show a single hardcoded "rush00" label and a 0-100 score.
    console.print(Text("-" * BANNER_WIDTH, style="bright_black"))
    print()

    prefix = "Result:      "
    if variant_results:
        entries = []
        for variant, passed in variant_results:
            color = "sea_green2" if passed else "deep_pink2"
            status = "OK" if passed else "KO"
            plain = f"rush0{variant}: {status}"
            entries.append((plain, f"[{color}]{plain}[/{color}]"))
        for line in _wrap_styled_entries(prefix, entries, BANNER_WIDTH):
            console.print(line)
    else:
        console.print(f"{prefix}[deep_pink2]rush00: ABSENT[/deep_pink2]")

    color = "sea_green2" if score > 0 else "deep_pink2"
    console.print(f"Final score: [{color}]{score}%[/{color}]", highlight=False)

    status_str = "PASSED" if score > 0 else "FAILED"
    console.print(f"Status:      [{color}]{status_str}[/{color}]")


def display_str(s, limit=80):
    truncated = len(s) > limit
    shown = s[:limit] if truncated else s
    escaped = shown.encode("unicode_escape").decode("utf-8")
    if truncated:
        return f"'{escaped}...' ({len(s)} chars total)"
    return f"'{escaped}'"


def _wrap_words(text, first_line_budget, width):
    # Plain greedy word-wrap, except a continuation line always gets exactly
    # one leading space (never rstripped later) rather than starting flush
    # left - confirmed against real reference output (3 of 4 worked examples
    # wrap exactly this way: the break line has no trailing space, the next
    # line starts with a single space, distinguishing it from a brand new
    # test line). A single word longer than `width` is left to overflow on
    # its own line rather than being broken mid-word.
    words = text.split(" ")
    lines = []
    current = ""
    budget = first_line_budget
    for word in words:
        candidate = current + (" " if current else "") + word
        if current and len(candidate) > budget:
            lines.append(current)
            current = word
            budget = width - 1
        else:
            current = candidate
    lines.append(current)
    return lines


def print_test_pass(index, description):
    prefix = f" ✓ [{index}] "
    lines = _wrap_words(description, BANNER_WIDTH - len(prefix), BANNER_WIDTH)
    console.print(
        f"[sea_green2]{escape(prefix)}[/sea_green2]"
        f"[sea_green2]{escape(lines[0])}[/sea_green2]",
        highlight=False,
    )
    for line in lines[1:]:
        console.print(f"[sea_green2] {escape(line)}[/sea_green2]", highlight=False)


def print_test_fail(index, description, expected=None, actual=None):
    # description stays identical to the pass case (same convention as
    # most test frameworks - the checkmark carries the pass/fail signal,
    # not the wording) - expected/actual are opt-in extras shown only when
    # the caller actually has them, so a purely structural check (e.g. "no
    # '&&' chaining") doesn't grow two blank/pointless detail lines.
    console.print(
        f"[deep_pink2] ✖ [/deep_pink2]"
        f"[deep_pink2][{index}][/deep_pink2] "
        f"[deep_pink2]{escape(description)}[/deep_pink2]",
        highlight=False,
    )
    if expected is not None:
        console.print(
            f"       [deep_pink2]expected:[/deep_pink2] {escape(display_str(str(expected), limit=200))}",
            highlight=False,
        )
    if actual is not None:
        console.print(
            f"       [deep_pink2]got:     [/deep_pink2] {escape(display_str(str(actual), limit=200))}",
            highlight=False,
        )


def print_exercise_result(exercise_name, passed, total):
    exercise_name = escape(exercise_name)
    if total == 0:
        console.print(
            f"[bold black on deep_pink2] FAIL [/bold black on deep_pink2] {exercise_name} (0 tests executed)\n"
        )
        return

    percent = (passed / total) * 100

    if percent == 100:
        console.print(
            f"[bold black on sea_green2] PASS [/bold black on sea_green2] {exercise_name} ({passed}/{total})\n"
        )
    else:
        console.print(
            f"[bold black on deep_pink2] FAIL [/bold black on deep_pink2] {exercise_name} ({passed}/{total})\n"
        )


def print_final_summary(results):
    console.print(Text("-" * BANNER_WIDTH, style="bright_black"))

    entries = []
    total_exercises = len(results)
    passed_for_score = 0
    counting_score = True

    for name, status in results:
        color = "sea_green2" if status == "OK" else "deep_pink2"
        plain = f"{name}: {status}"
        entries.append((plain, f"[{color}]{escape(name)}: {status}[/{color}]"))

        if status == "OK":
            if counting_score:
                passed_for_score += 1
        else:
            counting_score = False

    print()
    for line in _wrap_styled_entries("Result:      ", entries, BANNER_WIDTH):
        console.print(line)

    score = (
        int((passed_for_score / total_exercises) * 100) if total_exercises > 0 else 0
    )
    color = "sea_green2" if score >= 50 else "deep_pink2"
    console.print(f"Final score: [{color}]{score}/100[/{color}]", highlight=False)

    status_str = "PASSED" if score >= 50 else "FAILED"
    console.print(f"Status:      [{color}]{status_str}[/{color}]")
