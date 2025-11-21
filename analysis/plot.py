import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import glob
import os
import re


def clean_model_name(name):
    if "/" in name:
        name = name.split("/")[-1]
    name = re.sub(r'-\d{4}-\d{2}-\d{2}$', '', name)
    return name


def parse_builder_name(builder_str):
    parts = builder_str.split('_', 1)
    if len(parts) == 2:
        task = parts[0].title()
        # Replace underscores with spaces for strategy name
        strategy = parts[1].replace('_', ' ').title()
        return task, strategy
    return "Unknown", builder_str


def plot_benchmark_results_experiment_1(file_pattern: str):
    # 1. Load Data
    files = glob.glob(file_pattern)
    if not files:
        print("No files found.")
        return

    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f)
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {f}: {e}")

    if not dfs:
        return

    full_df = pd.concat(dfs, ignore_index=True)

    # 2. Preprocessing
    full_df['valid'] = full_df['valid'].astype(bool)
    full_df['model_clean'] = full_df['model'].apply(clean_model_name)

    full_df[['task', 'strategy']] = full_df['builder'].apply(
        lambda x: pd.Series(parse_builder_name(x))
    )

    # --- CONFIGURATION: Define Strict Order ---
    # This ensures the plot looks consistent even if data is missing
    EXPECTED_STRATEGIES = [
        "User Only",
        "System Plus User",
        "User Plus Assistant Seed"
    ]

    # 3. Aggregation
    # Group by Model, Task, Strategy and calculate Pass/Fail rates
    summary = full_df.groupby(['model_clean', 'task', 'strategy'])['valid'].value_counts(normalize=True).unstack(
        fill_value=0)
    summary = summary * 100

    # Ensure Pass/Fail columns exist
    if True not in summary.columns: summary[True] = 0
    if False not in summary.columns: summary[False] = 0

    summary = summary.rename(columns={True: 'Pass Rate', False: 'Fail Rate'})
    summary = summary.reset_index()

    # 4. Plotting
    sns.set_theme(style="whitegrid", context="talk")

    tasks = sorted(summary['task'].unique())
    models = sorted(summary['model_clean'].unique())

    # Dynamic figure size
    fig, axes = plt.subplots(
        nrows=len(models),
        ncols=len(tasks),
        figsize=(8 * len(tasks), 4 * len(models)),
        sharey=False,  # We don't share Y because we want to enforce order per plot
        sharex=True
    )

    # Normalize axes array
    if len(models) == 1 and len(tasks) == 1:
        axes = [[axes]]
    elif len(models) == 1:
        axes = [axes]
    elif len(tasks) == 1:
        axes = [[ax] for ax in axes]

    colors = ["#e74c3c", "#2ecc71"]  # Red (Fail), Green (Pass)

    for i, model in enumerate(models):
        for j, task in enumerate(tasks):
            ax = axes[i][j]

            # Filter data for this specific panel
            subset = summary[
                (summary['model_clean'] == model) &
                (summary['task'] == task)
                ]

            subset = subset.set_index('strategy')
            subset = subset.reindex(EXPECTED_STRATEGIES)


            if not subset.dropna(how='all').empty:
                subset[['Fail Rate', 'Pass Rate']].plot(
                    kind='barh',
                    stacked=True,
                    ax=ax,
                    color=colors,
                    width=0.6,
                    edgecolor='white',
                    legend=False
                )
            else:
                ax.text(0.5, 0.5, "No Data", ha='center', va='center', transform=ax.transAxes)

            # Titles and Labels
            if i == 0:
                ax.set_title(f"{task}", fontsize=18, fontweight='bold', pad=20)

            if j == 0:
                ax.set_ylabel(model, fontsize=16, fontweight='bold')
            else:
                ax.set_ylabel("")

            if i == len(models) - 1:
                ax.set_xlabel("Pass Rate (%)")
            else:
                ax.set_xlabel("")

            ax.set_xlim(0, 100)
            sns.despine(left=True, bottom=True)

            # Add percentage labels
            for container in ax.containers:
                # Only label if the value exists and > 0
                labels = []
                for val in container.datavalues:
                    if pd.isna(val) or val < 5:  # Don't label tiny or missing bars
                        labels.append('')
                    else:
                        labels.append(f'{val:.1f}%')
                ax.bar_label(container, labels=labels, label_type='center', color='white', fontsize=11,
                             fontweight='bold')

    # Global Legend
    handles, labels = axes[0][0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, ["Fail", "Pass"], loc='lower center', bbox_to_anchor=(0.5, -0.05), ncol=2, frameon=False)

    plt.tight_layout()

    output_filename = "figures/experiment_1_benchmark_comparison.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Comparison plot saved to {output_filename}")


plot_benchmark_results_experiment_1("../outputs/*.csv")