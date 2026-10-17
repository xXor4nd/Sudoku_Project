"""
sat_context.py: Context and variable management for SAT CNF encodings.
"""


def get_var_id(N, i, j, k):
    return i * (N * N) + j * N + k


class SatContext:
    def __init__(self, N):
        self.N = N
        self.next_var = N**3 + 1
        self.clauses = []

    def new_var(self):
        var = self.next_var
        self.next_var += 1
        return var

    def add_clause(self, clause):
        self.clauses.append(clause)

    def add_clauses(self, clauses):
        self.clauses.extend(clauses)
