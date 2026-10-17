"""
generate_datasets.py: Generates Sudoku benchmark datasets for large grid sizes (16x16 to 49x49)
with varying difficulty tiers and saves them to data/.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.generator import generate_sudoku
from utils.parser import parse_puzzle_string
from utils.verifier import verify_sudoku_solution


def generate_16x16_dataset(output_path="data/16x16_puzzles.txt"):
    """Generate 100 puzzles of size 16x16 across 4 difficulty tiers."""
    tiers = [
        ("Easy", 0.40, 25),
        ("Medium", 0.55, 25),
        ("Hard", 0.65, 25),
        ("VeryHard", 0.75, 25),
    ]

    lines = [
        "# SUDOKU 16x16 BENCHMARK DATASET",
        "# 100 puzzles: 25 Easy, 25 Medium, 25 Hard, 25 Very Hard",
    ]

    base_seed = 16000
    puzzle_idx = 1

    for tier_name, blank_ratio, count in tiers:
        lines.append(f"\n# Tier: {tier_name} (Blanks: {blank_ratio*100:.0f}%, Count: {count})")
        for _ in range(count):
            seed = base_seed + puzzle_idx
            p_text, s_text = generate_sudoku(box_size=4, blank_ratio=blank_ratio, seed=seed)
            single_line_p = "".join(ch for ch in p_text if not ch.isspace())
            single_line_s = "".join(ch for ch in s_text if not ch.isspace())

            grid_s = parse_puzzle_string(single_line_s)
            grid_p = parse_puzzle_string(single_line_p)
            assert verify_sudoku_solution(grid_s, grid_p), f"Invalid solution for puzzle {puzzle_idx}"

            lines.append(f"# ID={puzzle_idx:03d} Tier={tier_name} Seed={seed}")
            lines.append(single_line_p)
            puzzle_idx += 1

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Generated {puzzle_idx - 1} puzzles (16x16) -> {output_path}")


def generate_25x25_dataset(output_path="data/25x25_puzzles.txt"):
    """Generate 40 puzzles of size 25x25 across 4 difficulty tiers."""
    tiers = [
        ("Easy", 0.35, 10),
        ("Medium", 0.45, 10),
        ("Hard", 0.55, 10),
        ("VeryHard", 0.65, 10),
    ]

    lines = [
        "# SUDOKU 25x25 BENCHMARK DATASET",
        "# 40 puzzles: 10 Easy, 10 Medium, 10 Hard, 10 Very Hard",
    ]

    base_seed = 25000
    puzzle_idx = 1

    for tier_name, blank_ratio, count in tiers:
        lines.append(f"\n# Tier: {tier_name} (Blanks: {blank_ratio*100:.0f}%, Count: {count})")
        for _ in range(count):
            seed = base_seed + puzzle_idx
            p_text, s_text = generate_sudoku(box_size=5, blank_ratio=blank_ratio, seed=seed)
            single_line_p = "".join(ch for ch in p_text if not ch.isspace())
            single_line_s = "".join(ch for ch in s_text if not ch.isspace())

            grid_s = parse_puzzle_string(single_line_s)
            grid_p = parse_puzzle_string(single_line_p)
            assert verify_sudoku_solution(grid_s, grid_p), f"Invalid solution for puzzle {puzzle_idx}"

            lines.append(f"# ID={puzzle_idx:03d} Tier={tier_name} Seed={seed}")
            lines.append(single_line_p)
            puzzle_idx += 1

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Generated {puzzle_idx - 1} puzzles (25x25) -> {output_path}")


def generate_36x36_dataset(output_path="data/36x36_puzzles.txt"):
    """Generate 20 puzzles of size 36x36 in space-delimited format."""
    tiers = [
        ("Easy", 0.25, 5),
        ("Medium", 0.35, 5),
        ("Hard", 0.45, 5),
        ("VeryHard", 0.50, 5),
    ]

    lines = [
        "# SUDOKU 36x36 BENCHMARK DATASET",
        "# 20 puzzles: 5 Easy, 5 Medium, 5 Hard, 5 Very Hard",
    ]

    base_seed = 36000
    puzzle_idx = 1

    for tier_name, blank_ratio, count in tiers:
        lines.append(f"\n# Tier: {tier_name} (Blanks: {blank_ratio*100:.0f}%, Count: {count})")
        for _ in range(count):
            seed = base_seed + puzzle_idx
            p_text, s_text = generate_sudoku(box_size=6, blank_ratio=blank_ratio, seed=seed, delimited=True)

            grid_s = parse_puzzle_string(s_text)
            grid_p = parse_puzzle_string(p_text)
            assert verify_sudoku_solution(grid_s, grid_p), f"Invalid solution for puzzle {puzzle_idx}"

            lines.append(f"# ID={puzzle_idx:03d} Tier={tier_name} Seed={seed}")
            lines.append(p_text)
            puzzle_idx += 1

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Generated {puzzle_idx - 1} puzzles (36x36) -> {output_path}")


def generate_49x49_dataset(output_path="data/49x49_puzzles.txt"):
    """Generate 10 puzzles of size 49x49 in space-delimited format."""
    tiers = [
        ("Easy", 0.20, 3),
        ("Medium", 0.30, 3),
        ("Hard", 0.38, 2),
        ("VeryHard", 0.45, 2),
    ]

    lines = [
        "# SUDOKU 49x49 BENCHMARK DATASET",
        "# 10 puzzles: 3 Easy, 3 Medium, 2 Hard, 2 Very Hard",
    ]

    base_seed = 49000
    puzzle_idx = 1

    for tier_name, blank_ratio, count in tiers:
        lines.append(f"\n# Tier: {tier_name} (Blanks: {blank_ratio*100:.0f}%, Count: {count})")
        for _ in range(count):
            seed = base_seed + puzzle_idx
            p_text, s_text = generate_sudoku(box_size=7, blank_ratio=blank_ratio, seed=seed, delimited=True)

            grid_s = parse_puzzle_string(s_text)
            grid_p = parse_puzzle_string(p_text)
            assert verify_sudoku_solution(grid_s, grid_p), f"Invalid solution for puzzle {puzzle_idx}"

            lines.append(f"# ID={puzzle_idx:03d} Tier={tier_name} Seed={seed}")
            lines.append(p_text)
            puzzle_idx += 1

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Generated {puzzle_idx - 1} puzzles (49x49) -> {output_path}")


if __name__ == "__main__":
    generate_36x36_dataset()
    generate_49x49_dataset()
