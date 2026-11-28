"""Build the student's sources directly, without reference implementations."""
import subprocess
import tempfile
from pathlib import Path

from utils.compiler import _harness_flags, compile_source
from utils.reporting import (concise_cases, current_group, function_report, grouped_norm_report,
                             grouped_symbols_report)
from utils.runner import run_test_case
from utils.ui import (CasePresentation, print_command_execution, print_exercise_result,
                      print_test_fail, print_test_pass, print_test_section, print_test_stage)
from .cases import file_cases
from .declarations import variable_counts

HERE = Path(__file__).resolve().parent
BUFFER_SIZES = (None, 1, 10, 42, 9999, 10000000)
# Allocation campaigns. The tracker's default 1 MiB arena cannot hold a 10 MB
# read buffer, so that build gets an arena sized for a buffer on every call of
# the short campaign input; its slot table keeps the default size.
MEMORY_BUFFER_SIZES = (1, 42, 9999, 10000000)
LARGE_ARENA = ['-DH_ARENA_SIZE=134217728', '-DH_BLOCK_MAX=65536']
INT_MAX_BUFFER = 2147483647
NONPOSITIVE_BUFFER_SIZES = (0, -1)


def run_mandatory(student_file, norm_check=None, function_check=None):
    return run_project(student_file, bonus=False, norm_check=norm_check,
                       function_check=function_check)


def run_bonus(student_file, norm_check=None, function_check=None):
    return run_project(student_file, bonus=True, norm_check=norm_check,
                       function_check=function_check)


def run_project(student_file, bonus=False, norm_check=None, function_check=None):
    name = 'get_next_line_bonus' if bonus else 'get_next_line'
    with function_report(name) as group:
        success = _run(Path(student_file).resolve().parent, bonus, name,
                       norm_check, function_check)
        if group is not None:
            group.success = success
        return success


def _announce_block(command):
    """Each BUFFER_SIZE block names its own run; the group would show only the first."""
    group = current_group()
    if group is not None:
        group.announced = False
    print_test_stage(blank_before=True, reset_index=False)
    print_command_execution(command)


