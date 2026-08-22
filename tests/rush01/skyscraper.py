def count_visible(sequence):
    count = 0
    tallest = 0
    for h in sequence:
        if h > tallest:
            count += 1
            tallest = h
    return count


def compute_clues(grid):
    n = len(grid)
    cols = list(zip(*grid))
    col_top = [count_visible(cols[c]) for c in range(n)]
    col_bottom = [count_visible(tuple(reversed(cols[c]))) for c in range(n)]
    row_left = [count_visible(grid[r]) for r in range(n)]
    row_right = [count_visible(tuple(reversed(grid[r]))) for r in range(n)]
    return col_top + col_bottom + row_left + row_right


def is_latin_square(grid, n):
    for row in grid:
        if sorted(row) != list(range(1, n + 1)):
            return False
    for c in range(n):
        col = [grid[r][c] for r in range(n)]
        if sorted(col) != list(range(1, n + 1)):
            return False
    return True


def is_valid_solution(grid, clues, n=4):
    if len(grid) != n or any(len(row) != n for row in grid):
        return False
    if not is_latin_square(grid, n):
        return False
    return compute_clues(grid) == list(clues)


def solve(clues, n=4):
    # Row-major, increasing-value backtracking - matches the traversal order
    # of the C reference solution, so "the first solution encountered" is
    # the same grid on both sides for exact-match test cases.
    grid = [[0] * n for _ in range(n)]

    def backtrack(pos):
        if pos == n * n:
            return compute_clues(grid) == list(clues)
        row, col = divmod(pos, n)
        for val in range(1, n + 1):
            if any(grid[row][c2] == val for c2 in range(col)):
                continue
            if any(grid[r2][col] == val for r2 in range(row)):
                continue
            grid[row][col] = val
            if backtrack(pos + 1):
                return True
            grid[row][col] = 0
        return False

    if backtrack(0):
        return [row[:] for row in grid]
    return None


def count_solutions(clues, n=4, limit=2):
    grid = [[0] * n for _ in range(n)]
    found = [0]

    def backtrack(pos):
        if found[0] >= limit:
            return
        if pos == n * n:
            if compute_clues(grid) == list(clues):
                found[0] += 1
            return
        row, col = divmod(pos, n)
        for val in range(1, n + 1):
            if any(grid[row][c2] == val for c2 in range(col)):
                continue
            if any(grid[r2][col] == val for r2 in range(row)):
                continue
            grid[row][col] = val
            backtrack(pos + 1)
            grid[row][col] = 0
            if found[0] >= limit:
                return

    backtrack(0)
    return found[0]


def wire(clues):
    return " ".join(str(c) for c in clues)


def grid_to_output(grid):
    return "\n".join(" ".join(str(v) for v in row) for row in grid) + "\n"


def parse_grid(output):
    try:
        return [[int(x) for x in row.split()] for row in output.rstrip("\n").split("\n")]
    except ValueError:
        return None
