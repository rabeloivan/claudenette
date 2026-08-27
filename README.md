# Claudenette

A local reimplementation of 42's **moulinette** for the C Piscine. Point it at your
own submission directory and it grades the exercises the way the real one does —
norm, forbidden functions, extra files, and the actual behaviour of your code.

Covers **C00–C13**, **rush00 / rush01 / rush02**, **bsq**, and **shell00 / shell01**.

> Claudenette is an unofficial study aid. It is not affiliated with 42, and passing
> here does not guarantee passing the real moulinette. Always test your own work.

## Install

```bash
git clone https://github.com/rabeloivan/claudenette.git ~/claudenette
pip install -r ~/claudenette/requirements.txt
```

### Prerequisites

| Tool | How to get it |
| --- | --- |
| `rich` | `pip install -r requirements.txt` |
| `norminette` | `pip install -r requirements.txt` (it's on PyPI) |
| `cc` | your system C toolchain — macOS: `xcode-select --install`, Debian/Ubuntu: `sudo apt install build-essential` |
| `nm` | ships with the same toolchain as `cc` (`binutils` on Debian/Ubuntu) |

If any of these is missing, claudenette **refuses to run** rather than reporting a
pass for a check it never performed. If you're doing the C Piscine you already have
`cc` and `nm`.

The same applies to a tool an individual exercise is graded *against*: `C10 ex03` is
diffed against the real `hexdump`, so without it that one exercise is refused **by
name**, rather than marked wrong. Grading the rest still works —
`python3 ~/claudenette/main.py ex00 ex01`.

## Usage

Run it **from inside your exercise directory** — the directory's *name* is what
selects the tests:

```bash
cd ~/piscine/C01
python3 ~/claudenette/main.py
```

That directory must be named `C00`–`C13`, or `rush00` / `rush01` / `rush02` / `bsq` /
`shell00` / `shell01` (the project names are case-insensitive). Anything else exits
with an error. **This is the most common first-run mistake** — running from the repo
itself, or from a parent folder, will not work. Claudenette is the grader, not the
submissions.

Grade a subset by passing substring filters, matched against exercise paths:

```bash
python3 ~/claudenette/main.py ex03 ex04
```

### Options

| Flag | Effect |
| --- | --- |
| `--skip-norm` | Grade without running norminette |
| `--skip-fn` | Grade without the forbidden-function check |

Use these only if you genuinely can't install the tool. Exercises graded with a check
bypassed are reported as `SKIPPED`, never `OK`, and the final status becomes
`UNKNOWN` — because at that point claudenette can't tell you whether you'd pass.

## Reading the score

**The score counts only the leading run of consecutive `OK` results**, in exercise
order. The first failure stops the count, and later passing exercises contribute
nothing.

So if `ex00` fails and `ex01`–`ex08` all pass, your score is `0`. Fixing `ex08` will
not move it — fix `ex00` first. This mirrors the real moulinette and is deliberate,
not a bug.

`Status: PASSED` at 50 or above.

### Statuses

| Status | Meaning |
| --- | --- |
| `OK` | Everything passed |
| `KO` | Your code compiled but behaved incorrectly |
| `NORM ERR` | Norm violation |
| `FORBIDDEN FN` | You called a function the subject doesn't allow |
| `EXTRA FILES` | Files in the exercise directory the subject doesn't permit |
| `ABSENT` | The file you were meant to turn in isn't there |
| `SKIPPED` | Passed what ran, but a check was bypassed (see `--skip-norm` / `--skip-fn`) |
| `TODO` | Claudenette has no test for this exercise yet — not your fault |
| `CRASH` | Claudenette's own test errored. A bug here, not necessarily in your code |

When more than one applies, the most severe wins:
`EXTRA FILES` > `NORM ERR` > `FORBIDDEN FN` > `CRASH` > `KO` > `SKIPPED` > `OK`.

### A house rule: NULL must not crash you

Claudenette is **stricter than the subject** on one point, deliberately. If a function
takes a pointer, claudenette calls it with `NULL` and requires it not to segfault —
even for exercises whose subject says nothing about NULL at all.

Most C01 exercises are like this. The subject for `ft_ft` says only "takes a pointer to
an int as a parameter and sets the value of that int to 42", so this is a perfectly
faithful answer to the question asked:

```c
void	ft_ft(int *nbr)
{
	*nbr = 42;
}
```

and claudenette fails it. Add the guard:

```c
void	ft_ft(int *nbr)
{
	if (!nbr)
		return ;
	*nbr = 42;
}
```

The reasoning is that a segfault in front of an evaluator costs you the defense whether
or not the subject mentioned it, so it is worth being told now. But it does mean a
`KO` here is not always evidence that you misread the subject — check whether it is
just the NULL case. Remember the scoring rule too: one failure at `ex00` zeroes every
exercise after it, so a missing NULL guard early in a module can read as a total
failure.

### rush00 is scored differently

rush00's real grading is a random per-team draw across five variants with a bonus
above 100%, so it prints its own summary and scores `0` or `100`–`125`.

## Known gaps

- Every exercise in every module now has a test — nothing reports `TODO`.
- Norm checking depends on whichever `norminette` version pip installs; if 42 updates
  the norm, claudenette follows only once you upgrade it.
- `bsq`, the rushes and the shell modules are graded, but their tests have had less
  adversarial review than `C00`–`C13`, so a gap is likelier there than elsewhere.

## Subjects

The subject PDFs are 42's own course material and are **not** distributed here. Get
them from the intranet. Claudenette never reads them at runtime — they're only
needed if you want to check a rule yourself.

Two small exception files do ship: `tests/shell00/ex07/fixture/{a.txt,sw.diff}`. That
exercise asks you to produce a file `b` such that `diff a b > sw.diff`, so `b` has no
defined content without those two — the grader reads them on every run, and cannot
check the exercise at all otherwise. Unlike the PDFs, they aren't documentation; they
are the reference data the check is made of.

## License

MIT — see [LICENSE](LICENSE).
