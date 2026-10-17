"""
generator.py: Generates valid Sudoku puzzles of arbitrary size with unique or valid solutions.
"""

import os
import sys
import random

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.parser import SYMBOLS


def generate_sudoku(box_size=4, blank_ratio=0.60, seed=42, delimited=None):
    """
    Sinh Sudoku có ít nhất một nghiệm hợp lệ với kích thước tùy biến:
    - box_size=3 -> Sudoku 9x9
    - box_size=4 -> Sudoku 16x16
    - box_size=5 -> Sudoku 25x25
    - box_size=6 -> Sudoku 36x36 (Định dạng số nguyên cách nhau bởi dấu cách)
    - box_size=7 -> Sudoku 49x49 (Định dạng số nguyên cách nhau bởi dấu cách)

    blank_ratio: tỷ lệ ô bị xóa, từ 0 đến 1.
    seed: giúp tái tạo đúng bộ đề khi chạy lại.
    delimited: True nếu muốn xuất dạng số nguyên phân cách; mặc định True khi N > 25.
    """
    N = box_size * box_size

    if delimited is None:
        delimited = (N > 25)

    if not delimited and N > len(SYMBOLS):
        delimited = True

    if not 0 <= blank_ratio <= 1:
        raise ValueError("blank_ratio must be between 0 and 1.")

    rng = random.Random(seed)

    # Xáo trộn các nhóm hàng/cột và thứ tự bên trong mỗi nhóm.
    def shuffled_indices():
        groups = list(range(box_size))
        rng.shuffle(groups)

        indices = []
        for group in groups:
            within = list(range(box_size))
            rng.shuffle(within)
            indices.extend(group * box_size + x for x in within)
        return indices

    rows = shuffled_indices()
    cols = shuffled_indices()

    # Mẫu Sudoku hoàn chỉnh hợp lệ
    def pattern(r, c):
        return (box_size * (r % box_size) + r // box_size + c) % N

    all_cells = [(r, c) for r in range(N) for c in range(N)]
    blank_count = round(N * N * blank_ratio)
    blank_positions = set(rng.sample(all_cells, blank_count))

    if delimited:
        # Sử dụng số nguyên 1..N trực tiếp
        values = list(range(1, N + 1))
        rng.shuffle(values)

        solution = [
            [values[pattern(r, c)] for c in cols]
            for r in rows
        ]
        puzzle = [
            [
                0 if (r, c) in blank_positions else solution[r][c]
                for c in range(N)
            ]
            for r in range(N)
        ]
        puzzle_text = " ".join(str(val) for row in puzzle for val in row)
        solution_text = " ".join(str(val) for row in solution for val in row)
    else:
        # Sử dụng ký tự đơn SYMBOLS cho N <= 25
        symbols = list(SYMBOLS[:N])
        rng.shuffle(symbols)

        solution = [
            [symbols[pattern(r, c)] for c in cols]
            for r in rows
        ]
        puzzle = [
            [
                "." if (r, c) in blank_positions else solution[r][c]
                for c in range(N)
            ]
            for r in range(N)
        ]
        puzzle_text = "\n".join("".join(row) for row in puzzle)
        solution_text = "\n".join("".join(row) for row in solution)

    return puzzle_text, solution_text
