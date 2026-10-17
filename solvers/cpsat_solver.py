"""
cpsat_solver.py: Sudoku solver using Google OR-Tools CP-SAT.
"""

import time
import math

try:
    from ortools.sat.python import cp_model
    HAS_ORT_CPSAT = True
except ImportError:
    HAS_ORT_CPSAT = False


class SudokuCPSAT:
    """
    Bo giai Sudoku bang Google OR-Tools CP-SAT:
    - Bien nguyen: X[i][j] thuoc {1..N}
    - Rang buoc alldiff:
      1. row
      2. column
      3. box k x k
    - clues -> X[i][j] == val
    """

    def __init__(self, grid):
        self.grid = grid
        self.N = len(grid)
        self.b = math.isqrt(self.N)
        if self.b * self.b != self.N:
            raise ValueError(f"Kích thước N={self.N} phải là số chính phương.")

    def solve(self, time_limit=60.0, num_workers=1):
        if not HAS_ORT_CPSAT:
            return None, {
                "method": "ORTools_CPSAT",
                "status": "NOT_INSTALLED",
                "num_vars": 0,
                "num_constraints": 0,
                "time_build_sec": 0.0,
                "time_solve_sec": 0.0,
                "time_total_sec": 0.0,
                "error_msg": "ortools is not installed."
            }

        t0 = time.perf_counter()
        model = cp_model.CpModel()

        # bien nguyen X[i][j] thuoc 1..N
        X = [
            [model.NewIntVar(1, self.N, f"x_{i}_{j}") for j in range(self.N)]
            for i in range(self.N)
        ]

        # row (alldifferent)
        for i in range(self.N):
            model.AddAllDifferent(X[i])

        # column (alldifferent)
        for j in range(self.N):
            model.AddAllDifferent([X[i][j] for i in range(self.N)])

        # box (alldifferent)
        for br in range(self.b):
            for bc in range(self.b):
                box = [
                    X[br * self.b + di][bc * self.b + dj]
                    for di in range(self.b)
                    for dj in range(self.b)
                ]
                model.AddAllDifferent(box)

        # clues
        clue_count = 0
        for i in range(self.N):
            for j in range(self.N):
                val = self.grid[i][j]
                if val > 0:
                    model.Add(X[i][j] == val)
                    clue_count += 1

        t_build = time.perf_counter() - t0

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit
        solver.parameters.log_search_progress = False
        if num_workers > 0:
            solver.parameters.num_workers = num_workers

        t1 = time.perf_counter()
        status_code = solver.Solve(model)
        t_solve = time.perf_counter() - t1

        solution = None
        if status_code in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            status = "OPTIMAL"
            solution = [
                [solver.Value(X[i][j]) for j in range(self.N)]
                for i in range(self.N)
            ]
        elif status_code == cp_model.INFEASIBLE:
            status = "INFEASIBLE"
        elif status_code == cp_model.UNKNOWN:
            status = "TIMEOUT"
        else:
            status = f"CPSAT_STATUS_{status_code}"

        metrics = {
            "method": "ORTools_CPSAT",
            "status": status,
            "num_vars": self.N * self.N,
            "num_constraints": 3 * self.N + clue_count,
            "time_build_sec": t_build,
            "time_solve_sec": t_solve,
            "time_total_sec": t_build + t_solve,
            "error_msg": ""
        }
        return solution, metrics
