"""
Sequential Counter encoding for At-Most-One (AMO).
Uses N - 1 auxiliary variables and 3N - 4 clauses.
"""


def encode_sequential(ctx, lits):
    clauses = []
    n = len(lits)
    if n <= 1:
        return clauses

    # Prefix sum vars: s[t] = 1 if any of lits[0..t] is 1
    s = [ctx.new_var() for _ in range(n - 1)]

    # t = 0
    clauses.append([-lits[0], s[0]])

    # 1 <= t < n - 1
    for t in range(1, n - 1):
        clauses.append([-lits[t], s[t]])
        clauses.append([-s[t - 1], s[t]])
        clauses.append([-s[t - 1], -lits[t]])

    # t = n - 1
    clauses.append([-s[n - 2], -lits[n - 1]])
    
    return clauses