"""
benchmark_runner.py: Automated benchmark runner for generalized Sudoku.
Supports:
1. Ablation study of 5 SAT AMO encodings (Pairwise, Binary, Sequential, Commander, Product).
2. Cross-paradigm comparison (PySAT Glucose4, Google OR-Tools CP-SAT, Gurobi ILP, CPLEX MIP, CPLEX CP).
3. Board sizes: 9x9, 16x16, 25x25, 36x36, 49x49.
4. Tiered timeouts and adaptive early stopping.
"""

import os
import sys
import time
import argparse
import csv
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from encoders import AMO_METHODS
from solvers import (
    SudokuSAT,
    SudokuGurobi,
    SudokuCplexMIP,
    SudokuCPSAT,
    SudokuCplexCP,
)
from utils import (
    parse_puzzle_string,
    verify_sudoku_solution,
    generate_sudoku,
    load_benchmark_dataset,
)

CSV_HEADERS = [
    "timestamp",
    "matrix_size",
    "box_size",
    "puzzle_id",
    "blank_ratio",
    "paradigm",
    "solver_name",
    "amo_encoding",
    "status",
    "is_valid",
    "num_vars",
    "num_constraints",
    "time_build_sec",
    "time_solve_sec",
    "time_total_sec",
    "error_msg",
]


def append_csv_row(csv_path, row_dict):
    """Append a benchmark result row to CSV immediately."""
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row_dict)


def run_single_sat(grid, amo_name, solver_name="glucose4", time_limit=60.0):
    try:
        model = SudokuSAT(grid, amo_name=amo_name)
        sol, met = model.solve(solver_name=solver_name, time_limit=time_limit)
        is_valid = verify_sudoku_solution(sol, original_puzzle=grid) if sol else False
        status = "OPTIMAL" if met["status"] == "SAT" else met["status"]
        return {
            "paradigm": "SAT",
            "solver_name": solver_name,
            "amo_encoding": amo_name,
            "status": status,
            "is_valid": is_valid,
            "num_vars": met["num_total_vars"],
            "num_constraints": met["num_clauses"],
            "time_build_sec": met["time_encode_sec"],
            "time_solve_sec": met["time_solve_sec"],
            "time_total_sec": met["time_total_sec"],
            "error_msg": "",
        }
    except Exception as e:
        err_str = str(e)
        status = "TIMEOUT" if "timeout" in err_str.lower() else "ERROR"
        return {
            "paradigm": "SAT",
            "solver_name": solver_name,
            "amo_encoding": amo_name,
            "status": status,
            "is_valid": False,
            "num_vars": 0,
            "num_constraints": 0,
            "time_build_sec": 0.0,
            "time_solve_sec": 0.0,
            "time_total_sec": 0.0,
            "error_msg": err_str,
        }


def run_single_cpsat(grid, time_limit=60.0):
    solver = SudokuCPSAT(grid)
    sol, met = solver.solve(time_limit=time_limit)
    is_valid = verify_sudoku_solution(sol, original_puzzle=grid) if sol else False
    return {
        "paradigm": "CP",
        "solver_name": "OR-Tools_CP-SAT",
        "amo_encoding": "AllDifferent (CP)",
        "status": met["status"],
        "is_valid": is_valid,
        "num_vars": met["num_vars"],
        "num_constraints": met["num_constraints"],
        "time_build_sec": met["time_build_sec"],
        "time_solve_sec": met["time_solve_sec"],
        "time_total_sec": met["time_total_sec"],
        "error_msg": met.get("error_msg", ""),
    }


def run_single_gurobi(grid, time_limit=60.0):
    solver = SudokuGurobi(grid)
    sol, met = solver.solve(time_limit=time_limit)
    is_valid = verify_sudoku_solution(sol, original_puzzle=grid) if sol else False
    return {
        "paradigm": "ILP",
        "solver_name": "Gurobi_Optimizer",
        "amo_encoding": "Linear_Sum (ILP)",
        "status": met["status"],
        "is_valid": is_valid,
        "num_vars": met["num_vars"],
        "num_constraints": met["num_constraints"],
        "time_build_sec": met["time_build_sec"],
        "time_solve_sec": met["time_solve_sec"],
        "time_total_sec": met["time_total_sec"],
        "error_msg": met.get("error_msg", ""),
    }


