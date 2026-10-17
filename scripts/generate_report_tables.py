"""
generate_report_tables.py: Extracts benchmark statistics from benchmark_results.csv
and generates LaTeX tables for the Elsevier cas-sc template.
- Table 1: The runtime of different SAT encoding methods (seconds / timeout)
- Table 2: Ablation Study chi tiết (Số biến & Số mệnh đề qua các kích thước)
- Table 3: Cross-Paradigm Comparison (SAT vs CP vs ILP) kèm tỷ lệ giải thành công (Solved Rate).
"""

import os
import sys
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def df_to_elsevier_latex(df, caption, label):
    """Convert DataFrame to Elsevier cas-sc booktabs table format."""
    cols = list(df.columns)
    col_align = "l" + "r" * (len(cols) - 1)
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        f"\\begin{{tabular}}{{{col_align}}}",
        "\\toprule",
        " & ".join(f"\\textbf{{{c.replace('_', '\\_')}}}" for c in cols) + " \\\\",
        "\\midrule"
    ]
    for _, row in df.iterrows():
        row_vals = []
        for c in cols:
            val = row[c]
            if isinstance(val, float):
                row_vals.append(f"{val:.4f}")
            else:
                row_vals.append(str(val).replace("%", "\\%").replace("_", "\\_"))
        lines.append(" & ".join(row_vals) + " \\\\")
    lines.extend([
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}"
    ])
    return "\n".join(lines)


def generate_tables(csv_path=None):
    if csv_path is None:
        csv_path = os.path.join(PROJECT_ROOT, "benchmark_results.csv")

    if not os.path.isfile(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    df = pd.read_csv(csv_path)
    if df.empty:
        print("Error: CSV file is empty.")
        return

    latex_output_parts = []

    # Table 1: Runtime of SAT AMO encodings
    sat_df = df[df["paradigm"] == "SAT"].copy()
    if not sat_df.empty:
        amo_order = ["pairwise", "binary", "sequential", "commander", "product"]
        amo_display = {
            "pairwise": "Binomial",
            "binary": "Binary",
            "sequential": "Sequential counter",
            "commander": "Commander",
            "product": "Product"
        }

        sizes = sorted(sat_df["matrix_size"].unique())
        runtime_rows = []

        for sz in sizes:
            row_dict = {"n": f"{sz}x{sz}"}
            for amo in amo_order:
                sub = sat_df[(sat_df["matrix_size"] == sz) & (sat_df["amo_encoding"] == amo)]
                if sub.empty:
                    row_dict[amo_display[amo]] = "N/A"
                else:
                    valid_sub = sub[sub["is_valid"] == True]
                    if valid_sub.empty:
                        row_dict[amo_display[amo]] = "timeout"
                    else:
                        mean_t = valid_sub["time_total_sec"].mean()
                        if (len(valid_sub) / len(sub)) < 0.5:
                            row_dict[amo_display[amo]] = f"timeout ({len(valid_sub)}/{len(sub)})"
                        else:
                            row_dict[amo_display[amo]] = f"{mean_t:.4f}"
            runtime_rows.append(row_dict)

        tab1_df = pd.DataFrame(runtime_rows)
        print("Table 1: SAT AMO Runtime (seconds):")
        print(tab1_df.to_string(index=False))

        latex_tab1 = df_to_elsevier_latex(
            tab1_df,
            caption="The runtime of different SAT encoding methods (seconds).",
            label="tab:sat_runtime_comparison"
        )
        latex_output_parts.append(latex_tab1)

        # Table 2: Ablation study on variables and clauses
        ablation_summary = sat_df.groupby(["matrix_size", "amo_encoding"]).agg({
            "num_vars": "mean",
            "num_constraints": "mean",
            "time_build_sec": lambda x: x.mean() * 1000,
            "time_solve_sec": lambda x: x.mean() * 1000,
            "time_total_sec": lambda x: x.mean() * 1000
        }).reset_index()

        ablation_summary.rename(columns={
            "matrix_size": "Size (NxN)",
            "amo_encoding": "AMO Method",
            "num_vars": "Avg Vars",
            "num_constraints": "Avg Clauses",
            "time_build_sec": "Encode (ms)",
            "time_solve_sec": "Solve (ms)",
            "time_total_sec": "Total (ms)"
        }, inplace=True)

        print("\nTable 2: SAT Ablation Study:")
        print(ablation_summary.to_string(index=False))

        latex_tab2 = df_to_elsevier_latex(
            ablation_summary,
            caption="Ablation study of five SAT AMO encodings across Sudoku grid sizes.",
            label="tab:sat_ablation"
        )
        latex_output_parts.append(latex_tab2)

    # Table 3: Cross-paradigm comparison (SAT vs CP vs ILP)
    cross_df = df[(df["paradigm"] != "SAT") | (df["amo_encoding"] == "sequential")].copy()
    if not cross_df.empty:
        cross_summary = cross_df.groupby(["matrix_size", "solver_name"]).agg({
            "status": lambda s: f"{(s == 'OPTIMAL').sum()}/{len(s)}",
            "is_valid": lambda v: f"{(v == True).sum() / len(v) * 100:.1f}%",
            "num_vars": "mean",
            "num_constraints": "mean",
            "time_total_sec": lambda x: x.mean() * 1000
        }).reset_index()

        cross_summary.rename(columns={
            "matrix_size": "Size (NxN)",
            "solver_name": "Solver / Method",
            "status": "Solved",
            "is_valid": "Success Rate",
            "num_vars": "Variables",
            "num_constraints": "Constraints",
            "time_total_sec": "Total Time (ms)"
        }, inplace=True)

        print("\nTable 3: Cross-Paradigm Comparison:")
        print(cross_summary.to_string(index=False))

        latex_tab3 = df_to_elsevier_latex(
            cross_summary,
            caption="Comparison of SAT solving against exact methods (CP and ILP).",
            label="tab:cross_solvers"
        )
        latex_output_parts.append(latex_tab3)

    out_dir = os.path.join(PROJECT_ROOT, "report_tables")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "latex_tables.tex")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("% Auto-generated LaTeX tables (Elsevier cas-sc template)\n\n")
        f.write("\n\n".join(latex_output_parts) + "\n")
    print(f"\nSaved LaTeX tables: {out_file}")


if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else None
    generate_tables(csv_file)
