import glob
import json
import os
import re

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def clean_model_name(name: str) -> str:
    """Strip provider prefixes and date suffixes from model name."""
    if "/" in name:
        name = name.split("/")[-1]
    # remove trailing -YYYY-MM-DD if present
    name = re.sub(r"-\d{4}-\d{2}-\d{2}$", "", name)
    return name


def parse_builder_name(builder_str: str):
    """
    Generic parser:
    - task = "Multi-turn"
    - strategy = short, readable, idempotent label based on builder suffix.
    """

    # 1. split components
    parts = builder_str.split("_")

    # 2. remove leading boilerplate tokens
    drop_prefixes = {
        "toolbench",
    }
    parts = [p for p in parts if p not in drop_prefixes]

    # 4. remove glue words
    glue = {"with", "plus", "and"}
    parts = [p for p in parts if p not in glue]

    # 5. convert tokens into a readable label
    strategy = " ".join(p.capitalize() for p in parts)

    # 6. fallback if it becomes empty
    if not strategy:
        strategy = builder_str.replace("_", " ").title()

    task = "Multi-turn"
    return task, strategy


def parse_metadata_column(meta_str: str):
    """Safely parse the metadata JSON column."""
    try:
        return json.loads(meta_str)
    except Exception:
        return {}


def plot_multi_turn_results(file_pattern: str):
    # 1. Load Data
    files = glob.glob(file_pattern)
    if not files:
        print("No files found for pattern:", file_pattern)
        return

    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f)
            df["source_file"] = os.path.basename(f)
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {f}: {e}")

    if not dfs:
        print("No valid CSVs loaded.")
        return

    full_df = pd.concat(dfs, ignore_index=True)

    # 2. Preprocessing
    full_df["valid"] = full_df["valid"].astype(bool)
    full_df["model_clean"] = full_df["model"].apply(clean_model_name)

    # Parse builder into (task, strategy) generically
    full_df[["task", "strategy"]] = full_df["builder"].apply(
        lambda x: pd.Series(parse_builder_name(x))
    )

    # Optional: parse metadata JSON if you want to inspect details later
    full_df["metadata_dict"] = full_df["metadata"].apply(parse_metadata_column)

    # Use ALL rows for plotting (no task filter)
    df_for_plot = full_df.copy()
    if df_for_plot.empty:
        print("No rows to plot.")
        return

    # 3. Aggregation: pass/fail rates per model+strategy
    summary = (
        df_for_plot.groupby(["model_clean", "strategy"])["valid"]
        .value_counts(normalize=True)
        .unstack(fill_value=0)
        * 100
    )

    # Ensure columns exist
    if True not in summary.columns:
        summary[True] = 0.0
    if False not in summary.columns:
        summary[False] = 0.0

    summary = summary.rename(columns={True: "Pass Rate", False: "Fail Rate"})
    summary = summary.reset_index()

    print("\n=== Summary (Pass/Fail %) ===")
    print(summary.sort_values(["model_clean", "strategy"]))

    # 4. Plotting
    sns.set_theme(style="whitegrid", context="talk")

    models = sorted(summary["model_clean"].unique())

    fig, axes = plt.subplots(
        nrows=1,
        ncols=len(models),
        figsize=(7 * len(models), 5),
        sharey=True,
    )

    if len(models) == 1:
        axes = [axes]

    colors = ["#e74c3c", "#2ecc71"]  # Fail (red), Pass (green)

    for i, model in enumerate(models):
        ax = axes[i]

        subset = summary[summary["model_clean"] == model].set_index("strategy")

        # Dynamically get all strategies for this model
        strategies_for_model = sorted(subset.index.unique())
        subset = subset.reindex(strategies_for_model)

        if not subset.dropna(how="all").empty:
            subset[["Fail Rate", "Pass Rate"]].plot(
                kind="barh",
                stacked=True,
                ax=ax,
                color=colors,
                width=0.6,
                edgecolor="white",
                legend=False,
            )
        else:
            ax.text(
                0.5,
                0.5,
                "No Data",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )

        ax.set_title(f"{model}", fontsize=18, fontweight="bold", pad=15)
        ax.set_xlabel("Rate (%)")
        ax.set_xlim(0, 100)
        ax.set_ylabel("Prompting Strategy")

        # Add percentage labels inside bars
        for container in ax.containers:
            labels = []
            for val in container.datavalues:
                if pd.isna(val) or val < 5:
                    labels.append("")
                else:
                    labels.append(f"{val:.1f}%")
            ax.bar_label(
                container,
                labels=labels,
                label_type="center",
                color="white",
                fontsize=11,
                fontweight="bold",
            )

        sns.despine(left=True, bottom=True)

    # Global legend
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(
            handles,
            ["Fail", "Pass"],
            loc="lower center",
            bbox_to_anchor=(0.5, -0.05),
            ncol=2,
            frameon=False,
        )

    plt.tight_layout()

    os.makedirs("figures", exist_ok=True)
    output_filename = "figures/experiment_1_benchmark_comparison.png"
    plt.savefig(output_filename, dpi=300, bbox_inches="tight")
    print(f"\nComparison plot saved to {output_filename}")


if __name__ == "__main__":
    # Adjust the pattern if your CSVs live elsewhere
    plot_multi_turn_results("../outputs/exp1/*.csv")
