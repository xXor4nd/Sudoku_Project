"""
Product encoding for At-Most-One (AMO).
Maps literals onto a 2D grid with 2*ceil(sqrt(N)) auxiliary variables.
"""

import math
from .pairwise import encode_pairwise


def encode_product(ctx, lits):
    clauses = []
    n = len(lits)
    if n <= 6:
        return encode_pairwise(ctx, lits)

    p = math.ceil(math.sqrt(n))
    q = math.ceil(n / p)

    rows = [ctx.new_var() for _ in range(p)]
    cols = [ctx.new_var() for _ in range(q)]

    clauses.extend(encode_pairwise(ctx, rows))
    clauses.extend(encode_pairwise(ctx, cols))

    for idx, lit in enumerate(lits):
        u = idx // q
        v = idx % q
        clauses.append([-lit, rows[u]])
        clauses.append([-lit, cols[v]])

    return clauses