def run_single_cplex_mip(grid, time_limit=60.0):
    solver = SudokuCplexMIP(grid)
    sol, met = solver.solve(time_limit=time_limit)
    is_valid = verify_sudoku_solution(sol, original_puzzle=grid) if sol else False
    return {
        "paradigm": "ILP",
        "solver_name": "CPLEX_MIP",
        "amo_encoding": "Linear_Sum (ILP)",
        "status": met["status"],
        "is_valid": is_valid,
        "num_vars": met["num_vars"],
        "num_constraints": met["num_constraints"],
        "time_build_sec": met["time_build_sec"],
        "time_solve_sec": met["time_solve_sec"],
        "time_total_sec": met["time_total_sec"],
        "error_msg": met.get("error_msg", ""),
    }


def run_single_cplex_cp(grid, time_limit=60.0):
    solver = SudokuCplexCP(grid)
    sol, met = solver.solve(time_limit=time_limit)
    is_valid = verify_sudoku_solution(sol, original_puzzle=grid) if sol else False
    return {
        "paradigm": "CP",
        "solver_name": "CPLEX_CP",
        "amo_encoding": "AllDiff (CP)",
        "status": met["status"],
        "is_valid": is_valid,
        "num_vars": met["num_vars"],
        "num_constraints": met["num_constraints"],
        "time_build_sec": met["time_build_sec"],
        "time_solve_sec": met["time_solve_sec"],
        "time_total_sec": met["time_total_sec"],
        "error_msg": met.get("error_msg", ""),
    }


DEFAULT_SIZE_TIMEOUTS = {
    9: 3.0,
    16: 8.0,
    25: 20.0,
    36: 35.0,
    49: 50.0,
}

DEFAULT_PUZZLE_COUNTS = {
    9: 5000,
    16: 100,
    25: 40,
    36: 20,
    49: 10,
}


