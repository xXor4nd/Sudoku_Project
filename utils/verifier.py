"""
verifier.py: Independent solution and dataset verifier for Sudoku.
Validates:
1. Consistency with givens (clues).
2. All-different in each row.
3. All-different in each column.
4. All-different in each subgrid box.
"""

import os
import sys
import math

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.parser import parse_puzzle_string


def verify_sudoku_solution(grid, original_puzzle=None):
    """
    Verify whether a solved grid satisfies all Sudoku rules and matches the original clues.
    Returns True if valid, False otherwise.
    """
    if grid is None:
        return False

    N = len(grid)
    if N == 0:
        return False

    b = math.isqrt(N)
    if b * b != N:
        return False

    full_set = set(range(1, N + 1))

    # Check consistency with original clues
    if original_puzzle is not None:
        for i in range(N):
            for j in range(N):
                orig_val = original_puzzle[i][j]
                if orig_val != 0 and orig_val != grid[i][j]:
                    return False

    # Check rows
    for i in range(N):
        if set(grid[i]) != full_set:
            return False

    # Check columns
    for j in range(N):
        col_vals = set(grid[i][j] for i in range(N))
        if col_vals != full_set:
            return False

    # Check boxes
    for block_row in range(b):
        for block_col in range(b):
            block_vals = set(
                grid[block_row * b + di][block_col * b + dj]
                for di in range(b)
                for dj in range(b)
            )
            if block_vals != full_set:
                return False

    return True


def verify_puzzle_clues(grid):
    """
    Kiểm tra tính nhất quán và hợp lệ của đề bài Sudoku (chưa giải):
    1. Kích thước N x N phải là số chính phương (N = b^2).
    2. Các ô cho sẵn (clues > 0) phải nằm trong đoạn [1, N].
    3. Không có hai ô cùng hàng, cùng cột, hoặc cùng khối bxb có cùng giá trị > 0.
    Trả về: (True, "") nếu hợp lệ, (False, error_message) nếu vi phạm.
    """
    if grid is None or len(grid) == 0:
        return False, "Empty or None grid."

    N = len(grid)
    b = math.isqrt(N)
    if b * b != N:
        return False, f"Grid size N={N} is not a perfect square."

    for r_idx, row in enumerate(grid):
        if len(row) != N:
            return False, f"Row {r_idx} length {len(row)} != {N}."

    # Check row conflicts
    for i in range(N):
        seen = set()
        for j in range(N):
            val = grid[i][j]
            if val != 0:
                if not (1 <= val <= N):
                    return False, f"Cell ({i}, {j}) value {val} out of range [1, {N}]."
                if val in seen:
                    return False, f"Duplicate value {val} in row {i}."
                seen.add(val)

    # Check column conflicts
    for j in range(N):
        seen = set()
        for i in range(N):
            val = grid[i][j]
            if val != 0:
                if val in seen:
                    return False, f"Duplicate value {val} in column {j}."
                seen.add(val)

    # Check box conflicts
    for br in range(b):
        for bc in range(b):
            seen = set()
            for di in range(b):
                for dj in range(b):
                    val = grid[br * b + di][bc * b + dj]
                    if val != 0:
                        if val in seen:
                            return False, f"Duplicate value {val} in box ({br}, {bc})."
                        seen.add(val)

    return True, ""


def verify_dataset_file(file_path, expected_size):
    """
    Kiểm tra toàn bộ các đề Sudoku trong một file dataset:
    - Parse từng đề thành ma trận N x N.
    - Kiểm tra tính nhất quán của các clues.
    """
    import os

    if not os.path.isfile(file_path):
        return None

    puzzles = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for idx, line in enumerate(f, 1):
            s = line.strip()
            if s and not s.startswith("#"):
                puzzles.append((idx, s))

    total = len(puzzles)
    parse_ok = 0
    clues_ok = 0

    for line_no, p_str in puzzles:
        try:
            grid = parse_puzzle_string(p_str)
        except Exception:
            continue

        if len(grid) != expected_size or any(len(r) != expected_size for r in grid):
            continue
        parse_ok += 1

        is_valid, _ = verify_puzzle_clues(grid)
        if is_valid:
            clues_ok += 1

    return {
        "file": os.path.basename(file_path),
        "size": expected_size,
        "total": total,
        "parse_ok": parse_ok,
        "clues_ok": clues_ok,
        "is_all_valid": (parse_ok == total and clues_ok == total and total > 0)
    }


if __name__ == "__main__":
    import os
    import sys

    curr_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(curr_dir)
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
    data_dir = os.path.join(root_dir, "data")

    datasets = [
        ("16x16_puzzles.txt", 16),
        ("25x25_puzzles.txt", 25),
        ("36x36_puzzles.txt", 36),
        ("49x49_puzzles.txt", 49),
    ]

    print("Verifying dataset files...")
    for fname, size in datasets:
        fpath = os.path.join(data_dir, fname)
        res = verify_dataset_file(fpath, size)
        if res is None:
            print(f"  {fname}: file not found")
        else:
            status = "PASSED" if res["is_all_valid"] else "FAILED"
            print(f"  {fname} ({size}x{size}): {res['clues_ok']}/{res['total']} valid [{status}]")
