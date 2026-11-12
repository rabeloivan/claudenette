# Claudenette

A local tester for 42 projects, covering subject requirements, defined function
behavior and documented robustness checks. Point it at your submission directory
to check norm, forbidden functions, deliverables and the behavior of your code.

Covers the Piscine — **C00–C13**, **rush00 / rush01 / rush02**, **bsq**, **shell00 /
shell01** — and the common-core projects **libft** and **ft_printf**.

> Claudenette is an unofficial study aid. It is not affiliated with 42, and passing
> here does not guarantee passing the real moulinette. Always test your own work.

## Evaluation policy

Claudenette keeps one score and one verdict. A relevant subject, function-contract
or documented robustness failure can produce KO, even if a submission passed an
official evaluation. The score describes Claudenette's checks; it is not an
official Moulinette grade or a measured probability of passing it.

The reference environment is the campus Linux target documented below. Running
on a Mac must not silently impose macOS-specific behavior on a Linux submission.
The ft_printf tester implements the Linux/glibc 64-bit profile described in its
section; other modules retain their documented contracts. This is native testing,
not a complete Linux emulator. A required test that cannot be evaluated reliably
is UNKNOWN, with no final score, rather than a student failure or a pass.

Tests stay within each subject's domain and the defined behavior of functions it
requires reproducing. Additional policies, such as custom-function NULL safety,
are identified explicitly. Valid algorithms and allocation strategies are accepted;
exact allocation counts, undefined inputs and arbitrary performance requirements
are not added as grading obligations.

Run against the intended submission tree. Keep redirected logs and other local
reports outside that tree: files present there are still checked as deliverables.
An extra-file finding identifies the files to review, not a defect in the C code.
Claudenette does not ignore a file merely because its name resembles a test log.

## Install

Target campus environment: **Ubuntu 22.04.5 LTS**, Python 3.10 or newer.
Install as your normal user:

```bash
git clone https://github.com/rabeloivan/claudenette.git ~/claudenette
python3 ~/claudenette/install.py
```

The installer downloads the pinned Python dependencies into `~/claudenette/.deps/`.
It bootstraps a temporary, pinned pip wheel and verifies its SHA-256 against PyPI
metadata, so the system needs neither pip nor `python3-venv`. It uses no sudo,
asks no installation questions, and changes neither system Python nor shell config.
Internet access and write access to the checkout are required during installation.
Grading itself does not download or install anything. Re-run the installer after
updating `requirements.txt`.

### Prerequisites

| Tool | Source |
| --- | --- |
| Python 3.10+ | campus environment |
| `rich`, `norminette` | `install.py`, locally in `.deps/` |
| `cc`, `make`, `ar`, `nm` | campus C toolchain |
| shell exercise utilities | campus environment; checked when needed |

If a required tool is missing, Claudenette names it and refuses that run. On a
managed campus machine, contact campus staff about missing system tools. There
is no automatic package-manager installation. A missing tool never becomes a pass.
For example, C10 ex03 needs `hexdump`, and C10 ex02 needs `tail`; filtering to
other exercises avoids requiring tools those exercises do not use.

## Usage

Run it **from inside your exercise directory** — the directory's *name* is what
selects the tests:

```bash
cd ~/piscine/C01
python3 ~/claudenette/main.py   # or just `claudenette`, see below
```

That directory must be named `C00`–`C13`, or `rush00` / `rush01` / `rush02` / `bsq` /
`shell00` / `shell01` / `libft` / `ft_printf`
(project names are case-insensitive). Anything else exits
with an error. **This is the most common first-run mistake** — running from the repo
itself, or from a parent folder, will not work. Claudenette is the grader, not the
submissions.

### Set up the `claudenette` alias

Typing the full path every time gets old. Add the alias to your shell config —
`~/.zshrc` on macOS (zsh is the default since Catalina), `~/.bashrc` on most Linux:

```bash
echo "alias claudenette='python3 ~/claudenette/main.py'" >> ~/.zshrc && source ~/.zshrc
```

The script loads its checkout-local dependencies automatically. No environment
activation is needed. Add the alias to `~/.bashrc` on Ubuntu instead of `~/.zshrc`.

Every example below assumes it.

### What you can pass it

Arguments are **substring filters** matched against exercise paths and displayed names, so anything
that identifies an exercise works — an `exNN` directory, a filename, or both mixed.
With no arguments you get the whole module.

