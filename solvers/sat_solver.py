"""
sat_solver.py: Sudoku solver using CNF SAT encoding and PySAT.
Supports 5 AMO encodings: pairwise, binary, sequential, commander, product.
"""

import os
import sys
import math
import time
import threading

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.sat_context import SatContext, get_var_id
from encoders import AMO_METHODS
from pysat.solvers import Solver


class SudokuSAT:
    """
    Bo giai Sudoku dua tren SAT encoding:
    - Bieu dien moi o (r, c) nhan gia tri val bang mot literal Boolean x_{r, c, val}
    - Ma hoa cac rang buoc ALO va AMO:
      1. cell
      2. row
      3. column
      4. box k x k
    - clues -> unit clauses
    """

    def __init__(self, grid, amo_name="sequential"):
        self.grid = grid
        self.N = len(grid)
        self.b = math.isqrt(self.N)
        if self.b * self.b != self.N:
            raise ValueError(f"Grid size N={self.N} must be a perfect square.")

        if amo_name not in AMO_METHODS:
            raise ValueError(
                f"Invalid AMO method '{amo_name}'. Choose from: {list(AMO_METHODS.keys())}"
            )

        self.ctx = SatContext(self.N)
        self.amo_func = AMO_METHODS[amo_name]
        self.amo_name = amo_name

    def gen_clauses(self):
        N = self.N
        b = self.b

        # cell (alo + amo)
        for i in range(N):
            for j in range(N):
                lits = [get_var_id(N, i, j, k) for k in range(1, N + 1)]
                self.ctx.add_clause(lits)
                self.ctx.add_clauses(self.amo_func(self.ctx, lits))

        # row (alo + amo)
        for i in range(N):
            for k in range(1, N + 1):
                lits = [get_var_id(N, i, j, k) for j in range(N)]
                self.ctx.add_clause(lits)
                self.ctx.add_clauses(self.amo_func(self.ctx, lits))

        # column (alo + amo)
        for j in range(N):
            for k in range(1, N + 1):
                lits = [get_var_id(N, i, j, k) for i in range(N)]
                self.ctx.add_clause(lits)
                self.ctx.add_clauses(self.amo_func(self.ctx, lits))

        # box (alo + amo)
        for br in range(b):
            for bc in range(b):
                for k in range(1, N + 1):
                    lits = []
                    for di in range(b):
                        for dj in range(b):
                            lits.append(get_var_id(N, br * b + di, bc * b + dj, k))
                    self.ctx.add_clause(lits)
                    self.ctx.add_clauses(self.amo_func(self.ctx, lits))

        # clues
        for i in range(N):
            for j in range(N):
                val = self.grid[i][j]
                if val > 0:
                    self.ctx.add_clause([get_var_id(N, i, j, val)])

    def solve(self, solver_name="glucose4", time_limit=60.0):
        t0 = time.perf_counter()
        self.gen_clauses()
        t_encode = time.perf_counter() - t0

        t1 = time.perf_counter()
        solution = None
        status = "UNKNOWN"

        with Solver(name=solver_name, bootstrap_with=self.ctx.clauses) as solver:
            timer = threading.Timer(time_limit, solver.interrupt)
            timer.start()
            try:
                res = solver.solve_limited(expect_interrupt=True)
            except Exception:
                res = solver.solve()
            finally:
                timer.cancel()
                try:
                    solver.clear_interrupt()
                except Exception:
                    pass

            if res is True:
                status = "SAT"
                model = set(solver.get_model())
                solution = [[0] * self.N for r in range(self.N)]
                for i in range(self.N):
                    for j in range(self.N):
                        for k in range(1, self.N + 1):
                            if get_var_id(self.N, i, j, k) in model:
                                solution[i][j] = k
                                break
            elif res is False:
                status = "UNSAT"
            else:
                status = "TIMEOUT"

        t_solve = time.perf_counter() - t1

        metrics = {
            "method": "SAT",
            "N": self.N,
            "amo_method": self.amo_name,
            "solver": solver_name,
            "status": status,
            "num_base_vars": self.N**3,
            "num_total_vars": self.ctx.next_var - 1,
            "num_vars": self.ctx.next_var - 1,
            "num_clauses": len(self.ctx.clauses),
            "num_constraints": len(self.ctx.clauses),
            "time_encode_sec": t_encode,
            "time_build_sec": t_encode,
            "time_solve_sec": t_solve,
            "time_total_sec": t_encode + t_solve,
        }
        return solution, metrics