"""
demo, test
"""

import argparse
from utils import (
    parse_puzzle_string,
    print_grid,
    verify_sudoku_solution,
    generate_sudoku,
)
from encoders import AMO_METHODS
from solvers import (
    SudokuSAT,
    SudokuCPSAT,
    SudokuGurobi,
    SudokuCplexMIP,
    SudokuCplexCP,
)

SAMPLE_PUZZLE_9x9 = ".................1.....2.3......3.2...1.4......5....6..3......4.7..8...962...7..."


def test_sat_solver(grid, amo="sequential"):
    print(f"\n--- Testing SAT Solver (AMO: {amo}) ---")
    solver = SudokuSAT(grid, amo_name=amo)
    sol, stats = solver.solve(solver_name="glucose4")
    valid = verify_sudoku_solution(sol, original_puzzle=grid)

    print(f"Status: {stats['status']} (Valid: {valid})")
    print(f"Variables: {stats['num_total_vars']} | Clauses: {stats['num_clauses']}")
    print(f"Encode: {stats['time_encode_sec']*1000:.2f} ms | Solve: {stats['time_solve_sec']*1000:.2f} ms | Total: {stats['time_total_sec']*1000:.2f} ms")

    if sol:
        print("\nSolution:")
        print_grid(sol)
    return sol


def compare_amo_methods(grid):
    print("\n--- Comparing 5 SAT AMO Encodings ---")
    print(f"{'Method':<16} | {'Variables':<10} | {'Clauses':<10} | {'Encode (ms)':<12} | {'Solve (ms)':<12} | {'Valid'}")
    print("-" * 75)

    last_sol = None
    for amo in AMO_METHODS:
        model = SudokuSAT(grid, amo_name=amo)
        sol, stats = model.solve(solver_name="glucose4")
        valid = verify_sudoku_solution(sol, original_puzzle=grid)
        if valid:
            last_sol = sol

        enc_ms = stats["time_encode_sec"] * 1000
        slv_ms = stats["time_solve_sec"] * 1000
        print(f"{amo:<16} | {stats['num_total_vars']:<10} | {stats['num_clauses']:<10} | {enc_ms:<12.2f} | {slv_ms:<12.2f} | {valid}")

    if last_sol:
        print("\nSolution:")
        print_grid(last_sol)


def test_cross_solvers(grid):
    print("\n--- Cross-Paradigm Comparison (SAT vs CP vs ILP) ---")
    solvers = [
        ("SAT (Glucose4)", lambda: SudokuSAT(grid, amo_name="sequential").solve(solver_name="glucose4")),
        ("CP-SAT (OR-Tools)", lambda: SudokuCPSAT(grid).solve()),
        ("ILP (Gurobi)", lambda: SudokuGurobi(grid).solve()),
        ("ILP (CPLEX MIP)", lambda: SudokuCplexMIP(grid).solve()),
        ("CP (CPLEX CP)", lambda: SudokuCplexCP(grid).solve()),
    ]

    print(f"{'Solver':<20} | {'Status':<12} | {'Vars':<8} | {'Constraints':<12} | {'Time (ms)':<10} | {'Valid'}")
    print("-" * 75)

    for name, run_fn in solvers:
        sol, stats = run_fn()
        valid = verify_sudoku_solution(sol, original_puzzle=grid) if sol else False
        tot_ms = stats.get("time_total_sec", 0.0) * 1000
        vars_cnt = stats.get("num_vars", 0)
        cons_cnt = stats.get("num_constraints", 0)
        status = stats.get("status", "N/A")
        print(f"{name:<20} | {status:<12} | {vars_cnt:<8} | {cons_cnt:<12} | {tot_ms:<10.2f} | {valid}")


def main():
    parser = argparse.ArgumentParser(description="Sudoku Solver Interactive Runner")
    parser.add_argument("--size", type=int, choices=[9, 16, 25], default=9, help="Sudoku size (default: 9)")
    parser.add_argument("--amo", type=str, choices=list(AMO_METHODS.keys()), default="sequential", help="SAT AMO encoding")
    parser.add_argument("--compare-amo", action="store_true", help="Compare all 5 SAT AMO encodings")
    parser.add_argument("--cross-solvers", action="store_true", help="Compare SAT, CP, and ILP solvers")
    parser.add_argument("--puzzle", type=str, default=None, help="Custom puzzle string (single-line)")
    args = parser.parse_args()

    if args.puzzle:
        puzzle_str = args.puzzle
    elif args.size == 9:
        puzzle_str = SAMPLE_PUZZLE_9x9
    else:
        box_size = {9: 3, 16: 4, 25: 5}[args.size]
        puzzle_str, _ = generate_sudoku(box_size=box_size, blank_ratio=0.55, seed=42)

    grid = parse_puzzle_string(puzzle_str)

    print(f"Sudoku Puzzle ({len(grid)}x{len(grid)}):")
    print_grid(grid)

    if args.compare_amo:
        compare_amo_methods(grid)
    elif args.cross_solvers:
        test_cross_solvers(grid)
    else:
        test_sat_solver(grid, amo=args.amo)


if __name__ == "__main__":
    main()