| Command | Grades |
| --- | --- |
| `claudenette` | every exercise in the module |
| `claudenette ex00` | just `ex00` |
| `claudenette ex00 ex03` | `ex00` and `ex03` |
| `claudenette ft_print_program_name.c` | whichever exercise turns in that file |
| `claudenette ft_print_program_name.c ex02` | mixed — the file's exercise, plus `ex02` |
| `claudenette ex0` | `ex00`–`ex09` (it's a substring, not an exact match) |

Filters are matched, not validated, so a typo grades nothing rather than failing:

```
$ claudenette ex99
No exercises matched 'ex99'.
```

Two things worth knowing while iterating:

- Filtering changes the **score**, not just the output. `claudenette ex03` reports
  `100/100` for that one exercise alone. Only a full run tells you where you stand,
  because of the leading-run rule below.
- The exercise directory must exist. A filter naming an exercise you haven't started
  reports `ABSENT`, which counts as a failure.

### Options

| Flag | Effect |
| --- | --- |
| `--skip-norm` | Skip norminette |
| `--skip-fn` | Grade without the forbidden-function check |
| `--compact` | Show aligned FUNCTION / TESTS / RESULT columns without detailed errors |

The default output keeps the original colored CLAUDENETTE banner, all test cases,
expected/got diagnostics, score, elapsed time and final notice. Details require no
flag. `--compact` is optional; there is no `--verbose` option. Libft and ft_printf
use short scenario labels and aligned result values. Bold group titles identify
the existing campaigns. Failures show Call, Expected and Got fields, with context
for write errors, allocation tracking and the first differing output byte.
The other modules use one `as expected` or `not as expected` result phrase.

Function-level tests have one continuous numbered list and one final PASS/FAIL total.
Primary cases come before the additional campaigns in those function runners; successful
internal compilations and runs are not announced again. Compilation errors are
always shown in normal mode. For example, `Empty string` is followed by `output 0`
in the aligned value column of the Libft strlen report.

Normal output aligns wrapped commands, case descriptions and expected/got values
under their respective text. ft_printf presents deliverables, Makefile checks,
the header's Norminette and interface check, then source Norminette and allowed
calls, with delimiters before the archive-symbol command and runtime tests.
Its numbered stages start
at 1 independently; the final project total still includes every executed case.

Libft checks its
Makefile first, then the header, then each function's Norm, allowed calls and
runtime. Its additional boundary and constructor-allocation campaigns precede
the additional NULL-safety probes. ft_printf presents the Makefile first, then
the header, then the source checks alongside the function's tests. Primary cases in both modules
already contain some valid boundary inputs; there is no universal strict
all-basic-then-all-robustness ordering.

Libft messages explain what the harness checked: character classifications report
the tested range instead of a wall of 0/1 values, memory tests name the returned
pointer, and string searches report a byte position. If a range check fails,
normal mode identifies the first incorrect input and its expected/actual result.
Internal encodings such as `|R1` are compared internally, then translated for
display; simplifying a message does not weaken the comparison.

Compact rows align function names left, tests in the center and results right.
They show `✓` / `✖` and the number passed/total. Long sequences use counts
such as `✓×125 ✖×2` to keep the table short. Failed cases show only their `✖`,
without descriptions or expected/actual values below the row. `TESTS:` explains
the marks and counts; result-code explanations are omitted. Compilation failures
keep their short label. A separator precedes the final result and score, including
when no advisory notes are present. Run without `--compact`
to see full test, compiler and precheck diagnostics.
The final Result line names each function and its actual status, as in normal mode.

Use the skip options only when you cannot run the relevant check. Exercises graded with a check
bypassed are reported as `SKIPPED`, never `OK`, and the final status becomes
`UNKNOWN` — because at that point claudenette can't tell you whether you'd pass.

## Reading the score

**The score counts only the leading run of consecutive `OK` results**, in exercise
order. The first failure stops the count, and later passing exercises contribute
nothing.

So if `ex00` fails and `ex01`–`ex08` all pass, your score is `0`. Fixing `ex08` will
not move it — fix `ex00` first. This is Claudenette's scoring rule; it does not
reconstruct the official evaluator's hidden tests or grading rules.

`Status: PASSED` at 50 or above.

### Exit status

The verdict is also the exit status, so a script or a git hook can act on it without
reading the output:

| Exit | Meaning |
| --- | --- |
| `0` | `Status: PASSED` |
| `1` | `Status: FAILED` |
| `2` | No verdict: `Status: UNKNOWN`, or claudenette couldn't grade at all (not a module directory, an unknown option, no exercise matched, a missing tool) |

```bash
claudenette && git push
```

### Statuses

| Status | Meaning |
| --- | --- |
| `OK` | Everything passed |
| `KO` | Your code compiled but behaved incorrectly |
| `NORM ERR` | Norminette violation |
| `FORBIDDEN FN` | You called a function the subject doesn't allow |
| `EXTRA FILES` | Files in the exercise directory the subject doesn't permit |
| `ABSENT` | The file you were meant to turn in isn't there |
| `SKIPPED` | Passed what ran, but a check was bypassed (see `--skip-norm` / `--skip-fn`) |
| `UNKNOWN` | A required check cannot be evaluated reliably in this environment; no final score |
| `TODO` | Claudenette has no test for this exercise yet — not your fault |
| `CRASH` | Claudenette's own test errored. A bug here, not necessarily in your code |

When more than one applies, the most severe wins:
`EXTRA FILES` > `NORM ERR` > `FORBIDDEN FN` > `CRASH` > `UNKNOWN` > `KO` > `SKIPPED` > `OK`.

### A house rule: NULL must not crash custom functions

For custom pointer-taking functions, Claudenette tests NULL arguments even when
the subject is silent. This is a **Claudenette house rule**, not an additional
requirement attributed to 42. Each probe changes one argument, keeps the others
valid and requires termination without a crash or hang. It does not invent a
return value where the subject specifies none.

When the subject explicitly requires reproducing a manual function, tests stay
within that manual's defined domain. NULL arguments with undefined behavior are
excluded, including Libft Part 1 pointer functions, C02 strcpy/strncpy/strlcpy,
C03 and C07 strdup. CLI projects receive real command-line and file inputs;
Claudenette does not call their `main` with fabricated NULL arguments.

A missing NULL guard in a custom function can therefore produce KO even when its
ordinary cases pass. Check the case description before interpreting the result.

### rush00 is scored differently

rush00's real grading is a random per-team draw across five variants with a bonus
above 100%, so it prints its own summary and scores `0` or `100`–`125`.

### libft

libft is graded from the root of your project repository — the directory holding your
`Makefile`, `libft.h` and `ft_*.c` files — because that is where the subject says they
must live. The deliverables are `Makefile`, `libft.h`, `ft_*.c` and `README.md`.
`.git` is repository metadata. Object files, archives and `.gitignore` are extra
files. Run `make fclean` before grading a directory where you have built the library.

Three things are checked beyond the individual functions:

- **Your `Makefile`**, in a scratch copy of your sources: that `$(NAME)`, `all`, `clean`,
  `fclean` and `re` work, that `-Wall -Wextra
  -Werror` reach the compiler and `-std=c99` doesn't, that a second `make` doesn't
  relink, and that `libft.a` came from `ar` rather than the forbidden `libtool` — and
  actually contains every function you turned in, since a file missing from `SRCS` is
  invisible to every other test.
- **Your `libft.h`**, compiled on its own: it must build without help from your `.c`
  files and declare all 43 mandatory functions with the subject's prototypes. Each one
  gets its own line, so while you work the declarations you already have show as correct,
  and each missing one says whether its `.c` is written yet — the key stays `KO` until
  the header is complete.
- **`ft_memset`, `ft_bzero`, `ft_memcpy` and `ft_memmove`** are additionally checked for
  calls to the libc functions they reimplement, and no file may use `restrict`, which the
  subject forbids in your prototypes.

Your `README.md` is checked too, but only as a **note**: what it lacks from the subject's
"Readme Requirements" (the italic first line, `Description`, `Instructions`, `Resources`)
is printed in yellow above the score and never changes it, because the README is judged by
your peers at the defense, not by the moulinette.

Tests run in subject order: **Makefile**, **libft.h**, then **Part 1**, **Part 2**
and **Part 3**. Filters preserve that order, as does the final summary. Subject 19.3
has no bonus part: all nine linked-list functions are mandatory, use `ft_lst*.c`
filenames, and must be included by the normal `make` target. Missing list functions
report `ABSENT` and affect the score like any other required function.

## ft_printf

The tester follows subject 12.1. Run it from a directory named `ft_printf`, with
its Makefile and `ft_printf.h`. Source/header subdirectories and the supplied
Libft are supported. Builds run in scratch copies.

The submission check accepts source/header directories and the supplied Libft's
Makefile, and checks their contents recursively. Object files, archives and
`.gitignore` are extra files, including inside source directories. Run `make fclean`
before grading a previously built submission. README.md remains permitted at the
root, and `.git` is repository metadata. Grading builds only its temporary copies.

As in Libft, missing README.md requirements (the italic first line and
`Description`, `Instructions`, `Resources` sections) produce advisory notes above
the score in both output modes, without changing the grade.

Checks cover the Makefile rules, flags, archive format, `ft_printf` symbol and
header prototype, followed by conversions in subject order `c s p d i u x X %`.
Normal output identifies the archive symbol check and its allowed external
functions (`malloc`, `free`, `write`), with supplied Libft calls resolved from the
archive. The allowed-call display also names the standard variadic macros
`va_start`, `va_arg`, `va_copy` and `va_end`; these are not external symbols.
Internal harness compilation commands and success messages are hidden;
compilation errors remain visible.
Each case compares every emitted byte and the returned count using a Linux/glibc
64-bit target. Native libc supplies the portable conversions; NULL `%p` arguments
use glibc's `(nil)` spelling and matching count, including mixed and width cases.
Literal strings are never globally rewritten, and non-NULL pointers retain their
exact value. On macOS this adapts known expectations without requiring a VM.
Hosts outside the supported Linux/macOS LP64 data model produce UNKNOWN.
A diagnosed failure to prepare guarded strings or capture output also produces
UNKNOWN, without a final score.
Cases include embedded zero bytes, integer limits, real object pointers, long
strings, mixed conversions, repeated calls, output errors and allocation cleanup.
Memory checks include scoped allocation failures, heap guards and strings ending
at a protected memory boundary. Write errors are tested both before and after
partial output. A recovered allocation failure is accepted when output and return
count remain correct and temporary memory is freed.

Write-error and memory failures remain decisive robustness checks. A negative
return is required after an output error; official coverage of these particular
campaigns is not assumed. NULL formats, NULL `%s` and other undefined inputs
remain outside the test domain.

A declared `bonus` target enables two separate optional groups. One covers
`-0.`, width and precision. The other covers `#`, space and `+`. Precision checks
include bounded strings without a terminating zero, within libc's defined domain.
Target discovery respects expanded Makefile rules and conditions. Bonus assessment
requires a complete mandatory pass. A failed optional group preserves the
mandatory score. Filter by `ft_printf_bonus_width` or `ft_printf_bonus_signs` to
inspect one group; a bonus-only run has an incomplete mandatory verdict.

Invalid formats, mismatched argument types and undefined flag/conversion pairs
are outside the test domain. The runner uses the existing detailed and compact
layouts. The public runtime needs the installed compiler, make, ar and nm.

## Known gaps

- Validation on an actual 42 campus machine remains pending, including
  installation without sudo. Automated macOS and Ubuntu checks have run.
- Every exercise in every module now has a test — nothing reports `TODO`.
- `norminette` is pinned in `requirements.txt` (currently 3.3.60), because two point
  releases disagreed on files that aren't C. If 42 moves to a newer norminette,
  claudenette follows only once that pin moves.
- `bsq`, the rushes and the shell modules are graded, but their tests have had less
  adversarial review than `C00`–`C13`, so a gap is likelier there than elsewhere.
- Libft's 21 libc-comparable functions have an independent system oracle. The other
  22 have alternative correct implementations, plus allocation-failure campaigns
  for all ten constructors. `ft_split` results are freed word by word; `ft_lstmap`
  checks independent nodes, source preservation, and valid identity/NULL callbacks.
  These checks cover the exercised inputs and failure positions; they are not a
  proof of correctness for every possible submission.
- ft_printf has automated positive/negative controls on Linux and macOS.

## Subjects

The subject PDFs are 42's own course material and are **not** distributed here. Get
them from the intranet. Claudenette never reads them at runtime — they're only
needed if you want to check a rule yourself.

## License

MIT — see [LICENSE](LICENSE).

## Test acknowledgments

Test inputs and contract ideas were adapted from the Francinette ecosystem,
including Alelievr, Fsoares, Tripouille, War Machine and its C Piscine suites.
Credits include Francisco / fsoares-, alelievr, Tripouille, cacharle, jtoty, badam and their
contributors. Claudenette uses its own harnesses and interface.

The public distribution contains the grader, its C harnesses and the small
runtime resources used by C09 and shell00. Internal documentation, developer
tools, reference submissions, subject PDFs, knowledge graphs and AI setup remain
local. No developer fixture suite or Docker installation is required to run it.
