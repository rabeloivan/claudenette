"""Collect real case results once, for detailed groups and compact columns."""
import contextlib
import io
import re
from contextvars import ContextVar
from dataclasses import dataclass, field

from rich.console import Console
from rich.table import Table
from rich.text import Text
from utils.runner import RUNTIME_ISSUES, TestUnavailable

console = Console()


@dataclass
class Case:
    index: int
    passed: bool
    description: str
    expected: object = None
    actual: object = None


@dataclass
class Report:
    cases: list = field(default_factory=list)
    problems: list = field(default_factory=list)
    sections: list = field(default_factory=list)
    concise: bool = False
    presenter: object = None
    # 'delimited': ft_printf layout, a delimiter between stages of one project.
    # 'blocks': Libft layout, one delimited block per function, stages split by a blank line.
    stages: str | None = None
    stage: str | None = None
    stage_fresh: bool = False
    case_open: bool = False
    blank_pending: bool = False


@dataclass
class Group:
    compilations: int = 0
    commands: set = field(default_factory=set)
    announced: bool = False
    index: int = 0
    passed: int = 0
    total: int = 0
    success: bool = True
    unavailable: bool = False
    concise: bool = False
    norm_root: str | None = None
    symbols_name: str | None = None
    norm_announced: bool = False


_REPORT = ContextVar('exercise_report', default=None)
_GROUP = ContextVar('function_report', default=None)
_name_width = 18
_header_shown = False
_rush_footer = None


def current_group():
    return _GROUP.get()


def current_presenter():
    report = _REPORT.get()
    return report.presenter if report is not None else None


def staged_report():
    """The running report when its unit uses the ft_printf stage layout."""
    report = _REPORT.get()
    return report if report is not None and report.stages else None


def defer_stage_blank():
    """Keep consecutive file results together; the stage's end adds one gap."""
    report = staged_report()
    if report is None:
        return False
    report.blank_pending = True
    return True


@contextlib.contextmanager
def grouped_norm_report(root):
    """Group announcements while retaining each original per-file Norm check."""
    group = current_group()
    if group is None:
        yield
        return
    previous = group.norm_root, group.norm_announced
    group.norm_root, group.norm_announced = str(root), False
    try:
        yield
    finally:
        group.norm_root, group.norm_announced = previous


@contextlib.contextmanager
def grouped_symbols_report(name):
    """Show one allowed-function announcement for a project's per-file checks."""
    group = current_group()
    if group is None:
        yield
        return
    previous, group.symbols_name = group.symbols_name, name
    try:
        yield
    finally:
        group.symbols_name = previous


def concise_cases():
    report, group = _REPORT.get(), _GROUP.get()
    return bool((report and report.concise) or (group and group.concise))


def present_case(description, passed, expected=None, actual=None):
    report = _REPORT.get()
    if report is not None and report.presenter is not None:
        return report.presenter(description, passed, expected, actual)
    return None


def record_case(index, passed, description, expected=None, actual=None):
    group = current_group()
    if group is not None:
        group.index += 1
        index = group.index
    report = _REPORT.get()
    if report is not None:
        report.cases.append(Case(index, passed, description, expected, actual))
    return index


def record_problem(kind, message):
    report = _REPORT.get()
    if report is not None:
        report.problems.append((kind, message))


def record_summary(name, passed, total):
    group = current_group()
    if group is not None:
        group.passed += passed
        group.total += total
        return True
    return False


@contextlib.contextmanager
def case_section(name):
    """Keep rush00's separately scored variants and their diagnostics apart."""
    report = _REPORT.get()
    start = len(report.cases) if report else 0
    problems = len(report.problems) if report else 0
    try:
        yield
    finally:
        if report is not None:
            report.sections.append((name, report.cases[start:], report.problems[problems:]))


@contextlib.contextmanager
def function_report(name, enabled=True, concise=False):
    """Merge behavior, boundary, NULL and allocation stages of one function."""
    if not enabled or current_group() is not None:
        yield None
        return
    group = Group(concise=concise)
    token = _GROUP.set(group)
    try:
        yield group
    except TestUnavailable:
        group.unavailable = True
        raise
    except BaseException:
        group.success = False
        raise
    finally:
        _GROUP.reset(token)
        from utils.ui import print_exercise_result
        # A failed extra build is a real failure, but not an invented test case.
        if not group.unavailable:
            print_exercise_result(name, group.passed, group.total, failed=not group.success)


