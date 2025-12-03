import matplotlib.pyplot as plt
import os
import re
import csv
from collections import defaultdict


def clean_model_name(name: str) -> str:
    """Strip provider prefixes and date suffixes from model name."""
    if "/" in name:
        name = name.split("/")[-1]
    name = re.sub(r"-\d{4}-\d{2}-\d{2}$", "", name)
    return name


def parse_builder_name(builder_str: str):
    """Parse builder name into a readable strategy name."""
    if builder_str == "agent_chain_tools":
        return "Memory Update Style"
    elif builder_str == "agent_chain_assistant_style":
        return "ToolCall Style"
    else:
        # Generic parsing
        parts = builder_str.replace("agent_chain_", "").replace("_", " ").title()
        return parts


def plot_experiment_3_results():
    """Plot experiment 3 results with strategy comparison (like exp 1, 2, 4)."""
    
    # Load data from both exp3 and exp4 files to get best results
    exp3_file = "../outputs/exp3/exp3_toolagent_2025-11-28-22-28-53.csv"
    exp4_file = "../outputs/exp4_toolagent_2025-12-02-21-48-09.csv"
    
    model_stats = defaultdict(lambda: {
        'total': 0, 
        'valid': 0, 
        'invalid': 0,
        'builders': defaultdict(lambda: {'total': 0, 'valid': 0, 'invalid': 0})
    })
    
    # Get GPT results from exp3
    if os.path.exists(exp3_file):
        with open(exp3_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                model = row['model']
                if 'gpt-4.1-mini' in model.lower():
                    builder = row.get('builder', 'agent_chain_tools')
                    valid = row['valid'].strip().lower() == 'true'
                    
                    model_stats[model]['total'] += 1
                    model_stats[model]['builders'][builder]['total'] += 1
                    
                    if valid:
                        model_stats[model]['valid'] += 1
                        model_stats[model]['builders'][builder]['valid'] += 1
                    else:
                        model_stats[model]['invalid'] += 1
                        model_stats[model]['builders'][builder]['invalid'] += 1
    
    # Get Qwen results from exp4
    if os.path.exists(exp4_file):
        with open(exp4_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                model = row['model']
                if 'qwen' in model.lower():
                    builder = row.get('builder', 'agent_chain_tools')
                    valid = row['valid'].strip().lower() == 'true'
                    
                    model_stats[model]['total'] += 1
                    model_stats[model]['builders'][builder]['total'] += 1
                    
                    if valid:
                        model_stats[model]['valid'] += 1
                        model_stats[model]['builders'][builder]['valid'] += 1
                    else:
                        model_stats[model]['invalid'] += 1
                        model_stats[model]['builders'][builder]['invalid'] += 1
    
    # Check if we have multiple builders
    all_builders = set()
    for model_stats_dict in model_stats.values():
        all_builders.update(model_stats_dict['builders'].keys())
    
    models = sorted(model_stats.keys())
    
    # Create the plot - format like experiment 4
    plt.style.use('default')
    
    if len(all_builders) > 1:
        # Multiple strategies: show like experiment 4 (horizontal bars per model)
        fig, axes = plt.subplots(
            nrows=1,
            ncols=len(models),
            figsize=(7 * len(models), 5),
            sharey=True,
        )
        
        if len(models) == 1:
            axes = [axes]
        
        colors = ["#e74c3c", "#2ecc71"]  # Fail (red), Pass (green)
        
        # Get all strategies across all models
        all_strategies = sorted(all_builders, key=lambda x: parse_builder_name(x))
        
        for i, model in enumerate(models):
            ax = axes[i]
            model_clean = clean_model_name(model)
            stats = model_stats[model]
            
            # Prepare data for this model
            strategies_data = []
            for builder in all_strategies:
                builder_stats = stats['builders'].get(builder, {'total': 0, 'valid': 0, 'invalid': 0})
                total = builder_stats['total']
                if total > 0:
                    valid = builder_stats['valid']
                    invalid = builder_stats['invalid']
                    pass_rate = (valid / total * 100) if total > 0 else 0
                    fail_rate = (invalid / total * 100) if total > 0 else 0
                    strategies_data.append({
                        'strategy': parse_builder_name(builder),
                        'pass': pass_rate,
                        'fail': fail_rate
                    })
            
            if strategies_data:
                # Create horizontal stacked bars
                y_pos = range(len(strategies_data))
                strategies = [d['strategy'] for d in strategies_data]
                fail_rates = [d['fail'] for d in strategies_data]
                pass_rates = [d['pass'] for d in strategies_data]
                
                ax.barh(y_pos, fail_rates, color=colors[0], height=0.6, edgecolor='white', linewidth=1, label='Fail')
                ax.barh(y_pos, pass_rates, left=fail_rates, color=colors[1], height=0.6, edgecolor='white', linewidth=1, label='Pass')
                
                # Add percentage labels
                for j, (fail, pass_val) in enumerate(zip(fail_rates, pass_rates)):
                    if fail >= 5:
                        ax.text(fail / 2, j, f'{fail:.1f}%', 
                               ha='center', va='center', color='white', fontsize=11, fontweight='bold')
                    if pass_val >= 5:
                        ax.text(fail + pass_val / 2, j, f'{pass_val:.1f}%', 
                               ha='center', va='center', color='white', fontsize=11, fontweight='bold')
                
                ax.set_yticks(y_pos)
                ax.set_yticklabels(strategies)
            
            ax.set_title(f"{model_clean}", fontsize=18, fontweight='bold', pad=15)
            ax.set_xlabel("Rate (%)", fontsize=14)
            ax.set_xlim(0, 100)
            ax.set_ylabel("Prompting Strategy", fontsize=14)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
        
        # Global legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=colors[0], label='Fail'),
            Patch(facecolor=colors[1], label='Pass')
        ]
        fig.legend(
            handles=legend_elements,
            loc='lower center',
            bbox_to_anchor=(0.5, -0.05),
            ncol=2,
            frameon=False,
            fontsize=12
        )
        
        plt.suptitle('Experiment 3: Agent Chain Tools', fontsize=20, fontweight='bold', y=1.02)
        
    else:
        # Single strategy: show side-by-side comparison with explanation
        fig, ax = plt.subplots(figsize=(10, 6))
        
        plot_data = []
        for model in models:
            stats = model_stats[model]
            model_clean = clean_model_name(model)
            total = stats['total']
            valid = stats['valid']
            invalid = stats['invalid']
            pass_rate = (valid / total * 100) if total > 0 else 0
            fail_rate = (invalid / total * 100) if total > 0 else 0
            
            plot_data.append({
                'model': model_clean,
                'pass': pass_rate,
                'fail': fail_rate,
                'total': total
            })
        
        models_list = [d['model'] for d in plot_data]
        pass_rates = [d['pass'] for d in plot_data]
        fail_rates = [d['fail'] for d in plot_data]
        
        x = range(len(models_list))
        width = 0.6
        
        bars1 = ax.bar(x, fail_rates, width, label='Fail', color='#e74c3c', edgecolor='white', linewidth=1)
        bars2 = ax.bar(x, pass_rates, width, bottom=fail_rates, label='Pass', color='#2ecc71', edgecolor='white', linewidth=1)
        
        # Add percentage labels
        for i, (fail, pass_val) in enumerate(zip(fail_rates, pass_rates)):
            if fail >= 5:
                ax.text(i, fail / 2, f'{fail:.1f}%', ha='center', va='center', 
                       color='white', fontsize=12, fontweight='bold')
            if pass_val >= 5:
                ax.text(i, fail + pass_val / 2, f'{pass_val:.1f}%', ha='center', va='center', 
                       color='white', fontsize=12, fontweight='bold')
        
        ax.set_xlabel('Model', fontsize=14, fontweight='bold')
        ax.set_ylabel('Rate (%)', fontsize=14, fontweight='bold')
        ax.set_title('Experiment 3: Agent Chain Tools\nPass/Fail Rates by Model', 
                     fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(models_list, fontsize=12)
        ax.set_ylim(0, 100)
        ax.legend(loc='upper right', frameon=False, fontsize=12)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add explanation text
        strategy_name = parse_builder_name(list(all_builders)[0]) if all_builders else "Agent Chain Tools"
        explanation = f"Note: Only one prompting strategy tested ({strategy_name}).\n" \
                     f"To match Experiments 1, 2, and 4, add 'agent_chain_assistant_style' builder."
        ax.text(0.5, -0.15, explanation, transform=ax.transAxes, 
               ha='center', va='top', fontsize=10, style='italic', 
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    os.makedirs("../figures", exist_ok=True)
    output_filename = "../figures/experiment_3_results.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"\n✅ Experiment 3 plot saved to {output_filename}")
    
    # Print summary table
    print("\n" + "=" * 70)
    print("EXPERIMENT 3 RESULTS SUMMARY")
    print("=" * 70)
    
    if len(all_builders) > 1:
        print(f"\n{'Model':<25} {'Strategy':<30} {'Pass Rate':<15} {'Fail Rate':<15} {'Total':<10}")
        print("-" * 100)
        for model in sorted(models):
            model_clean = clean_model_name(model)
            stats = model_stats[model]
            for builder in sorted(stats['builders'].keys()):
                builder_stats = stats['builders'][builder]
                total = builder_stats['total']
                if total > 0:
                    valid = builder_stats['valid']
                    invalid = builder_stats['invalid']
                    pass_rate = (valid / total * 100) if total > 0 else 0
                    fail_rate = (invalid / total * 100) if total > 0 else 0
                    strategy_name = parse_builder_name(builder)
                    print(f"{model_clean:<25} {strategy_name:<30} {pass_rate:>6.1f}%        {fail_rate:>6.1f}%        {total:<10}")
    else:
        print(f"\n{'Model':<25} {'Pass Rate':<15} {'Fail Rate':<15} {'Total':<10}")
        print("-" * 70)
        for model in sorted(models):
            stats = model_stats[model]
            model_clean = clean_model_name(model)
            total = stats['total']
            valid = stats['valid']
            invalid = stats['invalid']
            pass_rate = (valid / total * 100) if total > 0 else 0
            fail_rate = (invalid / total * 100) if total > 0 else 0
            print(f"{model_clean:<25} {pass_rate:>6.1f}%        {fail_rate:>6.1f}%        {total:<10}")
        print("\nNote: Only one prompting strategy tested. Add 'agent_chain_assistant_style' to compare strategies.")
    
    print("=" * 70)


if __name__ == "__main__":
    plot_experiment_3_results()
