import re
from dataclasses import dataclass
from itertools import zip_longest

from rich.console import Console
from rich.markup import escape
from rich.text import Text

from utils import __version__
from utils.reporting import (
    concise_cases, current_group, current_presenter, present_case, record_case, record_summary,
    staged_report,
)

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
    msg = f"Claudenette version {__version__}"
    console.print(Text(f"{msg:^{BANNER_WIDTH}s}", style="italic bright_black"))
    print()
    console.print(Text("-" * BANNER_WIDTH, style="bright_black"))
    print()


def print_command_execution(command, failed_build=False):
    presenter = current_presenter()
    if presenter is not None:
        command = presenter.command(command)
        if command is None:
            return
    staged = staged_report()
    kind = _stage_kind(command) if staged is not None else None
    # A successful harness build is an internal step; a failed one is shown.
    if kind == 'build' and not failed_build:
        return
    group = current_group()
    if group is not None and group.symbols_name and command.startswith('nm -u '):
        command = re.sub(r'^nm -u \S+ \(', f'nm -u {group.symbols_name} sources (', command)
    if group is not None and group.norm_root is not None and command.startswith(
            ('norminette ', 'python -m norminette ')):
        if group.norm_announced:
            return
        group.norm_announced = True
        command = command.rsplit(' ', 1)[0] + ' .'
    # File prechecks have their own cache; different paths may share a basename.
    if command.startswith(('norminette ', 'python -m norminette ', 'checking ')):
        group = None
    if group is not None:
        if command in group.commands:
            return
        group.commands.add(command)
    if group is not None and not command.startswith(('cc ', 'nm ')):
        if group.announced:
            return
        group.announced = True
    if staged is not None:
        if staged.stage == kind and kind in ('norm', 'symbols'):
            return
        begin_stage(kind)
        staged.stage_fresh = False
    _print_wrapped('Executing: ', Text(command, style='bright_black'), 'bright_black')


def _stage_kind(command):
    if command.startswith('checking for extra files (turn-in:'):
        return 'project-delivery'
    if command.startswith('checking for extra files'):
        return 'delivery'
    if command.startswith(('norminette ', 'python -m norminette ')):
        return 'norm'
    if command.startswith('nm '):
        return 'symbols'
    if command.startswith('cc '):
        return 'build'
    if command == 'make' or command.startswith(('make ', 'sh libft_creator.sh')):
        return 'make'
    if command.startswith('checking '):
        return 'header'
    return 'runtime'


def begin_stage(kind, after_silent_stage=False):
    """Separate one stage of a unit from the previous stage, as ft_printf does."""
    staged = staged_report()
    if staged is None or staged.stage == kind:
        return
    gap_needed = staged.case_open or staged.blank_pending or (
        # Delivery checks print their own gap; other announcements may print nothing.
        after_silent_stage and staged.stage not in (None, 'delivery', 'project-delivery'))
    # A project-wide turn-in check stands apart from the first function's block.
    if staged.stage is not None and (staged.stages == 'delimited' or staged.stage == 'project-delivery'):
        print_test_stage(blank_before=gap_needed, reset_index=False)
        staged.stage_fresh = True
    elif gap_needed:
        console.print()
    staged.stage = kind
    staged.case_open = staged.blank_pending = False


def print_test_stage(blank_before=False, reset_index=True):
    """Separate project stages, optionally restarting their displayed numbering."""
    group = current_group()
    if group is not None and reset_index:
        group.index = 0
    if blank_before:
        console.print()
    console.print(Text('-' * BANNER_WIDTH, style='bright_black'))
    console.print()


@dataclass(frozen=True)
class CasePresentation:
    title: str
    result: str = ''
    call: str = ''
    expected: str | None = None
    actual: str | None = None
    details: tuple = ()


def print_test_section(title, separate=False):
    if concise_cases():
        staged = staged_report()
        fresh = staged is not None and staged.stage_fresh
        if staged is not None:
            staged.stage_fresh = staged.blank_pending = False
        if separate:
            print_test_stage(blank_before=True, reset_index=False)
        elif not fresh:
            console.print()
        console.print(Text(title, style='bold'))


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


def _print_wrapped(prefix, content, style):
    """Align continuation lines with the text following a command/case label."""
    for index, line in enumerate(content.wrap(console, BANNER_WIDTH - len(prefix), overflow='fold')):
        line.rstrip()
        lead = prefix if index == 0 else ' ' * len(prefix)
        rendered = Text()
        rendered.append(lead, style=style)
        rendered.append_text(line)
        console.print(rendered, soft_wrap=True, highlight=False)