def run_benchmark(args):
    print(f"Benchmark: mode={args.mode}, source={args.source}, sizes={args.sizes}")
    print(f"Output CSV: {args.csv_output}")

    os.makedirs(os.path.dirname(os.path.abspath(args.csv_output)), exist_ok=True)

    size_to_box = {9: 3, 16: 4, 25: 5, 36: 6, 49: 7}
    total_runs = 0

    # Theo dõi trạng thái giải thành công ở kích thước trước của từng solver
    solver_prev_success = {}

    for N in args.sizes:
        if N not in size_to_box:
            print(f"Size {N}x{N} not supported, skipping.")
            continue

        box_size = size_to_box[N]
        current_timeout = DEFAULT_SIZE_TIMEOUTS.get(N, args.time_limit)

        if args.full_dataset:
            target_count = args.puzzles_9x9 if (N == 9 and args.puzzles_9x9) else DEFAULT_PUZZLE_COUNTS.get(N, args.puzzles_per_size)
        else:
            target_count = args.puzzles_per_size

        puzzles_to_test = []

        if args.source == "dataset":
            try:
                raw_puzzles = load_benchmark_dataset(
                    size=N,
                    count=target_count,
                    data_dir=args.data_dir,
                    seed=args.base_seed,
                )
            except Exception as e:
                print(f"Failed to load dataset for {N}x{N}: {e}")
                continue

            for idx, p_str in enumerate(raw_puzzles, 1):
                pid = f"Dataset_{N}x{N}_p{idx:03d}" if N != 9 else f"Dataset_9x9_17clue_p{idx:03d}"
                try:
                    grid = parse_puzzle_string(p_str)
                    blank_count = sum(row.count(0) for row in grid)
                    b_ratio = round(blank_count / (N * N), 4)
                    puzzles_to_test.append((pid, b_ratio, grid))
                except Exception as e:
                    print(f"Parse error for {pid}: {e}")
        else:
            for p_idx in range(1, target_count + 1):
                seed = args.base_seed + (N * 100) + p_idx
                for blank_ratio in args.blank_ratios:
                    pid = f"Sudoku_{N}x{N}_seed{seed}_blank{int(blank_ratio*100)}"
                    try:
                        p_text, _ = generate_sudoku(box_size=box_size, blank_ratio=blank_ratio, seed=seed)
                        grid = parse_puzzle_string(p_text)
                        blank_count = sum(row.count(0) for row in grid)
                        b_ratio = round(blank_count / (N * N), 4)
                        puzzles_to_test.append((pid, b_ratio, grid))
                    except Exception as e:
                        print(f"Generation error: {e}")
                        continue

        if not puzzles_to_test:
            continue

        print(f"\n--- Testing size: {N}x{N} ({len(puzzles_to_test)} puzzles, timeout={current_timeout}s) ---")

        configs_to_run = []
        if args.mode in ("sat_ablation", "all"):
            for amo in list(AMO_METHODS.keys()):
                for sat_engine in args.sat_solvers:
                    configs_to_run.append((
                        f"SAT_{amo}_{sat_engine}",
                        "SAT",
                        sat_engine,
                        amo,
                        lambda g, a=amo, s=sat_engine, t=current_timeout: run_single_sat(g, a, s, t),
                    ))

        if args.mode in ("cross_solver", "all"):
            if args.mode == "cross_solver":
                configs_to_run.append((
                    "SAT_sequential_glucose4",
                    "SAT",
                    "glucose4",
                    "sequential",
                    lambda g, t=current_timeout: run_single_sat(g, "sequential", "glucose4", t),
                ))
            configs_to_run.append((
                "OR-Tools_CP-SAT",
                "CP",
                "OR-Tools_CP-SAT",
                "AllDifferent (CP)",
                lambda g, t=current_timeout: run_single_cpsat(g, t),
            ))
            configs_to_run.append((
                "Gurobi_ILP",
                "ILP",
                "Gurobi_Optimizer",
                "Linear_Sum (ILP)",
                lambda g, t=current_timeout: run_single_gurobi(g, t),
            ))
            configs_to_run.append((
                "CPLEX_MIP",
                "ILP",
                "CPLEX_MIP",
                "Linear_Sum (ILP)",
                lambda g, t=current_timeout: run_single_cplex_mip(g, t),
            ))
            configs_to_run.append((
                "CPLEX_CP",
                "CP",
                "CPLEX_CP",
                "AllDiff (CP)",
                lambda g, t=current_timeout: run_single_cplex_cp(g, t),
            ))

        # Filter out solvers that timed out 100% in previous grid size
        active_configs = []
        for cfg in configs_to_run:
            tag = cfg[0]
            if not solver_prev_success.get(tag, True):
                print(f"Skipping {tag} (timed out 100% in previous size)")
            else:
                active_configs.append(cfg)
        configs_to_run = active_configs

        if not configs_to_run:
            print(f"All solvers timed out previously. Early stopping at {N}x{N}.")
            break

        # Thống kê kết quả cho kích thước N này
        solved_count_this_size = 0
        solver_solved_in_this_size = {tag: 0 for tag, _, _, _, _ in configs_to_run}
        is_large_batch = len(puzzles_to_test) > 100
        batch_start_time = time.perf_counter()

        for puzzle_idx, (puzzle_id, blank_ratio, grid) in enumerate(puzzles_to_test, 1):
            if is_large_batch and (puzzle_idx == 1 or puzzle_idx % 100 == 0 or puzzle_idx == len(puzzles_to_test)):
                elapsed_batch = time.perf_counter() - batch_start_time
                pct = (puzzle_idx / len(puzzles_to_test)) * 100
                print(f"  [{N}x{N}] {puzzle_idx}/{len(puzzles_to_test)} ({pct:.1f}%) in {elapsed_batch:.1f}s")

            for tag, paradigm, s_name, amo_enc, run_fn in configs_to_run:
                res = run_fn(grid)

                if res["time_total_sec"] >= current_timeout or res["status"] in ("TIMEOUT", "LICENSE_LIMIT", "ERROR"):
                    if res["status"] != "LICENSE_LIMIT":
                        res["status"] = "TIMEOUT"
                    res["is_valid"] = False
                    res["time_total_sec"] = min(res["time_total_sec"], current_timeout) if res["time_total_sec"] > 0 else current_timeout

                if res["is_valid"]:
                    solved_count_this_size += 1
                    solver_solved_in_this_size[tag] += 1

                row = {
                    "timestamp": datetime.now().isoformat(),
                    "matrix_size": N,
                    "box_size": box_size,
                    "puzzle_id": puzzle_id,
                    "blank_ratio": blank_ratio,
                    "paradigm": res["paradigm"],
                    "solver_name": res["solver_name"],
                    "amo_encoding": res["amo_encoding"],
                    "status": res["status"],
                    "is_valid": res["is_valid"],
                    "num_vars": res["num_vars"],
                    "num_constraints": res["num_constraints"],
                    "time_build_sec": round(res["time_build_sec"], 5),
                    "time_solve_sec": round(res["time_solve_sec"], 5),
                    "time_total_sec": round(res["time_total_sec"], 5),
                    "error_msg": res["error_msg"],
                }
                append_csv_row(args.csv_output, row)
                total_runs += 1

                if not is_large_batch:
                    v_str = "OK" if res["is_valid"] else res["status"]
                    print(f"  {tag:<28} -> [{v_str:<8}] Vars: {res['num_vars']:<6} Cons: {res['num_constraints']:<8} Time: {res['time_total_sec']*1000:.1f} ms")

        for tag, _, _, _, _ in configs_to_run:
            solver_prev_success[tag] = (solver_solved_in_this_size[tag] > 0)

        print(f"Summary for {N}x{N}:")
        for tag, _, _, _, _ in configs_to_run:
            solved = solver_solved_in_this_size[tag]
            total_p = len(puzzles_to_test)
            print(f"  {tag:<28}: {solved}/{total_p} solved ({solved/total_p*100:.1f}%)")

        # early stopping
        if solved_count_this_size == 0:
            print("No solver succeeded at this size. Early stopping.")
            break

    print(f"\nBenchmark finished. Total runs: {total_runs}")

    if args.plot:
        plot_benchmark_charts(args.csv_output, time_limit=args.time_limit)

    try:
        from scripts.generate_report_tables import generate_tables
        generate_tables(args.csv_output)
    except Exception as e:
        print(f"Warning: could not generate LaTeX tables: {e}")


