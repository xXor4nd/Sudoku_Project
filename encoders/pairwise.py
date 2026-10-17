"""
Pairwise (Binomial) encoding for At-Most-One (AMO).
Generates O(N^2) clauses without auxiliary variables.
"""


def encode_pairwise(ctx, lits):
    clauses = []
    n = len(lits)
    for a in range(n):
        for b in range(a + 1, n):
            clauses.append([-lits[a], -lits[b]])
    return clauses