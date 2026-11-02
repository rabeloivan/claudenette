"""Collect real case results once, for detailed groups and compact columns."""
import contextlib
import io
import re
from contextvars import ContextVar
from dataclasses import dataclass, field

from rich.console import Console
from rich.table import Table
from rich.text import Text
from utils.runner import RUNTIME_ISSUES

console = Console()
EXPLANATIONS = {
    'ABSENT': 'required file missing', 'TODO': 'test not implemented',
    'NORM ERR': 'coding-style errors', 'FORBIDDEN FN': 'forbidden function calls',
    'EXTRA FILES': 'unexpected files', 'CRASH': 'tester error',
    'SKIPPED': 'some checks were skipped; verdict incomplete',
    'KO': 'test or compilation failed', 'OK': 'all checks passed',
}


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


@dataclass
class Group:
    compilations: int = 0
    commands: set = field(default_factory=set)
    announced: bool = False
    index: int = 0
    passed: int = 0
    total: int = 0
    success: bool = True


_REPORT = ContextVar('exercise_report', default=None)
_GROUP = ContextVar('function_report', default=None)
_name_width = 18
_header_shown = False
_statuses = set()
_rush_footer = None


def current_group():
    return _GROUP.get()


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
def function_report(name, enabled=True):
    """Merge behavior, boundary, NULL and allocation stages of one function."""
    if not enabled or current_group() is not None:
        yield None
        return
    group = Group()
    token = _GROUP.set(group)
    try:
        yield group
    except BaseException:
        group.success = False
        raise
    finally:
        _GROUP.reset(token)
        from utils.ui import print_exercise_result
        # A failed extra build is a real failure, but not an invented test case.
        print_exercise_result(name, group.passed, group.total, failed=not group.success)


def start_compact_report(names):
    global _name_width, _header_shown, _rush_footer
    _name_width = min(30, max(12, *(len(name) for name in names)))
    _header_shown = False
    _statuses.clear()
    _rush_footer = None


def compact_report(name, status, report=None, cases=None):
    global _header_shown
    report = report or Report()
    cases = report.cases if cases is None else cases
    _statuses.add(status)
    passed = sum(case.passed for case in cases)
    failed = len(cases) - passed
    tests = Text()
    compilation_failed = any(kind == 'compile' for kind, _ in report.problems)
    missing_implementation = any(kind == 'implementation' for kind, _ in report.problems)
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
    else:
        tests.append('not implemented' if missing_implementation else
                     'compilation failed' if compilation_failed else '—')
    color = 'sea_green2' if status == 'OK' else 'yellow' if status == 'SKIPPED' else 'deep_pink2'
    table = Table(box=None, padding=(0, 1), pad_edge=False, show_header=not _header_shown,
                  width=min(92, console.width))
    table.add_column('FUNCTION', width=_name_width, no_wrap=False)
    table.add_column('TESTS', ratio=1)
    table.add_column('RESULT', width=12, no_wrap=True)
    table.add_row(Text(name), tests, Text(status, style=color))
    console.print(table)
    _header_shown = True


def finish_compact_report():
    console.print()
    console.print(Text('Tests: ✓ passed  ✖ failed  ×N count of tests', style='bright_black'))
    for status in EXPLANATIONS:
        if status in _statuses:
            console.print(Text(f'{status}: {EXPLANATIONS[status]}', style='bright_black'))
    if _rush_footer:
        console.print()
        console.print(Text(_rush_footer))


@contextlib.contextmanager
def exercise_report(result, compact=False):
    global _rush_footer
    RUNTIME_ISSUES.clear()
    report = Report()
    token = _REPORT.set(report)
    capture = io.StringIO()
    try:
        if compact:
            with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture):
                yield
        else:
            yield
    finally:
        _REPORT.reset(token)
    if not compact:
        return
    output = capture.getvalue()
    match = re.search(r'^Result:(.*?)^Status:\s*(\S+)', output, re.M | re.S)
    if match and re.search(r'^Final score:.*%', match.group(0), re.M):
        statuses = dict(re.findall(r'(rush0\d):\s*(OK|KO)', match.group(1)))
        for name, cases, problems in report.sections:
            status = statuses.get(name, 'OK' if all(c.passed for c in cases) and not problems else 'KO')
            compact_report(name, status, Report(cases=cases, problems=problems))
        score = re.search(r'^Final score:.*$', output, re.M)
        _rush_footer = score.group(0) + '\nStatus:      ' + match.group(2)
    else:
        compact_report(*result(), report=report)