def plot_benchmark_charts(csv_path, time_limit=60.0):
    from utils import generate_all_scientific_plots
    plots_dir = os.path.join(PROJECT_ROOT, "plots")
    generate_all_scientific_plots(csv_path=csv_path, output_dir=plots_dir, time_limit=time_limit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sudoku Solver Benchmark Suite")
    parser.add_argument("--source", choices=["dataset", "generated"], default="dataset")
    parser.add_argument("--data_dir", type=str, default=os.path.join(PROJECT_ROOT, "data"))
    parser.add_argument("--mode", choices=["sat_ablation", "cross_solver", "all"], default="all")
    parser.add_argument("--sizes", nargs="+", type=int, default=[9, 16, 25, 36, 49])
    parser.add_argument("--puzzles_per_size", type=int, default=5)
    parser.add_argument("--puzzles_9x9", type=int, default=5000)
    parser.add_argument("--full_dataset", action="store_true", default=False)
    parser.add_argument("--blank_ratios", nargs="+", type=float, default=[0.50, 0.65])
    parser.add_argument("--time_limit", type=float, default=60.0)
    parser.add_argument("--sat_solvers", nargs="+", default=["glucose4"])
    parser.add_argument("--base_seed", type=int, default=2026)
    parser.add_argument("--csv_output", type=str, default=os.path.join(PROJECT_ROOT, "benchmark_results.csv"))
    parser.add_argument("--plot", action=argparse.BooleanOptionalAction, default=True)

    args = parser.parse_args()
    run_benchmark(args)
