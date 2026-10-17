"""
data_loader.py: Dataset loader for Sudoku benchmark puzzles.
"""

import os
import random

DATA_FILES = {
    9: "9x9_17_clue.txt",
    16: "16x16_puzzles.txt",
    25: "25x25_puzzles.txt",
    36: "36x36_puzzles.txt",
    49: "49x49_puzzles.txt",
}


def load_puzzles_from_file(file_path, limit=None, seed=None):
    """
    Đọc danh sách chuỗi đề Sudoku từ một file text.
    - Bỏ qua các dòng chú thích bắt đầu bằng '#' hoặc dòng trống.
    - Mỗi dòng hợp lệ là một chuỗi đề tương ứng.
    - Nếu có limit và seed, chọn ngẫu nhiên có lặp lại kết quả theo seed.
    - Nếu có limit và không có seed, lấy limit dòng đầu tiên.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    puzzles = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            puzzles.append(stripped)

    if limit is not None and limit < len(puzzles):
        if seed is not None:
            rng = random.Random(seed)
            return rng.sample(puzzles, limit)
        return puzzles[:limit]

    return puzzles


def get_dataset_path(size, data_dir="data"):
    """Lấy đường dẫn file dataset tương ứng với kích thước ma trận size x size."""
    if size not in DATA_FILES:
        raise ValueError(f"No dataset configured for size {size}x{size}.")
    return os.path.join(data_dir, DATA_FILES[size])


def load_benchmark_dataset(size=9, count=5, data_dir="data", seed=2026):
    """
    Nạp count đề bài cho kích thước size x size từ thư mục dataset data_dir.
    """
    file_path = get_dataset_path(size, data_dir=data_dir)
    return load_puzzles_from_file(file_path, limit=count, seed=seed)