def _build(sources, binary, flags):
    """A build whose failure is itself a graded case, reported by the caller."""
    command = ['cc', *flags, *_harness_flags(), *sources, '-o', str(binary)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    error = result.stderr
    for source in sources:  # name the student's files as they appear in the submission
        error = error.replace(str(Path(source).parent) + '/', '')
    return result.returncode == 0, error.strip()


def _run_limits(temp, root, name, sources, execute, report):
    """BUFFER_SIZE values at the edges: INT_MAX, then zero and negative."""
    harness = [*sources, str(HERE / 'harness.c'), str(HERE.parent / 'free_tracker.c')]
    tracked = ['-I', str(root), '-Dread=gnl_read', '-DGNL_TRACK_MEMORY']
    binary = temp / 'get_next_line_limits'
    label = f'BUFFER_SIZE={INT_MAX_BUFFER}'
    # The subject's flags: an int expression such as BUFFER_SIZE + 1 overflows here.
    built, error = _build(harness, binary, ['-Wall', '-Wextra', '-Werror', *tracked,
                                            f'-D BUFFER_SIZE={INT_MAX_BUFFER}'])
    _announce_block(f'{name}_limits')
    print_test_section('Largest buffer — ' + label)
    report(f'{label} compiles with -Wall -Wextra -Werror', built, error,
           CasePresentation('Compiles with -Wall -Wextra -Werror', 'no warnings',
                            call=f'cc -Wall -Wextra -Werror -D {label}',
                            expected='no warnings', actual=error, details=(('Buffer', label),)))
    if built:
        execute(binary, 'oversized', [b'alpha\n\nbeta\nlast'],
                f'{label}, an allocation the arena cannot hold returns NULL and releases memory',
                buffer_label=label)
    else:
        report(f'{label}, an allocation the arena cannot hold returns NULL and releases memory',
               False, 'not run: the build failed',
               CasePresentation('Buffer allocation refused', 'not run: the build failed',
                                call=f'{name}(fd)', expected='lines, or NULL with no retained memory',
                                actual='not run: the build failed', details=(('Buffer', label),)))
    print_test_section('Nonpositive BUFFER_SIZE')
    for buffer_size in NONPOSITIVE_BUFFER_SIZES:
        label = f'BUFFER_SIZE={buffer_size}'
        scenario = 'returns NULL on every call without reading or leaking'
        description = f'{label}, {scenario}'
        # Without -Werror: gcc rejects a guarded read(fd, buf, -1) as a constant
        # oversized access, while clang accepts it. Behaviour is what is graded.
        built, error = _build(harness, binary, ['-Wall', '-Wextra', *tracked,
                                                '-DGNL_NONPOSITIVE', f'-D BUFFER_SIZE={buffer_size}'])
        if built:
            execute(binary, 'nonpositive', [b'first\n\nlast line'], description,
                    buffer_label=label)
        else:
            report(description, False, error,
                   CasePresentation(label, 'NULL on every call, no read, no leak',
                                    call=f'cc -Wall -Wextra -D {label}',
                                    expected='builds with -Wall -Wextra', actual=error,
                                    details=(('Buffer', label),)))


def _run(root, bonus, name, norm_check=None, function_check=None):
    suffix = '_bonus' if bonus else ''
    sources = [str(root / f'get_next_line{suffix}.c'),
               str(root / f'get_next_line_utils{suffix}.c')]
    header = str(root / f'get_next_line{suffix}.h')
    passed = total = 0
    builds_ok = True
    prechecks_done = False

    def report(description, success, diagnostic='', presentation=None):
        nonlocal passed, total
        total += 1
        if success:
            passed += 1
            print_test_pass(total, description, presentation=presentation)
        else:
            print_test_fail(total, description, actual=diagnostic or 'check failed',
                            presentation=presentation)
        return success

    def execute(binary, mode, inputs, description, extra=(), buffer_label=None):
        buffer = buffer_label or label
        paths = []
        for index, data in enumerate(inputs):
            path = Path(binary).parent / f'input-{index}'
            path.write_bytes(data)
            paths.append(str(path))
        output, error, code = run_test_case(
            str(binary), args=[mode, *paths, *extra], timeout=5)
        diagnostic = error or output or f'exit status {code}'
        scenario = description.removeprefix(buffer + ', ')
        titles = {
            'stdin': 'Standard input', 'pipe': 'Ready pipe lines',
            'short': 'Short reads', 'negative': 'Negative descriptor',
            'huge_fd': 'Descriptor INT_MAX',
            'closed': 'Closed descriptor', 'write_only': 'Write-only descriptor',
            'directory': 'Directory read error', 'read_error': 'Read error after partial input',
            'pending_error': 'Read error with pending input',
            'next_call_error': 'Read error at the start of the next call',
            'multi': 'Interleaved descriptors', 'multi_error': 'Read error on one descriptor',
            'oversized': 'Buffer allocation refused', 'nonpositive': buffer,
        }
        results = {
            'file': 'lines and EOF match', 'stdin': 'ready lines returned before EOF',
            'pipe': 'ready lines returned before EOF', 'short': 'lines and EOF match',
            'negative': 'returns NULL', 'huge_fd': 'returns NULL', 'closed': 'returns NULL',
            'write_only': 'returns NULL', 'directory': 'returns NULL',
            'read_error': 'returns NULL and clears partial input',
            'pending_error': 'returns NULL and clears pending input',
            'next_call_error': 'returns NULL and clears pending input',
            'multi': 'independent lines and EOF',
            'multi_error': 'other descriptors remain readable',
            'allocation_failure': 'returns NULL and frees pending memory',
            'oversized': 'lines, or NULL with no retained memory',
            'nonpositive': 'NULL on every call, no read, no leak',
        }
        title = titles.get(mode, scenario[:1].upper() + scenario[1:])
        if mode == 'allocation_failure':
            title = f'Allocation failure {int(extra[0]) + 1}'
        report(description, code == 0 and not output and not error, diagnostic,
               CasePresentation(title, results[mode], call=f'{name}(fd)',
                                expected=results[mode], actual=diagnostic,
                                details=(('Buffer', buffer), ('Scenario', scenario))))
        return output, error, code

    with tempfile.TemporaryDirectory(prefix='claudenette-gnl-') as directory:
        temp = Path(directory)
        probe = temp / 'header.c'
        probe.write_text(f'#include "{Path(header).name}"\n'
                         'char *(*gnl_prototype)(int) = get_next_line;\n')
        for buffer_size in BUFFER_SIZES:
            label = 'default BUFFER_SIZE' if buffer_size is None else f'BUFFER_SIZE={buffer_size}'
            flags = ['-Wall', '-Wextra', '-Werror', '-I', str(root)]
            if buffer_size is not None:
                flags.append(f'-D BUFFER_SIZE={buffer_size}')
            binary = temp / 'get_next_line_test'
            if not compile_source(sources + [str(HERE / 'harness.c')], str(binary),
                                  flags + ['-Dread=gnl_read'], announce=not concise_cases()):
                builds_ok = False
                continue
            if not prechecks_done:
                # Same moment as before: the sources are checked once something compiles.
                if norm_check is not None:
                    if not bonus:  # the bonus unit opens right after the mandatory delimiter
                        print_test_stage(reset_index=False)
                    with grouped_norm_report(root):
                        for source in [header, *sources]:
                            norm_check(source)
                if function_check is not None:
                    print_test_stage(blank_before=True, reset_index=False)
                    with grouped_symbols_report(name):
                        function_check()
                prechecks_done = True
            _announce_block(f'{name}_test ({label})')
            print_test_section('Header validation — ' + label)
            header_result = subprocess.run(
                ['cc', *flags, '-c', str(probe), '-o', str(temp / 'header.o')],
                capture_output=True, text=True, timeout=30)
            report(f'{label}, header compiles independently and declares char *get_next_line(int)',
                   header_result.returncode == 0, header_result.stderr,
                   CasePresentation('Standalone compilation and prototype',
                                    'char *get_next_line(int)',
                                    expected='char *get_next_line(int)',
                                    actual=header_result.stderr, details=(('Buffer', label),)))
            print_test_section('Source requirements — ' + label)
            try:
                globals_count, static_count = variable_counts(sources + [header], flags)
                report(f'{label} uses no global variables', globals_count == 0,
                       f'{globals_count} global variable declarations',
                       CasePresentation('File-scope variables', 'none', expected='no global variables',
                                        actual=f'{globals_count} declarations', details=(('Buffer', label),)))
                if bonus:
                    report(f'{label} uses at most one static variable', static_count <= 1,
                           f'{static_count} static variable declarations',
                           CasePresentation('Static variables', f'{static_count} declarations',
                                            expected='at most one static variable',
                                            actual=f'{static_count} declarations', details=(('Buffer', label),)))
            except Exception as error:
                report(f'{label} variable declarations can be checked', False,
                       f'{type(error).__name__}: {error}')
            print_test_section('Input and returned lines — ' + label)
            for description, data in file_cases(buffer_size):
                execute(binary, 'file', [data], f'{label}, {description}')
            small = b'first\n\nlast line'
            print_test_section('Streams and read errors — ' + label)
            for mode, description in [
                ('stdin', 'returns each ready stdin line before EOF'),
                ('pipe', 'returns consecutive ready lines while the pipe writer stays open'),
                ('short', 'handles reads that return fewer bytes than requested'),
                ('negative', 'negative descriptor returns NULL'),
                ('huge_fd', 'descriptor INT_MAX returns NULL'),
                ('closed', 'closed descriptor returns NULL'),
                ('write_only', 'write-only descriptor returns NULL'),
                ('directory', 'directory read error returns NULL'),
                ('read_error', 'read error after partial input returns NULL'),
                ('pending_error', 'read error after a returned line clears pending input'),
                ('next_call_error', 'read error at the start of the next call clears pending input'),
            ]:
                data = small
                if mode == 'read_error':
                    data = b'abcdefghijklmnop\nlast\n'
                elif mode in ('pending_error', 'next_call_error'):
                    data = b'a\nbcdefghijklmnop\nlast\n'
                execute(binary, mode, [data], f'{label}, {description}')
            if bonus:
                print_test_section('Multiple descriptors — ' + label)
                execute(binary, 'multi', [b'a\n\nlast-A', b'B' * 85 + b'\nlast-B\n', b'\nC\n'],
                        f'{label}, three interleaved descriptors retain independent lines')
                execute(binary, 'multi_error', [b'abcdefghijklmnop\n', b'b\nbbb\nlast-B', b'c\ncccc\nlast-C'],
                        f'{label}, a read error leaves other descriptors readable')
        # The tracker has a finite arena. Short inputs keep injection within its
        # capacity; the 10 MB build gets a larger one (MEMORY_BUFFER_SIZES).
        for buffer_size in MEMORY_BUFFER_SIZES:
            label = f'BUFFER_SIZE={buffer_size}'
            flags = ['-Wall', '-Wextra', '-Werror', '-I', str(root),
                     '-Dread=gnl_read', '-DGNL_TRACK_MEMORY', f'-D BUFFER_SIZE={buffer_size}']
            if buffer_size > 1024 * 1024:
                flags += LARGE_ARENA
            binary = temp / 'get_next_line_memory'
            if not compile_source(sources + [str(HERE / 'harness.c'),
                                             str(HERE.parent / 'free_tracker.c')], str(binary), flags,
                                  announce=not concise_cases()):
                builds_ok = False
                continue
            data = b'alpha\n\nbeta\nlast'
            path = temp / 'memory-input'
            path.write_bytes(data)
            output, error, code = run_test_case(str(binary), args=['measure', str(path)], timeout=5)
            measured = code == 0 and not error and output.strip().isdigit()
            _announce_block(f'{name}_memory ({label})')
            print_test_section('Allocation tracking — ' + label)
            report(f'BUFFER_SIZE={buffer_size}, lines are freeable and EOF releases retained memory',
                   measured, error or output,
                   CasePresentation('Returned-line ownership and EOF cleanup',
                                    'freeable results and no retained memory',
                                    expected='freeable results and no retained memory',
                                    actual=error or output, details=(('Buffer', label),)))
            if measured:
                attempts = int(output.strip())
                if attempts:
                    print_test_section('Allocation failures — ' + label)
                # A new process per position also resets the student's static state.
                for failure in range(attempts):
                    execute(binary, 'allocation_failure', [data],
                            f'BUFFER_SIZE={buffer_size}, allocation failure {failure + 1} returns NULL and frees pending memory',
                            [str(failure)])
            print_test_section('Memory boundaries and cleanup — ' + label)
            execute(binary, 'file', [b'x' * 257 + b'\n\nlast'],
                    f'BUFFER_SIZE={buffer_size}, a longer line preserves heap boundaries and releases memory at EOF')
            execute(binary, 'read_error', [b'abcdefghijklmnop\n'],
                    f'BUFFER_SIZE={buffer_size}, read error frees partially built input')
            execute(binary, 'pending_error', [b'a\nbcdefghijklmnop\n'],
                    f'BUFFER_SIZE={buffer_size}, read error frees pending state after a returned line')
            execute(binary, 'next_call_error', [b'a\nbcdefghijklmnop\n'],
                    f'BUFFER_SIZE={buffer_size}, read error at the start of the next call frees pending state')
            if bonus:
                execute(binary, 'multi', [b'a\nlast-A', b'B\n\nlast-B', b'\nC\n'],
                        f'BUFFER_SIZE={buffer_size}, interleaved descriptors release all memory at EOF')
                execute(binary, 'multi_error', [b'abcdefghijklmnop\n', b'b\nbbb\nlast-B', b'c\ncccc\nlast-C'],
                        f'BUFFER_SIZE={buffer_size}, descriptor error frees only its own pending memory')
        if prechecks_done:
            _run_limits(temp, root, name, sources, execute, report)
    if not prechecks_done and norm_check is not None:
        # Nothing compiled: the header was still checked first before this layout.
        norm_check(header)
    print_exercise_result(name, passed, total, failed=not builds_ok)
    return passed == total and total > 0 and builds_ok
