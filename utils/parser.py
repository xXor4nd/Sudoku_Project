"""
parser.py: Parsing and formatting utilities for Sudoku grids.
"""

import math

SYMBOLS = "123456789ABCDEFGHIJKLMNOP"


def parse_puzzle_string(puzzle_str):
    """
    Chuyển đổi chuỗi Sudoku (1 dòng hoặc nhiều dòng) thành ma trận số nguyên N x N.
    Hỗ trợ 2 định dạng:
    1. Delimited Integer Format: Các số cách nhau bởi dấu cách (ví dụ: '0 12 36 0 ...'),
       thích hợp cho ma trận lớn (36x36, 49x49, v.v.). Ô trống là 0 hoặc '.'.
    2. Single-character Format: Chuỗi ký tự liên tiếp ('1'-'9', 'A'-'P', '.' cho ô trống).
    """
    stripped = puzzle_str.strip()
    if not stripped:
        raise ValueError("Empty puzzle string.")

    tokens = stripped.split()
    total_tokens = len(tokens)
    N_from_tokens = math.isqrt(total_tokens)

    # Check for space-delimited integer format
    if total_tokens > 1 and N_from_tokens * N_from_tokens == total_tokens:
        first_token = tokens[0]
        if first_token.isdigit() or first_token in (".", "-", "0"):
            grid = []
            for i in range(N_from_tokens):
                row = []
                for j in range(N_from_tokens):
                    tk = tokens[i * N_from_tokens + j]
                    row.append(0 if tk in (".", "-", "0") else int(tk))
                grid.append(row)
            return grid

    # Single-character format (N <= 25)
    clean_str = (
        "".join(ch for ch in puzzle_str if not ch.isspace())
        .upper()
        .replace("0", ".")
        .replace("-", ".")
    )
    if not clean_str:
        raise ValueError("Empty puzzle string.")

    N = math.isqrt(len(clean_str))
    if N * N != len(clean_str):
        raise ValueError(f"String length {len(clean_str)} is not a square (N x N).")

    val_map = {ch: idx + 1 for idx, ch in enumerate(SYMBOLS[:N])}
    val_map["."] = 0

    return [
        [val_map[clean_str[i * N + j]] for j in range(N)] for i in range(N)
    ]


def grid_to_string(grid, delimited=None):
    """
    Chuyển ma trận Sudoku N x N thành chuỗi 1 dòng.
    - Với N > 25 hoặc delimited=True: định dạng số nguyên phân cách bằng dấu cách ('0 12 35 ...').
    - Với N <= 25 và delimited=False: định dạng chuỗi ký tự liền nhau ('..1.A...').
    """
    N = len(grid)
    if delimited is None:
        delimited = (N > 25)

    if delimited:
        return " ".join(str(grid[r][c]) for r in range(N) for c in range(N))

    chars = []
    for r in range(N):
        for c in range(N):
            val = grid[r][c]
            chars.append(SYMBOLS[val - 1] if val > 0 else ".")
    return "".join(chars)


def print_grid(grid):
    """
    In ma trận Sudoku dạng bảng trực quan chia theo các khối b x b.
    Tự động căn chỉnh độ rộng cột theo kích thước N.
    """
    if grid is None:
        print("No solution to display.")
        return

    N = len(grid)
    b = math.isqrt(N)
    cell_w = len(str(N))

    for i in range(N):
        if i % b == 0 and i > 0:
            block_sep = "-+-".join(["-" * (b * (cell_w + 1) - 1)] * b)
            print(block_sep)
        row = []
        for j in range(N):
            if j % b == 0 and j > 0:
                row.append("|")
            val = grid[i][j]
            if val > 0:
                text = SYMBOLS[val - 1] if N <= 25 else str(val)
                row.append(text.rjust(cell_w))
            else:
                row.append(".".rjust(cell_w))
        print(" ".join(row))
