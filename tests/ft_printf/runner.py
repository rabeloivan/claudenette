"""Exercise the student's archive against the native Linux/glibc target profile."""
from pathlib import Path
from dataclasses import replace
from functools import partial
import struct
import subprocess
import sys
import tempfile

from tests.libft.build_utils import archive_is_ar, run_make
from utils.compiler import compile_source
from utils.reporting import function_report
from utils.runner import TestUnavailable, run_test_case
from utils.ui import (CasePresentation, display_str, print_command_execution, print_exercise_result,
                      print_test_fail, print_test_pass, print_test_section, print_test_stage)
from .build import NAME, check_archive_symbols, check_makefile, copy_project, find_header, source_files_ok
from .cases import c_string, describe, mandatory_cases, oracle_call, sign_cases, width_cases
from .presentation import case_title, result_presentation

HERE = Path(__file__).resolve().parent


def profile_unavailable_reason():
    if sys.platform not in ('darwin', 'linux') or struct.calcsize('i') != 4 or any(
            struct.calcsize(kind) != 8 for kind in ('l', 'P')):
        return 'ft_printf Linux/glibc target requires a Linux/macOS LP64 host; verify on campus Linux'
    return ''


def run_mandatory(path, check_symbols=True, norm_check=None):
    return run_project(path, 'mandatory', check_symbols, norm_check)


def run_width_bonus(path, check_symbols=True, norm_check=None):
    return run_project(path, 'width', check_symbols, norm_check)


def run_sign_bonus(path, check_symbols=True, norm_check=None):
    return run_project(path, 'signs', check_symbols, norm_check)


def run_project(path, part, check_symbols=True, norm_check=None):
    unavailable = profile_unavailable_reason()
    if unavailable:
        raise TestUnavailable(unavailable)
    root = Path(path).resolve()
    if root.is_file():
        root = root.parent
    name = 'ft_printf' if part == 'mandatory' else f'ft_printf_bonus_{part}'
    command = 'make' if part == 'mandatory' else 'make bonus'
    if part == 'mandatory':
        print_test_stage()
    print_command_execution(command + ' (in a scratch copy of the sources)')
    with function_report(name, concise=True) as group:
        success = _run(root, part, check_symbols, name, norm_check)
        if group is not None:
            group.success = success
        return success


