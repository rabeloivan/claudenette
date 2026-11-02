def parse_map(text):
    # Returns (grid, body_lines, empty_c, obstacle_c, full_c) or None if the
    # text does not describe a valid map, per every rule in the subject.
    if not text:
        return None
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if not lines:
        return None
    first = lines[0]
    if len(first) < 4:
        return None
    special = first[-3:]
    if len(set(special)) != 3:
        return None
    if not all(c.isprintable() for c in special):
        return None
    count_str = first[:-3]
    if not count_str.isdigit():
        return None
    n = int(count_str)
    if n <= 0:
        return None
    empty_c, obstacle_c, full_c = special[0], special[1], special[2]
    body = lines[1:]
    if len(body) != n:
        return None
    width = len(body[0]) if body else 0
    if width == 0:
        return None
    for row in body:
        if len(row) != width:
            return None
        for c in row:
            # The subject: "The map is made up of lines containing 'empty'
            # characters and 'obstacle' characters" - full_c is introduced in
            # the header but is output-only, never valid in the input body.
            if c not in (empty_c, obstacle_c):
                return None
    grid = [[1 if c == empty_c else 0 for c in row] for row in body]
    return (grid, body, empty_c, obstacle_c, full_c)


def find_biggest_square(grid):
    # DP: dp[i][j] = size of the largest all-empty square with its
    # bottom-right corner at (i, j). Scanning row-major and only updating
    # "best" on a *strictly* greater size (never >=) keeps the first
    # (topmost, then leftmost) square among ties - see CLAUDE.md for the
    # proof this is equivalent to comparing top-left corners directly.
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    if rows == 0 or cols == 0:
        return (0, 0, 0)
    dp = [[0] * cols for _ in range(rows)]
    best_size = 0
    best_row = 0
    best_col = 0
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == 1:
                if i == 0 or j == 0:
                    dp[i][j] = 1
                else:
                    dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1
                if dp[i][j] > best_size:
                    best_size = dp[i][j]
                    best_row = i - dp[i][j] + 1
                    best_col = j - dp[i][j] + 1
    return (best_size, best_row, best_col)


def render_output(body_lines, size, top_row, top_col, full_c):
    if size == 0:
        return "\n".join(body_lines) + "\n"
    out_lines = []
    for i, row in enumerate(body_lines):
        if top_row <= i < top_row + size:
            row = row[:top_col] + full_c * size + row[top_col + size:]
        out_lines.append(row)
    return "\n".join(out_lines) + "\n"


def solve_map(text):
    parsed = parse_map(text)
    if parsed is None:
        return "map error\n"
    grid, body, empty_c, obstacle_c, full_c = parsed
    size, top_row, top_col = find_biggest_square(grid)
    return render_output(body, size, top_row, top_col, full_c)