def start_compact_report(names):
    global _name_width, _header_shown, _rush_footer
    _name_width = min(30, max(12, *(len(name) for name in names)))
    _header_shown = False
    _rush_footer = None


def compact_report(name, status, report=None, cases=None):
    global _header_shown
    report = report or Report()
    if not _header_shown and (name.startswith('ft_printf') or report.stages):
        from utils.ui import print_test_stage
        print_test_stage(reset_index=False)
    cases = report.cases if cases is None else cases
    passed = sum(case.passed for case in cases)
    failed = len(cases) - passed
    tests = Text()
    compilation_failed = any(kind == 'compile' for kind, _ in report.problems)
    missing_implementation = any(kind == 'implementation' for kind, _ in report.problems)
    unavailable = any(kind == 'environment' for kind, _ in report.problems)
    if cases:
        if len(cases) <= 24:
            for case in cases:
                tests.append('✓' if case.passed else '✖', 'sea_green2' if case.passed else 'deep_pink2')
        else:
            tests.append(f'✓×{passed}', 'sea_green2')
            if failed:
                tests.append(f'  ✖×{failed}', 'deep_pink2')
        tests.append(f'  ({passed}/{len(cases)})')
        if compilation_failed:
            tests.append('  compilation failed', 'deep_pink2')
        if unavailable:
            tests.append('  test unavailable', 'yellow')
    else:
        tests.append('not implemented' if missing_implementation else
                     'test unavailable' if unavailable else
                     'compilation failed' if compilation_failed else '—')
    color = 'sea_green2' if status == 'OK' else 'yellow' if status in ('SKIPPED', 'UNKNOWN') else 'deep_pink2'
    table = Table(box=None, padding=(0, 1), pad_edge=False, show_header=not _header_shown,
                  width=min(92, console.width))
    table.add_column('FUNCTION', width=_name_width, no_wrap=False)
    table.add_column('TESTS', ratio=1, justify='center')
    table.add_column('RESULT', width=12, no_wrap=True, justify='right')
    table.add_row(Text(name), tests, Text(status, style=color))
    console.print(table)
    _header_shown = True


def finish_compact_report():
    console.print()
    console.print(Text('TESTS: ✓ passed  ✖ failed  ×N count of tests', style='bright_black'))
    if _rush_footer:
        from utils.ui import print_rush00_summary
        print_rush00_summary(*_rush_footer)


def _close_stage(report):
    if report.blank_pending:
        report.blank_pending = False
        print()


@contextlib.contextmanager
def exercise_report(result, compact=False, concise=False, presenter=None, stages=None):
    global _rush_footer
    RUNTIME_ISSUES.clear()
    report = Report(concise=concise, presenter=presenter, stages=stages)
    token = _REPORT.set(report)
    capture = io.StringIO()
    try:
        if compact:
            with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture):
                try:
                    yield
                finally:
                    if presenter is not None:
                        presenter.flush_prechecks()
                    _close_stage(report)
        else:
            try:
                yield
            finally:
                if presenter is not None:
                    presenter.flush_prechecks()
                _close_stage(report)
    finally:
        _REPORT.reset(token)
    if not compact:
        return
    output = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', capture.getvalue())
    match = re.search(r'^Result:(.*?)^Status:\s*(\S+)', output, re.M | re.S)
    if match and re.search(r'^Final score:.*%', match.group(0), re.M):
        statuses = dict(re.findall(r'(rush0\d):\s*(OK|KO)', match.group(1)))
        for name, cases, problems in report.sections:
            status = statuses.get(name, 'OK' if all(c.passed for c in cases) and not problems else 'KO')
            compact_report(name, status, Report(cases=cases, problems=problems, stages=report.stages))
        score = re.search(r'^Final score:\s*(\d+)%', output, re.M)
        variants = [(int(name[-1]), status == 'OK') for name, status in statuses.items()]
        _rush_footer = variants, int(score[1])
    else:
        name, status = result()
        compact_report(presenter.name if presenter is not None else name, status, report=report)
