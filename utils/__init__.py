"""
Utility modules for data loading, parsing, generation, verification, and plotting.
"""

from utils.parser import SYMBOLS, parse_puzzle_string, print_grid, grid_to_string
from utils.verifier import verify_sudoku_solution, verify_puzzle_clues
from utils.generator import generate_sudoku
from utils.sat_context import SatContext, get_var_id
from utils.data_loader import (
    load_puzzles_from_file,
    get_dataset_path,
    load_benchmark_dataset,
)
try:
    from utils.plots import generate_all_scientific_plots
except ImportError:
    generate_all_scientific_plots = None

__all__ = [
    "SYMBOLS",
    "parse_puzzle_string",
    "print_grid",
    "grid_to_string",
    "verify_sudoku_solution",
    "verify_puzzle_clues",
    "generate_sudoku",
    "SatContext",
    "get_var_id",
    "load_puzzles_from_file",
    "get_dataset_path",
    "load_benchmark_dataset",
    "generate_all_scientific_plots",
]
