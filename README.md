# Claudenette

A local tester for 42 projects. Run it inside your project directory and it checks
what the Moulinette would look at: norminette, forbidden functions, the files you turn
in, and how your code behaves.

> Claudenette is an unofficial study aid, not affiliated with 42. Its tests are its
> own, not the Moulinette's, so passing here does not guarantee passing there.

```
~/libft $> claudenette --compact ft_strlen ft_strlcpy ft_strchr ft_strdup ft_split

FUNCTION                                   TESTS                                      RESULT
ft_strlen                              ✓×27  (27/27)                                      OK
ft_strlcpy                    ✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓  (23/23)                            OK
ft_strchr                           ✓×16  ✖×22  (16/38)                                   KO
ft_strdup                              ✓×25  (25/25)                                      OK
ft_split                               ✓×32  (32/32)                                      OK

Result:      ft_strlen: OK, ft_strlcpy: OK, ft_strchr: KO, ft_strdup: OK, ft_split: OK
Final score: 40/100
Status:      FAILED
```

## Table of Contents

1. [Why](#why)
2. [Install](#install)
3. [Usage](#usage)
4. [Supported projects](#supported-projects)
5. [Reading the result](#reading-the-result)
6. [FAQ](#faq)
7. [Update and uninstall](#update-and-uninstall)
8. [Acknowledgments](#acknowledgments)

## Why

Every failed evaluation costs a retry and a wait. Claudenette lets you catch the
silly mistakes before you submit: a norm error, a missing file, a crash on an empty
string, a leak when `malloc` fails.

It is a second opinion, not a replacement for your own tests. Write a `main`, think
about the corner cases, and then let Claudenette look for the ones you missed.

## Install

Target: **Ubuntu 22.04** (the campus machines), Python 3.10 or newer. No sudo needed.

```bash
git clone https://github.com/rabeloivan/claudenette.git ~/claudenette
python3 ~/claudenette/install.py
```

The installer puts its Python dependencies (`rich`, `norminette`) in
`~/claudenette/.deps/` and changes nothing else on your system. The C tools (`cc`,
`make`, `ar`, `nm`) come from the campus machine.

Then add an alias, so you can type `claudenette` anywhere. Use the line for the
shell you run (`echo $SHELL` tells you), on macOS and Ubuntu alike:

```bash
# zsh
echo "alias claudenette='python3 ~/claudenette/main.py'" >> ~/.zshrc && source ~/.zshrc
# bash
echo "alias claudenette='python3 ~/claudenette/main.py'" >> ~/.bashrc && source ~/.bashrc
# fish
echo "alias claudenette='python3 ~/claudenette/main.py'" >> ~/.config/fish/config.fish && source ~/.config/fish/config.fish
```

## Usage

Run it **from inside the project directory**. The directory's name tells Claudenette
which project to grade.

```
~/piscine/C01 $> claudenette                     # every exercise in C01
~/piscine/C01 $> claudenette ex03                # only ex03
~/piscine/C01 $> claudenette ex00 ex03           # ex00 and ex03
~/piscine/C01 $> claudenette ft_swap.c           # the exercise that turns in this file
~/libft       $> claudenette ft_strchr ft_split  # only these functions
~/libft       $> claudenette --compact           # one line per function, no details
```

Arguments are substring filters, so `ex0` matches `ex00` to `ex09`. A filtered run
scores only what it ran: run the whole project to know where you stand.

| Option | Effect |
| --- | --- |
| `--compact` | Show the summary table only, without the details of each case |
| `--skip-norm` | Do not run norminette |
| `--skip-fn` | Do not check for forbidden functions |

Without `--compact`, every case is shown with what was called, what was expected
and what your code returned.

## Supported projects

| Project | Run from | Good to know |
| --- | --- | --- |
| C00–C13 | `C00` … `C13` | |
| rush00, rush01, rush02 | `rush00` … | rush00 grades all five variants and scores 0 or 100–125 |
| bsq | `bsq` | |
| shell00, shell01 | `shell00`, `shell01` | |
| Piscine Reloaded (2.2) | `piscine_reloaded` or `piscine-reloaded` | Do not turn in `ft_putchar`: Claudenette supplies its own, like the Moulinette |
| libft (19.3) | your repository root | 43 mandatory functions, list functions included; no bonus. README is a note only |
| ft_printf (12.1) | `ft_printf` | A `bonus` rule enables two bonus groups. Output is compared against Linux/glibc, even on macOS |

Directory names are case-insensitive.

## Reading the result

| Status | Meaning |
| --- | --- |
| `OK` | Everything passed |
| `KO` | Your code compiled but behaved incorrectly |
| `NORM ERR` | Norminette error |
| `FORBIDDEN FN` | You called a function the subject does not allow |
| `EXTRA FILES` | Files the subject does not ask you to turn in |
| `ABSENT` | A file you must turn in is missing |
| `SKIPPED` | Passed what ran, but you skipped a check with `--skip-norm` or `--skip-fn` |
| `UNKNOWN` | A required check could not run reliably here; no score is given |
| `CRASH` | Claudenette itself failed. That is our bug, not necessarily yours |

When several apply, the most severe wins: `EXTRA FILES` > `NORM ERR` >
`FORBIDDEN FN` > `CRASH` > `UNKNOWN` > `KO` > `SKIPPED` > `OK`.

**The score stops at the first failure.** Exercises count in order, and the first
one that is not `OK` (or `SKIPPED`) ends the count. If `ex00` fails, the score is 0
no matter how many later exercises pass, so fix them in order. `PASSED` starts at 50.

**Bonus.** A bonus is graded only when the mandatory part is 100%. A complete bonus
gives 125/100; one of ft_printf's two bonus groups alone gives 112/100.
With `--skip-norm` or `--skip-fn` the bonus is still graded, but it adds no points
and the status is `UNKNOWN`.

**Exit code.** `0` for `PASSED`, `1` for `FAILED`, `2` when there is no verdict.
So `claudenette && git push` pushes only when you pass.

## FAQ

**"Current directory does not match expected pattern"**
You ran it from the wrong place. `cd` into the project directory itself (for example
`~/piscine/C01`, not `~/piscine`), and check that its name matches the table above.

**Everything is `EXTRA FILES`.**
The directory may contain only the files you turn in, plus `.git`. Object files,
`libft.a`, executables, `.gitignore` and logs all count. Run `make fclean` and move
other files out. Claudenette builds in a scratch copy, so it never adds files itself.

**I got KO for passing NULL, but the subject never mentions NULL.**
For functions you design yourself, Claudenette requires that NULL does not crash.
This is Claudenette's own rule, not 42's. Functions that reproduce a libc function,
like `ft_strlen` in Libft, are not tested with NULL.

**The Moulinette gave me 100, but Claudenette says KO.**
That is possible. Claudenette's tests are not the Moulinette's: it checks cases
such as `malloc` failures, write errors and memory leaks that the Moulinette may
not test. The case description tells you exactly what failed; it is usually worth
fixing.

**My bonus was not tested.**
The mandatory part is not 100% yet. Fix it first, then the bonus runs.

**It says a tool is missing.**
Claudenette refuses to grade without a tool it needs, rather than pass you without
checking (C10 ex03, for example, needs `hexdump`). Filtering to other exercises
avoids tools those exercises do not use.

**How reliable is it?**
Every exercise of every supported project is tested, on Ubuntu and macOS. Libft,
ft_printf and C00–C13 had the most review; bsq, the rushes and the shell modules had
less, so a gap is likelier there. Norminette is pinned to 3.3.60.

**Where are the subjects?**
The PDFs are 42's material and are not included. Get them from the intranet.

## Update and uninstall

Update:

```bash
cd ~/claudenette && git pull && python3 install.py
```

Uninstall: delete `~/claudenette` and remove the `claudenette` alias line from your
shell's config file (`~/.zshrc`, `~/.bashrc` or `~/.config/fish/config.fish`).

## Acknowledgments

Test inputs and ideas were adapted from the
[Francinette](https://github.com/xicodomingues/francinette) ecosystem: Alelievr,
Fsoares, Tripouille, War Machine and its C Piscine suites, with credit to Francisco /
fsoares-, alelievr, Tripouille, cacharle, jtoty, badam and their contributors.
Claudenette uses its own harnesses and interface.

The report style, with its banner, per-exercise results and a score that stops at the
first failure, follows [mini-moulinette](https://github.com/k11q/mini-moulinette) by
Khairul Haaziq (k11q), MIT license. No mini-moulinette code is included.

## License

MIT. See [LICENSE](LICENSE).