def _case_description(description, passed):
    """Keep the scenario and diagnostic; give every test one result phrase."""
    text = str(description).rstrip()
    text = re.sub(r"(?::?\s+)?(?:not )?as expected(?P<stream> on stderr)?(?=[.!]?$|[,;]|\s+[-(])",
                  lambda match: match.group("stream") or "", text)
    text = text.rstrip(" :.!")
    text = re.sub(r': (?:returned|output) ', ' output ', text)
    return text + (" as expected" if passed else " not as expected")


def _case_printed():
    staged = staged_report()
    if staged is not None:
        staged.case_open = True


def print_test_pass(index, description, presentation=None):
    description = _case_description(description, True)
    index = record_case(index, True, description)
    prefix = f" ✓ [{index}] "
    if concise_cases():
        presentation = presentation or present_case(description, True)
        _case_printed()
        view = presentation or CasePresentation(description.removesuffix(' as expected'))
        if view.result:
            title_width = 44 - len(prefix)
            titles = Text(view.title).wrap(console, title_width, overflow='fold')
            values = Text(view.result).wrap(console, BANNER_WIDTH - 46, overflow='fold')
            for line, (title, value) in enumerate(zip_longest(titles, values, fillvalue='')):
                lead = prefix if line == 0 else ' ' * len(prefix)
                text = lead + str(title).ljust(title_width) + '  ' + str(value)
                console.print(Text(text.rstrip(), style='sea_green2'), soft_wrap=True)
        else:
            _print_wrapped(prefix, Text(view.title, style='sea_green2'), 'sea_green2')
        return
    _print_wrapped(prefix, Text(description, style='sea_green2'), 'sea_green2')


def print_test_fail(index, description, expected=None, actual=None, presentation=None):
    description = _case_description(description, False)
    index = record_case(index, False, description, expected, actual)
    if concise_cases():
        presentation = presentation or present_case(description, False, expected, actual)
        _case_printed()
        view = presentation or CasePresentation(
            description.removesuffix(' not as expected'),
            expected=None if expected is None else str(expected),
            actual=None if actual is None else str(actual),
        )
        _print_wrapped(f" ✖ [{index}] ", Text(view.title, style='deep_pink2'), 'deep_pink2')
        indent = ' ' * (len(str(index)) + 6)
        fields = [('Call', view.call or None), ('Expected', view.expected),
                  ('Got', view.actual if view.actual else actual), *view.details]
        width = max(len(label) for label, _ in fields)
        for label, value in fields:
            if value is not None:
                _print_wrapped(indent + (label + ':').ljust(width + 2), Text(str(value)), 'deep_pink2')
        console.print()
        return
    # Keep the scenario; show expected/actual only when the caller has them.
    _print_wrapped(f" ✖ [{index}] ", Text(description, style='deep_pink2'), 'deep_pink2')
    if expected is not None:
        _print_wrapped('       expected: ', Text(display_str(str(expected), limit=200)), 'deep_pink2')
    if actual is not None:
        _print_wrapped('       got:      ', Text(display_str(str(actual), limit=200)), 'deep_pink2')


def print_exercise_result(exercise_name, passed, total, failed=False):
    if record_summary(exercise_name, passed, total):
        return
    presenter = current_presenter()
    if presenter is not None:
        exercise_name = presenter.summary_name(exercise_name)
    staged = staged_report()
    if staged is not None:
        # The summary already ends with the gap the next block needs.
        staged.blank_pending = staged.case_open = False
        staged.stage_fresh = True
    if concise_cases():
        console.print()
    exercise_name = escape(exercise_name)
    if total == 0:
        console.print(
            f"[bold black on deep_pink2] FAIL [/bold black on deep_pink2] {exercise_name} (0 tests executed)\n"
        )
        return

    percent = (passed / total) * 100

    if percent == 100 and not failed:
        console.print(
            f"[bold black on sea_green2] PASS [/bold black on sea_green2] {exercise_name} ({passed}/{total})\n"
        )
    else:
        note = " — additional checks failed" if passed == total else ""
        console.print(
            f"[bold black on deep_pink2] FAIL [/bold black on deep_pink2] {exercise_name} ({passed}/{total}){note}\n"
        )


def _status_color(status):
    if status == "OK":
        return "sea_green2"
    if status in ("SKIPPED", "UNKNOWN"):
        return "yellow"
    return "deep_pink2"


