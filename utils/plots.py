"""
plots.py: Visualizes benchmark results:
- Figure 4.1: Clauses comparison across SAT AMO encodings.
- Figure 4.2: Variables comparison across SAT AMO encodings.
- Figure 4.3: Runtime comparison across SAT AMO encodings.
- Figure 4.4: Runtime comparison across paradigms (SAT vs CP vs ILP).
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt


def setup_plot_style():
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.titlesize": 14,
        "lines.linewidth": 2.2,
        "lines.markersize": 7,
        "grid.linestyle": "--",
        "grid.alpha": 0.6,
    })


def generate_all_scientific_plots(csv_path="benchmark_results.csv", output_dir="plots", time_limit=30.0):
    """Generate all figures from benchmark CSV data."""
    if not os.path.isfile(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    df = pd.read_csv(csv_path)
    if df.empty:
        print("Error: CSV file is empty.")
        return

    os.makedirs(output_dir, exist_ok=True)
    setup_plot_style()

    sat_df = df[df["paradigm"] == "SAT"].copy()
    sizes = sorted(sat_df["matrix_size"].unique())
    size_labels = [f"{n}x{n}" for n in sizes]

    amo_methods = ["pairwise", "binary", "sequential", "commander", "product"]
    amo_names = {
        "pairwise": "Binomial (Pairwise)",
        "binary": "Binary",
        "sequential": "Sequential counter",
        "commander": "Commander",
        "product": "Product"
    }
    amo_colors = {
        "pairwise": "#1f77b4",
        "binary": "#ff7f0e",
        "sequential": "#2ca02c",
        "commander": "#d62728",
        "product": "#9467bd"
    }
    amo_markers = {
        "pairwise": "o",
        "binary": "s",
        "sequential": "^",
        "commander": "D",
        "product": "v"
    }

    # Figure 4.1: Number of clauses
    plt.figure(figsize=(9, 5.5))
    for amo in amo_methods:
        sub = sat_df[sat_df["amo_encoding"] == amo]
        if sub.empty:
            continue
        grouped = sub.groupby("matrix_size")["num_constraints"].mean()
        plt.plot(
            size_labels,
            [grouped.get(s, 0) for s in sizes],
            label=amo_names[amo],
            color=amo_colors[amo],
            marker=amo_markers[amo]
        )
    plt.title("Figure 4.1: Number of clauses across CNF encoding methods", fontweight="bold", pad=12)
    plt.xlabel("Sudoku Board Size (NxN)", fontweight="bold")
    plt.ylabel("Number of Clauses", fontweight="bold")
    plt.grid(True)
    plt.legend(title="CNF Encoding Method", loc="upper left", frameon=True)
    plt.tight_layout()
    f41_path = os.path.join(output_dir, "fig_4_1_clauses_comparison.png")
    plt.savefig(f41_path, dpi=300)
    plt.close()
    print(f"Saved: {f41_path}")

    # Figure 4.2: Number of variables
    plt.figure(figsize=(9, 5.5))
    for amo in amo_methods:
        sub = sat_df[sat_df["amo_encoding"] == amo]
        if sub.empty:
            continue
        grouped = sub.groupby("matrix_size")["num_vars"].mean()
        plt.plot(
            size_labels,
            [grouped.get(s, 0) for s in sizes],
            label=amo_names[amo],
            color=amo_colors[amo],
            marker=amo_markers[amo]
        )
    plt.title("Figure 4.2: Number of variables across CNF encoding methods", fontweight="bold", pad=12)
    plt.xlabel("Sudoku Board Size (NxN)", fontweight="bold")
    plt.ylabel("Number of Variables", fontweight="bold")
    plt.grid(True)
    plt.legend(title="CNF Encoding Method", loc="upper left", frameon=True)
    plt.tight_layout()
    f42_path = os.path.join(output_dir, "fig_4_2_variables_comparison.png")
    plt.savefig(f42_path, dpi=300)
    plt.close()
    print(f"Saved: {f42_path}")

    # Figure 4.3: SAT runtime
    plt.figure(figsize=(9, 5.5))
    for amo in amo_methods:
        sub = sat_df[sat_df["amo_encoding"] == amo]
        if sub.empty:
            continue
        grouped = sub.groupby("matrix_size")["time_total_sec"].mean()
        plt.plot(
            size_labels,
            [grouped.get(s, 0) for s in sizes],
            label=amo_names[amo],
            color=amo_colors[amo],
            marker=amo_markers[amo]
        )
    plt.title("Figure 4.3: Runtime comparison of SAT encoding methods", fontweight="bold", pad=12)
    plt.xlabel("Sudoku Board Size (NxN)", fontweight="bold")
    plt.ylabel("Runtime (seconds)", fontweight="bold")
    plt.grid(True)
    plt.legend(title="CNF Encoding Method", loc="upper left", frameon=True)
    plt.tight_layout()
    f43_path = os.path.join(output_dir, "fig_4_3_runtime_sat.png")
    plt.savefig(f43_path, dpi=300)
    plt.close()
    print(f"Saved: {f43_path}")

    # Figure 4.4: Cross-paradigm comparison
    cross_df = df[(df["paradigm"] != "SAT") | (df["amo_encoding"] == "sequential")].copy()
    solvers = [
        ("glucose4", "PySAT Glucose4 (SAT)", "#1f77b4", "o"),
        ("OR-Tools_CP-SAT", "OR-Tools CP-SAT (CP)", "#2ca02c", "^"),
        ("CPLEX_CP", "IBM CPLEX CP (CP)", "#17becf", "s"),
        ("Gurobi_Optimizer", "Gurobi Optimizer (ILP)", "#d62728", "D"),
        ("CPLEX_MIP", "IBM CPLEX MIP (ILP)", "#9467bd", "v"),
    ]

    plt.figure(figsize=(9, 5.5))
    for s_id, s_label, col, m in solvers:
        sub = cross_df[cross_df["solver_name"] == s_id]
        if sub.empty:
            continue
        grouped = sub.groupby("matrix_size")["time_total_sec"].mean()
        x_pts = []
        y_pts = []
        for s, s_lbl in zip(sizes, size_labels):
            if s in grouped:
                x_pts.append(s_lbl)
                y_pts.append(grouped[s])
        if x_pts:
            plt.plot(x_pts, y_pts, label=s_label, color=col, marker=m)

    plt.title("Figure 4.4: Runtime comparison across Exact Solvers (SAT, CP, ILP)", fontweight="bold", pad=12)
    plt.xlabel("Sudoku Board Size (NxN)", fontweight="bold")
    plt.ylabel("Runtime (seconds)", fontweight="bold")
    plt.grid(True)
    plt.legend(title="Solvers", loc="upper left", frameon=True)
    plt.tight_layout()
    f44_path = os.path.join(output_dir, "fig_4_4_runtime_solvers.png")
    plt.savefig(f44_path, dpi=300)
    plt.close()
    print(f"Saved: {f44_path}")
