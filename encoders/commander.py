"""
Commander encoding for At-Most-One (AMO).
Partitions literals into groups and assigns commander variables.
"""

from .pairwise import encode_pairwise


def encode_commander(ctx, lits, group_size=3):
    n = len(lits)
    if n <= group_size:
        return encode_pairwise(ctx, lits)

    clauses = []
    groups = []
    commanders = []

    # Partition literals into groups of size group_size
    for start in range(0, n, group_size):
        group = lits[start : start + group_size]
        groups.append(group)
        commanders.append(ctx.new_var())

    for i, group in enumerate(groups):
        c_i = commanders[i]

        # c_i -> (x_1 V ... V x_k)
        clauses.append([-c_i] + group)

        # amo in group
        clauses.extend(encode_pairwise(ctx, group))

        # -c_i -> -x
        for x in group:
            clauses.append([c_i, -x])

    # amo commanders
    clauses.extend(encode_pairwise(ctx, commanders))

    return clauses