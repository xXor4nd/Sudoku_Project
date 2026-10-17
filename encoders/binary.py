"""
Binary (Logarithmic) encoding for At-Most-One (AMO).
Uses ceil(log2 N) auxiliary variables and O(N log N) clauses.
"""

import math


def encode_binary(ctx, lits):
    clauses = []
    n = len(lits)
    if n <= 1:
        return clauses

    m = math.ceil(math.log2(n))
    bits = [ctx.new_var() for _ in range(m)]

    for idx, lit in enumerate(lits):
        for bit_pos in range(m):
            bit_val = (idx >> bit_pos) & 1
            if bit_val == 1:
                clauses.append([-lit, bits[bit_pos]])
            else:
                clauses.append([-lit, -bits[bit_pos]])

    return clauses