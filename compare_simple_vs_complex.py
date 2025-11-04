"""
Compare results between simple and complex schema experiments
"""
import json
from pathlib import Path
from collections import defaultdict

def load_latest_results(pattern):
    """Load the latest results file matching pattern"""
    result_files = sorted(Path('.').glob(pattern), reverse=True)
    if result_files:
        with open(result_files[0]) as f:
            return json.load(f), result_files[0].name
    return None, None

def analyze_comparison():
    """Compare simple vs complex schema results"""
    print("="*70)
    print("COMPARISON: SIMPLE vs COMPLEX SCHEMAS")
    print("="*70)
    
    # Load results
    simple_data, simple_file = load_latest_results('results_exp1_*.json')
    complex_data, complex_file = load_latest_results('results_exp1_complex_*.json')
    
    # Exclude complex results from simple results
    if simple_file and 'complex' in simple_file:
        simple_data = None
        simple_file = None
    
    if not simple_data:
        print("⚠️  Simple schema results not found. Run eval_adherence.py first.")
        return
    
    if not complex_data:
        print("⚠️  Complex schema results not found. Run eval_adherence_complex.py first.")
        return
    
    print(f"Simple schema file: {simple_file}")
    print(f"Complex schema file: {complex_file}")
    print()
    
    # Compare overall results
    print("="*70)
    print("OVERALL COMPARISON BY VARIANT")
    print("="*70)
    print(f"{'Variant':<30} {'Simple':<20} {'Complex':<20} {'Difference':<15}")
    print("-" * 85)
    
    for variant in simple_data['summary'].keys():
        simple_result = simple_data['summary'][variant]
        complex_result = complex_data['summary'].get(variant, {})
        
        simple_rate = simple_result.get('percentage', 0)
        complex_rate = complex_result.get('percentage', 0)
        diff = complex_rate - simple_rate
        
        print(f"{variant:<30} {simple_rate:>5.1f}% ({simple_result.get('valid', 0)}/{simple_result.get('total', 0)})  "
              f"{complex_rate:>5.1f}% ({complex_result.get('valid', 0)}/{complex_result.get('total', 0)})  "
              f"{diff:>+6.1f}%")
    
    # Compare extraneous text
    print("\n" + "="*70)
    print("EXTRANEOUS TEXT COMPARISON")
    print("="*70)
    print(f"{'Variant':<30} {'Simple Avg %':<15} {'Complex Avg %':<15} {'Difference':<15}")
    print("-" * 75)
    
    for variant in simple_data['summary'].keys():
        simple_ext = simple_data['summary'][variant].get('avg_extraneous_text_pct', 0)
        complex_ext = complex_data['summary'].get(variant, {}).get('avg_extraneous_text_pct', 0)
        diff = complex_ext - simple_ext
        
        print(f"{variant:<30} {simple_ext:>6.2f}%       {complex_ext:>6.2f}%       {diff:>+6.2f}%")
    
    # Error breakdown for complex schemas
    if 'schema_type_breakdown' in complex_data:
        print("\n" + "="*70)
        print("COMPLEX SCHEMA RESULTS BY TYPE")
        print("="*70)
        
        for schema_type, stats in sorted(complex_data['schema_type_breakdown'].items()):
            total = stats['total']
            valid = stats['valid']
            rate = (valid / total * 100) if total > 0 else 0
            print(f"\n{schema_type.upper()}: {valid}/{total} ({rate:.1f}%)")
            
            for variant, v_stats in stats.get('by_variant', {}).items():
                v_total = v_stats['total']
                v_valid = v_stats['valid']
                v_rate = (v_valid / v_total * 100) if v_total > 0 else 0
                print(f"  {variant:25s}: {v_valid}/{v_total} ({v_rate:.1f}%)")
    
    # Key insights
    print("\n" + "="*70)
    print("KEY INSIGHTS")
    print("="*70)
    
    insights = []
    
    # Check if complex schemas are harder
    for variant in simple_data['summary'].keys():
        simple_rate = simple_data['summary'][variant].get('percentage', 0)
        complex_rate = complex_data['summary'].get(variant, {}).get('percentage', 0)
        diff = complex_rate - simple_rate
        
        if diff < -5:
            insights.append(f"❌ {variant}: Complex schemas significantly harder ({diff:.1f}% drop)")
        elif diff < -1:
            insights.append(f"⚠️  {variant}: Complex schemas slightly harder ({diff:.1f}% drop)")
        elif diff > 1:
            insights.append(f"✅ {variant}: Complex schemas actually easier ({diff:.1f}% improvement)")
        else:
            insights.append(f"➡️  {variant}: No significant difference ({diff:.1f}%)")
    
    # Check role structure impact
    simple_user = simple_data['summary'].get('user_only', {}).get('percentage', 0)
    simple_system = simple_data['summary'].get('system_plus_user', {}).get('percentage', 0)
    complex_user = complex_data['summary'].get('user_only', {}).get('percentage', 0)
    complex_system = complex_data['summary'].get('system_plus_user', {}).get('percentage', 0)
    
    simple_diff = abs(simple_user - simple_system)
    complex_diff = abs(complex_user - complex_system)
    
    if complex_diff > simple_diff + 2:
        insights.append(f"📊 Role structure matters MORE with complex schemas (difference: {simple_diff:.1f}% → {complex_diff:.1f}%)")
    elif complex_diff < simple_diff - 2:
        insights.append(f"📊 Role structure matters LESS with complex schemas (difference: {simple_diff:.1f}% → {complex_diff:.1f}%)")
    else:
        insights.append(f"📊 Role structure impact similar across schema complexity (difference: {simple_diff:.1f}% vs {complex_diff:.1f}%)")
    
    for insight in insights:
        print(f"  {insight}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    analyze_comparison()

