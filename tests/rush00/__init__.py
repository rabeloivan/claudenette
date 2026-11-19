from .ex00.test_ex00 import run_C_rush00


def get_mapping():
    return {
        "ex00/ft_putchar.c": (
            "rush00",
            run_C_rush00,
            ["write"],
            {"allowed_files": ["main.c", "rush0[0-4].c"],
             # Shown with ft_putchar.c; each verdict still counts where the runner uses it.
             "display_sources": ["main.c", "rush0[0-4].c"]},
        ),
    }