def _run(root, part, check_symbols, name, norm_check=None):
    total = passed = 0

    def check(success, description, actual='', presentation=None):
        nonlocal total, passed
        total += 1
        if success:
            passed += 1
            print_test_pass(total, description, presentation=presentation)
        else:
            if presentation is not None:
                presentation = replace(presentation,
                    expected=presentation.expected or description,
                    actual=presentation.actual or actual or 'check failed')
            print_test_fail(total, description, actual=actual or 'check failed',
                            presentation=presentation)
        return success

    with tempfile.TemporaryDirectory(prefix='claudenette-printf-') as directory:
        temp = Path(directory)
        project = copy_project(root, temp / 'project')
        if part == 'mandatory':
            source_files_ok(root, partial(check, presentation=CasePresentation(
                'Submission files', 'match permitted file types')))
            archive = check_makefile(project, check)
        else:
            output, code = run_make(str(project), ['bonus'])
            archive = project / NAME
            check(code == 0 and archive_is_ar(str(archive)),
                  'make bonus builds libftprintf.a', output[-1200:])
        print_test_stage(blank_before=True)
        if norm_check is not None:
            norm_check(str(find_header(root)))
        print_command_execution('checking ft_printf.h')
        probe = temp / 'header.c'
        header_path = find_header(project)
        probe.write_text('#include "ft_printf.h"\n'
                         'int (*prototype)(const char *, ...) = ft_printf;\n')
        include_dirs = sorted({path.parent for path in project.rglob('*.h')})
        includes = [flag for path in include_dirs for flag in ('-I', str(path))]
        header = subprocess.run(['cc', '-Wall', '-Wextra', '-Werror', '-I', str(header_path.parent),
                                 '-I', str(project), *includes,
                                 '-c', str(probe), '-o', str(temp / 'header.o')],
                                capture_output=True, text=True, timeout=30)
        print_test_section('Header validation')
        check(header.returncode == 0,
              'ft_printf.h compiles independently and declares int ft_printf(const char *, ...)',
              header.stderr, presentation=CasePresentation(
                  'Standalone compilation and ft_printf prototype',
                  expected='int ft_printf(const char *, ...)', actual=header.stderr or None))
        if norm_check is not None:
            print_test_stage(blank_before=True)
            main_header = find_header(root)
            for source in sorted(root.rglob('*')):
                if (source.suffix in ('.c', '.h') and '.git' not in source.parts
                        and source != main_header):
                    norm_check(str(source))
        if check_symbols and archive.is_file():
            print_test_stage(blank_before=True)
            print_command_execution(
                'nm -g libftprintf.a (checking allowed functions: malloc, free, write, '
                'va_start, va_arg, va_copy, va_end)')
            symbols_ok, diagnostic = check_archive_symbols(archive)
            check(symbols_ok, 'archive external calls use the allowed functions or supplied Libft', diagnostic,
                  presentation=CasePresentation('External calls', 'use permitted functions',
                                                expected='permitted external functions', actual=diagnostic))
        cases = {'mandatory': mandatory_cases, 'width': width_cases, 'signs': sign_cases}[part]()
        lines = ['static void prepare_case(int index)', '{', '    switch (index)', '    {']
        for index, case in enumerate(cases):
            if case.string_size is not None:
                lines.append(f'    case {index}: protect_string({case.string_size}, {int(case.terminated)}); break;')
        lines += ['    default: break;', '    }', '}',
                  'static int invoke_case(int index)', '{', '    switch (index)', '    {']
        for index, case in enumerate(cases):
            arguments = ', '.join((c_string(case.format), *case.arguments))
            reference_format, reference_arguments = oracle_call(case)
            if (reference_format, reference_arguments) != (case.format, case.arguments):
                reference = ', '.join((c_string(reference_format), *reference_arguments))
                lines.append(f'    case {index}: if (h_call == reference_printf) return h_call({reference}); return h_call({arguments});')
                continue
            lines.append(f'    case {index}: return h_call({arguments});')
        lines += ['    default: exit(90);', '    }', '}']
        (temp / 'cases.h').write_text('\n'.join(lines) + '\n')
        sources = [str(HERE / 'harness.c'), str(archive)]
        flags = ['-Wall', '-Wextra', '-Werror', '-I', str(temp)]
        binary = temp / 'ft_printf_test'
        print_test_stage(blank_before=True)
        built = compile_source(sources, str(binary), flags, announce=False)
        if built:
            print_command_execution(name + '_test')
            output_lengths = {}

            def execute(case_id, binary=binary, mode='normal', failure=-1, repeats=1):
                actual_path = temp / 'actual'
                expected_path = temp / 'expected'
                actual_path.unlink(missing_ok=True)
                expected_path.unlink(missing_ok=True)
                output, error, code = run_test_case(str(binary), timeout=5,
                    args=[str(case_id), str(actual_path), str(expected_path), mode,
                          str(failure), str(repeats)])
                marker = 'CLAUDENETTE_TEST_UNAVAILABLE: '
                if code == 90 and error.startswith(marker):
                    raise TestUnavailable(error[len(marker):].strip())
                actual = actual_path.read_bytes() if actual_path.exists() else b''
                expected = expected_path.read_bytes() if expected_path.exists() else b''
                try:
                    expected_return, actual_return, attempts, live = map(int, output.split())
                    valid = code == 0 and not error
                except ValueError:
                    diagnostic = error or output or actual.decode('latin-1')[-500:] or f'exit status {code}'
                    return False, 0, diagnostic, CasePresentation(
                        case_title(cases[case_id]), call=describe(cases[case_id]), actual=diagnostic)
                if mode == 'normal' and failure < 0 and valid:
                    output_lengths[case_id] = expected_return
                if mode == 'late_write_error':
                    valid = (valid and expected_return > 1 and actual_return < 0
                             and actual == expected[:1] and live == 0)
                elif mode == 'write_error':
                    valid = valid and actual_return < 0 and live == 0
                elif failure >= 0:
                    recovered = actual_return == expected_return and actual == expected
                    valid = valid and attempts > failure and live == 0 and (actual_return < 0 or recovered)
                else:
                    valid = valid and actual == expected and actual_return == expected_return and live == 0
                diagnostic = (f'expected output {display_str(expected.decode("latin-1"), 100)} '
                              f'(return {expected_return}), got {display_str(actual.decode("latin-1"), 100)} '
                              f'(return {actual_return}, live allocations {live})')
                problems = []
                if mode in ('write_error', 'late_write_error'):
                    partial = mode == 'late_write_error'
                    failure_output = expected[:1] if partial else b''
                    context = 'after partial output' if partial else 'stdout is closed'
                    if actual_return >= 0:
                        problems.append('return error: write failure was not reported with a negative value')
                    if partial and actual != failure_output:
                        problems.append('output error: incorrect bytes before the write failure')
                    diagnostic = (
                        f'expected return < 0 ({context}); expected output during failure '
                        f'{display_str(failure_output.decode("latin-1"), 100)}; '
                        f'got output {display_str(actual.decode("latin-1"), 100)} '
                        f'(return {actual_return}, live allocations {live}); '
                        f'normal output {display_str(expected.decode("latin-1"), 100)} '
                        f'(normal return {expected_return})'
                    )
                elif failure >= 0:
                    if not (actual_return < 0 or recovered):
                        problems.append('return/output error: allocation failure was neither reported nor recovered')
                    if attempts <= failure:
                        problems.append('allocation error: the requested failure position was not reached')
                    diagnostic = (
                        f'expected a negative return (partial output permitted) or complete recovery; '
                        f'normal output {display_str(expected.decode("latin-1"), 100)} '
                        f'(normal return {expected_return}); '
                        f'got output {display_str(actual.decode("latin-1"), 100)} '
                        f'(return {actual_return}, live allocations {live})'
                    )
                else:
                    if actual != expected:
                        problems.append('output error: bytes differ from the normal output')
                    if actual_return != expected_return:
                        problems.append('return count error: count differs from the normal return')
                if live > 0:
                    problems.append(f'memory leak: live allocations {live} (expected 0)')
                if problems:
                    diagnostic = '; '.join(problems) + '; ' + diagnostic
                if valid and mode == 'normal' and failure < 0:
                    diagnostic = f'output {display_str(actual.decode("latin-1"), 60)} (return {actual_return})'
                presentation = result_presentation(
                    cases[case_id], actual, expected, actual_return, expected_return,
                    live, mode, failure, attempts, problems,
                    tracked=binary.name == 'ft_printf_memory',
                )
                if error:
                    presentation = replace(presentation,
                                           details=presentation.details + (('Runtime', error),))
                return valid, attempts, error or diagnostic, presentation

            print_test_section('Output and return values')
            for index, case in enumerate(cases):
                valid, _, diagnostic, presentation = execute(index)
                description = describe(case) + (' ' + diagnostic if valid else ' emits the expected bytes and return count')
                check(valid, description, diagnostic, presentation)
            # Repeated calls catch retained parser/count state and va_list misuse.
            selected = list(dict.fromkeys([0, len(cases) // 2, len(cases) - 1]))
            print_test_section('Repeated calls')
            for index in selected:
                valid, _, diagnostic, presentation = execute(index, repeats=3)
                check(valid, describe(cases[index]) + ' works on three consecutive calls', diagnostic,
                      replace(presentation, title=presentation.title + ' — three consecutive calls', result=''))
            print_test_section('Write errors')
            for index in selected:
                if not cases[index].format:
                    continue
                valid, _, diagnostic, presentation = execute(index, mode='write_error')
                check(valid, describe(cases[index]) + ' returns a negative value when stdout is closed', diagnostic,
                      presentation)
            late_cases = [index for index in range(len(cases)) if output_lengths.get(index, 0) > 1]
            late_cases = late_cases[::max(1, len(late_cases) // 3)][:3]
            for index in late_cases:
                valid, _, diagnostic, presentation = execute(index, mode='late_write_error')
                check(valid, describe(cases[index]) + ' reports a write error after partial output', diagnostic,
                      presentation)
            memory_binary = temp / 'ft_printf_memory'
            memory_built = compile_source([str(HERE / 'harness.c'),
                str(HERE.parent / 'free_tracker.c'), str(archive)], str(memory_binary),
                flags + ['-DPF_TRACK_MEMORY'], announce=False)
            built = built and memory_built
            if memory_built:
                print_test_section('Allocation tracking')
                # Small representative formats leave the finite tracker arena ample room.
                memory_cases = [i for i, case in enumerate(cases)
                                if len(case.format) <= 100 and (case.string_size or 0) <= 100
                                and all(len(arg) <= 100 for arg in case.arguments)]
                stride = max(1, len(memory_cases) // 12)
                memory_cases = list(dict.fromkeys(memory_cases[::stride] + selected))
                for index in memory_cases:
                    if len(cases[index].format) > 100 or (cases[index].string_size or 0) > 100:
                        continue
                    valid, attempts, diagnostic, presentation = execute(index, binary=memory_binary)
                    check(valid, describe(cases[index]) + ' checks output, return count and temporary memory', diagnostic,
                          presentation)
                    if cases[index].format:
                        error_ok, _, error_detail, presentation = execute(index, binary=memory_binary, mode='write_error')
                        check(error_ok, describe(cases[index]) + ' reports a write error when stdout is closed (allocation tracking enabled)', error_detail,
                              presentation)
                    if output_lengths.get(index, 0) > 1:
                        error_ok, _, error_detail, presentation = execute(index, binary=memory_binary, mode='late_write_error')
                        check(error_ok, describe(cases[index]) + ' reports a write error after partial output (allocation tracking enabled)', error_detail,
                              presentation)
                    if valid:
                        for failure in range(attempts):
                            valid, _, diagnostic, presentation = execute(index, binary=memory_binary, failure=failure)
                            check(valid, describe(cases[index]) +
                                  f' handles allocation failure {failure + 1} and frees temporary memory', diagnostic,
                                  presentation)
        print_exercise_result(name, passed, total, failed=not built)
        return built and passed == total and total > 0