def print_final_summary(results, bonus_names=None, compact=False):
    """Print the Result/score/Status block; returns the Status word."""
    console.print(Text("-" * BANNER_WIDTH, style="bright_black"))

    # bonus_names: entries the subject evaluates separately from the mandatory
    # part. They are reported on their own line and can only add to a complete
    # mandatory score - a missing or broken bonus
    # must not reduce a complete mandatory submission, and because mapping
    # keys are scored in sorted order, an interleaved bonus failure would
    # otherwise break the streak partway through the mandatory functions.
    # Empty for every Piscine module, which keeps their output byte-identical.
    bonus_names = bonus_names or set()
    bonus_results = [(n, s) for n, s in results if n in bonus_names]
    results = [(n, s) for n, s in results if n not in bonus_names]

    entries = []
    total_exercises = len(results)
    passed_for_score = 0
    counting_score = True

    # SKIPPED means every check that ran passed, but --skip-norm/--skip-fn
    # meant one didn't run. That's not a failure, so it must not break the
    # score streak the way KO does - the functional result is still real and
    # worth showing. What it does poison is the verdict: we genuinely cannot
    # say whether the moulinette would pass this, so the status becomes
    # UNKNOWN rather than a PASSED we can't stand behind or a FAILED that
    # would wrongly imply the code is broken.
    any_skipped = False
    any_unknown = any(status == 'UNKNOWN' for _, status in results)

    for name, status in results:
        color = _status_color(status)
        plain = f"{name}: {status}"
        entries.append((plain, f"[{color}]{escape(name)}: {status}[/{color}]"))

        if status == "SKIPPED":
            any_skipped = True

        if status in ("OK", "SKIPPED"):
            if counting_score:
                passed_for_score += 1
        else:
            counting_score = False

    print()
    if entries:
        for line in _wrap_styled_entries("Result:      ", entries, BANNER_WIDTH):
            console.print(line)

    if bonus_results:
        bonus_entries = []
        for name, status in bonus_results:
            color = _status_color(status)
            plain = f"{name}: {status}"
            bonus_entries.append((plain, f"[{color}]{escape(name)}: {status}[/{color}]"))
            if status == "SKIPPED":
                any_skipped = True
        for line in _wrap_styled_entries("Bonus:       ", bonus_entries, BANNER_WIDTH):
            console.print(line)

    score = (
        int((passed_for_score / total_exercises) * 100) if total_exercises > 0 else 0
    )
    # 42 awards up to 25 extra points, only on top of a complete mandatory part.
    bonus_ok = sum(1 for _, s in bonus_results if s in ("OK", "SKIPPED"))
    bonus_total = len(bonus_results)
    bonus_points = 0
    if bonus_total and results and score == 100 and not any_skipped and not any_unknown:
        bonus_points = 25 * bonus_ok // bonus_total
    final_score = score + bonus_points

    # A filter naming only bonus keys grades none
    # of the mandatory part: there is no score to give, and "0/100 FAILED"
    # would read as a verdict on work that was never run.
    if not results:
        status_str = "UNKNOWN"
        console.print("Status:      [yellow]UNKNOWN (mandatory part not graded)[/yellow]")
    elif any_unknown:
        status_str = "UNKNOWN"
        console.print("Status:      [yellow]UNKNOWN (required tests unavailable)[/yellow]")
    elif any_skipped:
        status_str = "UNKNOWN"
        console.print(f"Final score: [yellow]{score}/100[/yellow]", highlight=False)
        console.print("Status:      [yellow]UNKNOWN (checks skipped)[/yellow]")
    else:
        color = "sea_green2" if score >= 50 else "deep_pink2"
        console.print(f"Final score: [{color}]{final_score}/100[/{color}]", highlight=False)
        status_str = "PASSED" if score >= 50 else "FAILED"
        console.print(f"Status:      [{color}]{status_str}[/{color}]")

    if bonus_results:
        # 42 only awards the bonus when the mandatory part is complete, so the
        # verdict is reported against that rule rather than on its own. It is
        # printed whatever the status above - skipped checks used to return
        # before reaching it, so --skip-norm on libft showed no tally at all.
        if bonus_points:
            bonus_color = "sea_green2" if bonus_ok == bonus_total else "yellow"
            note = f" (awarded: +{bonus_points})"
        elif bonus_ok < bonus_total:
            bonus_color, note = "deep_pink2", ""
        elif not results:
            bonus_color, note = "yellow", " (the mandatory part was not graded)"
        elif score < 100:
            bonus_color, note = "yellow", " (not awarded: mandatory part incomplete)"
        elif any_skipped:
            bonus_color, note = "yellow", " (awarded only if the skipped checks pass)"
        else:
            bonus_color, note = "deep_pink2", " (not awarded)"
        console.print(
            f"Bonus score: [{bonus_color}]{bonus_ok}/{bonus_total}{note}[/{bonus_color}]",
            highlight=False,
        )

    return status_str
