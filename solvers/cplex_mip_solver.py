"""
cplex_mip_solver.py: Sudoku solver using 0-1 ILP (IBM CPLEX MIP via docplex.mp).
"""

import time
import math

try:
    import docplex.mp.model as cpx_mp
    from docplex.mp.utils import DOcplexLimitsExceeded
    HAS_CPLEX_MP = True
except ImportError:
    HAS_CPLEX_MP = False


class SudokuCplexMIP:
    """
    Bo giai Sudoku bang ILP (IBM CPLEX MIP):
    - Bien nhi phan: x[i, j, k] thuoc {0, 1}
    - Rang buoc tuyen tinh:
      1. cell: sum x[i, j, k] == 1
      2. row: sum x[i, j, k] == 1
      3. column: sum x[i, j, k] == 1
      4. box k x k: sum x[i, j, k] == 1
    - clues -> x[i, j, val] == 1
    """

    def __init__(self, grid):
        self.grid = grid
        self.N = len(grid)
        self.b = math.isqrt(self.N)
        if self.b * self.b != self.N:
            raise ValueError(f"Grid size N={self.N} must be a perfect square.")

    def solve(self, time_limit=60.0):
        if not HAS_CPLEX_MP:
            return None, {
                "method": "CPLEX_MIP",
                "status": "NOT_INSTALLED",
                "num_vars": 0,
                "num_constraints": 0,
                "time_build_sec": 0.0,
                "time_solve_sec": 0.0,
                "time_total_sec": 0.0,
                "error_msg": "docplex.mp is not installed."
            }

        t0 = time.perf_counter()
        try:
            mdl = cpx_mp.Model(name="Sudoku_CPLEX_MIP")
            mdl.set_time_limit(time_limit)

            # bien binary x[i, j, k] thuoc {0, 1}
            x = {}
            for i in range(self.N):
                for j in range(self.N):
                    for k in range(1, self.N + 1):
                        x[i, j, k] = mdl.binary_var(name=f"x_{i}_{j}_{k}")

            # cell (alo + amo)
            for i in range(self.N):
                for j in range(self.N):
                    mdl.add_constraint(
                        mdl.sum(x[i, j, k] for k in range(1, self.N + 1)) == 1,
                        ctname=f"cell_{i}_{j}"
                    )

            # row (alo + amo)
            for i in range(self.N):
                for k in range(1, self.N + 1):
                    mdl.add_constraint(
                        mdl.sum(x[i, j, k] for j in range(self.N)) == 1,
                        ctname=f"row_{i}_{k}"
                    )

            # column (alo + amo)
            for j in range(self.N):
                for k in range(1, self.N + 1):
                    mdl.add_constraint(
                        mdl.sum(x[i, j, k] for i in range(self.N)) == 1,
                        ctname=f"col_{j}_{k}"
                    )

            # box (alo + amo)
            for br in range(self.b):
                for bc in range(self.b):
                    for k in range(1, self.N + 1):
                        mdl.add_constraint(
                            mdl.sum(
                                x[br * self.b + di, bc * self.b + dj, k]
                                for di in range(self.b)
                                for dj in range(self.b)
                            ) == 1,
                            ctname=f"box_{br}_{bc}_{k}"
                        )

            # clues
            for i in range(self.N):
                for j in range(self.N):
                    val = self.grid[i][j]
                    if val > 0:
                        mdl.add_constraint(x[i, j, val] == 1, ctname=f"given_{i}_{j}")

            t_build = time.perf_counter() - t0
            num_vars = mdl.number_of_variables
            num_constrs = mdl.number_of_constraints

            t1 = time.perf_counter()
            msol = mdl.solve(log_output=False)
            t_solve = time.perf_counter() - t1

            solution = None
            if msol is not None:
                status = "OPTIMAL"
                solution = [[0] * self.N for row in range(self.N)]
                for i in range(self.N):
                    for j in range(self.N):
                        for k in range(1, self.N + 1):
                            if msol[x[i, j, k]] > 0.5:
                                solution[i][j] = k
                                break
            else:
                solve_details = mdl.get_solve_details()
                status_str = str(solve_details.status).upper() if solve_details else ""
                if "TIME" in status_str:
                    status = "TIMEOUT"
                else:
                    status = "NO_SOLUTION"

            metrics = {
                "method": "CPLEX_MIP",
                "status": status,
                "num_vars": num_vars,
                "num_constraints": num_constrs,
                "time_build_sec": t_build,
                "time_solve_sec": t_solve,
                "time_total_sec": t_build + t_solve,
                "error_msg": ""
            }
            return solution, metrics

        except DOcplexLimitsExceeded as e:
            t_total = time.perf_counter() - t0
            return None, {
                "method": "CPLEX_MIP",
                "status": "LICENSE_LIMIT",
                "num_vars": self.N ** 3,
                "num_constraints": 4 * (self.N ** 2),
                "time_build_sec": t_total,
                "time_solve_sec": 0.0,
                "time_total_sec": t_total,
                "error_msg": str(e)
            }
        except Exception as e:
            t_total = time.perf_counter() - t0
            return None, {
                "method": "CPLEX_MIP",
                "status": "ERROR",
                "num_vars": self.N ** 3,
                "num_constraints": 4 * (self.N ** 2),
                "time_build_sec": t_total,
                "time_solve_sec": 0.0,
                "time_total_sec": t_total,
                "error_msg": str(e)
            }
