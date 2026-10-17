"""
cplex_cp_solver.py: Sudoku solver using IBM CPLEX CP Optimizer (docplex.cp).
"""

import os
import shutil
import time
import math

try:
    from docplex.cp.model import CpoModel
    from docplex.cp.config import context

    # Detect cpoptimizer binary path if not configured
    candidate_cp_exes = [
        r"E:\cpoptimizer\bin\x64_win64\cpoptimizer.exe",
        r"C:\Program Files\IBM\ILOG\CPLEX_Studio2211\cpoptimizer\bin\x64_win64\cpoptimizer.exe",
        r"C:\Program Files\IBM\ILOG\CPLEX_Studio2210\cpoptimizer\bin\x64_win64\cpoptimizer.exe",
    ]
    candidate_cplex_bins = [
        r"E:\cplex\bin\x64_win64",
        r"C:\Program Files\IBM\ILOG\CPLEX_Studio2211\cplex\bin\x64_win64",
        r"C:\Program Files\IBM\ILOG\CPLEX_Studio2210\cplex\bin\x64_win64",
    ]

    found_cp = False
    for cp_path in candidate_cp_exes:
        if os.path.exists(cp_path):
            context.solver.local.execfile = cp_path
            cp_dir = os.path.dirname(cp_path)
            if cp_dir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = cp_dir + ";" + os.environ.get("PATH", "")
            found_cp = True
            break

    if not found_cp and shutil.which("cpoptimizer.exe"):
        context.solver.local.execfile = shutil.which("cpoptimizer.exe")
        found_cp = True

    for cpx_dir in candidate_cplex_bins:
        if os.path.exists(cpx_dir):
            if cpx_dir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = cpx_dir + ";" + os.environ.get("PATH", "")
            break

    HAS_CPLEX_CP = True
except ImportError:
    HAS_CPLEX_CP = False


class SudokuCplexCP:
    """
    Bo giai Sudoku bang Constraint Programming (IBM CPLEX CP qua docplex.cp):
    - Bien nguyen: X[i][j] thuoc 1..N
    - Rang buoc all_diff:
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
            raise ValueError(f"Grid size N={self.N} must be a perfect square.")

    def solve(self, time_limit=60.0):
        if not HAS_CPLEX_CP:
            return None, {
                "method": "CPLEX_CP",
                "status": "NOT_INSTALLED",
                "num_vars": 0,
                "num_constraints": 0,
                "time_build_sec": 0.0,
                "time_solve_sec": 0.0,
                "time_total_sec": 0.0,
                "error_msg": "docplex.cp is not installed."
            }

        t0 = time.perf_counter()
        try:
            mdl = CpoModel(name="Sudoku_CPLEX_CP")

            # bien nguyen X[i][j] thuoc 1..N
            X = [
                [mdl.integer_var(1, self.N, name=f"x_{i}_{j}") for j in range(self.N)]
                for i in range(self.N)
            ]

            # row (alldiff)
            for i in range(self.N):
                mdl.add(mdl.all_diff(X[i]))

            # column (alldiff)
            for j in range(self.N):
                mdl.add(mdl.all_diff([X[i][j] for i in range(self.N)]))

            # box (alldiff)
            for br in range(self.b):
                for bc in range(self.b):
                    box = [
                        X[br * self.b + di][bc * self.b + dj]
                        for di in range(self.b)
                        for dj in range(self.b)
                    ]
                    mdl.add(mdl.all_diff(box))

            # clues
            clue_count = 0
            for i in range(self.N):
                for j in range(self.N):
                    val = self.grid[i][j]
                    if val > 0:
                        mdl.add(X[i][j] == val)
                        clue_count += 1

            t_build = time.perf_counter() - t0

            t1 = time.perf_counter()
            msol = mdl.solve(TimeLimit=time_limit, LogVerbosity="Quiet")
            t_solve = time.perf_counter() - t1

            solution = None
            status = "UNKNOWN"
            if msol and msol.is_solution():
                status = "OPTIMAL"
                solution = [
                    [int(msol[X[i][j]]) for j in range(self.N)]
                    for i in range(self.N)
                ]
            elif msol and msol.get_solve_status() == "JobStopped":
                status = "TIMEOUT"
            else:
                status = "NO_SOLUTION"

            metrics = {
                "method": "CPLEX_CP",
                "status": status,
                "num_vars": self.N * self.N,
                "num_constraints": 3 * self.N + clue_count,
                "time_build_sec": t_build,
                "time_solve_sec": t_solve,
                "time_total_sec": t_build + t_solve,
                "error_msg": ""
            }
            return solution, metrics

        except Exception as e:
            t_total = time.perf_counter() - t0
            err_str = str(e)
            if "cpoptimizer" in err_str.lower() or "solver sub-process start failure" in err_str.lower():
                status = "NOT_INSTALLED"
            else:
                status = "ERROR"

            return None, {
                "method": "CPLEX_CP",
                "status": status,
                "num_vars": self.N * self.N,
                "num_constraints": 3 * self.N,
                "time_build_sec": t_total,
                "time_solve_sec": 0.0,
                "time_total_sec": t_total,
                "error_msg": err_str
            }
