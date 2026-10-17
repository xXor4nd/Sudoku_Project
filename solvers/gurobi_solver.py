"""
gurobi_solver.py: Sudoku solver using 0-1 ILP (Gurobi Optimizer).
"""

import os
import time
import math

if "GRB_LICENSE_FILE" not in os.environ:
    user_lic = os.path.expanduser("~/gurobi.lic")
    for candidate_lic in [
        user_lic,
        os.path.join(user_lic, "gurobi.lic"),
        r"C:\gurobi\gurobi.lic",
    ]:
        if os.path.isfile(candidate_lic):
            os.environ["GRB_LICENSE_FILE"] = candidate_lic
            break

try:
    import gurobipy as gp
    from gurobipy import GRB
    HAS_GUROBI = True
except ImportError:
    HAS_GUROBI = False


class SudokuGurobi:
    """
    Bo giai Sudoku bang ILP (Gurobi Optimizer):
    - Bien nhi phan: x[i, j, k] in {0, 1}
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
        if not HAS_GUROBI:
            return None, {
                "method": "Gurobi_ILP",
                "status": "NOT_INSTALLED",
                "num_vars": 0,
                "num_constraints": 0,
                "time_build_sec": 0.0,
                "time_solve_sec": 0.0,
                "time_total_sec": 0.0,
                "error_msg": "gurobipy is not installed."
            }

        t0 = time.perf_counter()
        try:
            model = gp.Model("Sudoku_Gurobi_ILP")
            model.Params.OutputFlag = 0
            model.Params.TimeLimit = time_limit

            # bien binary x[i, j, k] in {0, 1}
            x = {}
            for i in range(self.N):
                for j in range(self.N):
                    for k in range(1, self.N + 1):
                        x[i, j, k] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}_{k}")

            # cell (alo + amo)
            for i in range(self.N):
                for j in range(self.N):
                    model.addConstr(
                        gp.quicksum(x[i, j, k] for k in range(1, self.N + 1)) == 1,
                        name=f"cell_{i}_{j}"
                    )

            # row (alo + amo)
            for i in range(self.N):
                for k in range(1, self.N + 1):
                    model.addConstr(
                        gp.quicksum(x[i, j, k] for j in range(self.N)) == 1,
                        name=f"row_{i}_{k}"
                    )

            # column (alo + amo)
            for j in range(self.N):
                for k in range(1, self.N + 1):
                    model.addConstr(
                        gp.quicksum(x[i, j, k] for i in range(self.N)) == 1,
                        name=f"col_{j}_{k}"
                    )

            # box (alo + amo)
            for br in range(self.b):
                for bc in range(self.b):
                    for k in range(1, self.N + 1):
                        model.addConstr(
                            gp.quicksum(
                                x[br * self.b + di, bc * self.b + dj, k]
                                for di in range(self.b)
                                for dj in range(self.b)
                            ) == 1,
                            name=f"box_{br}_{bc}_{k}"
                        )

            # clues
            for i in range(self.N):
                for j in range(self.N):
                    val = self.grid[i][j]
                    if val > 0:
                        model.addConstr(x[i, j, val] == 1, name=f"given_{i}_{j}")

            model.update()
            t_build = time.perf_counter() - t0

            num_vars = model.NumVars
            num_constrs = model.NumConstrs

            t1 = time.perf_counter()
            model.optimize()
            t_solve = time.perf_counter() - t1

            solution = None
            if model.Status == GRB.OPTIMAL:
                status = "OPTIMAL"
                solution = [[0] * self.N for row in range(self.N)]
                for i in range(self.N):
                    for j in range(self.N):
                        for k in range(1, self.N + 1):
                            if x[i, j, k].X > 0.5:
                                solution[i][j] = k
                                break
            elif model.Status == GRB.TIME_LIMIT:
                status = "TIMEOUT"
            elif model.Status == GRB.INFEASIBLE:
                status = "INFEASIBLE"
            else:
                status = f"GUROBI_STATUS_{model.Status}"

            metrics = {
                "method": "Gurobi_ILP",
                "status": status,
                "num_vars": num_vars,
                "num_constraints": num_constrs,
                "time_build_sec": t_build,
                "time_solve_sec": t_solve,
                "time_total_sec": t_build + t_solve,
                "error_msg": ""
            }
            return solution, metrics

        except gp.GurobiError as e:
            t_total = time.perf_counter() - t0
            status = "LICENSE_LIMIT" if "size-limited license" in str(e).lower() else "ERROR"
            return None, {
                "method": "Gurobi_ILP",
                "status": status,
                "num_vars": self.N ** 3,
                "num_constraints": 4 * (self.N ** 2),
                "time_build_sec": t_total,
                "time_solve_sec": 0.0,
                "time_total_sec": t_total,
                "error_msg": str(e)
            }
