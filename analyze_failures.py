"""
Analyze failures from experiment results
"""
import json
import sys
from pathlib import Path

def analyze_results(results_file):
    """Analyze experiment results and show failures"""
    with open(results_file) as f:
        data = json.load(f)
    
    print("="*70)
    print("EXPERIMENT 1 FAILURE ANALYSIS")
    print("="*70)
    print(f"Model: {data['model']}")
    print(f"Total samples: {len(data['detailed_results'])}")
    print()
    
    # Group by variant
    variants = {}
    for result in data['detailed_results']:
        variant = result['variant']
        if variant not in variants:
            variants[variant] = {'total': 0, 'valid': 0, 'failures': []}
        
        variants[variant]['total'] += 1
        if result['valid']:
            variants[variant]['valid'] += 1
        else:
            variants[variant]['failures'].append(result)
    
    # Print summary
    print("SUMMARY BY VARIANT:")
    print("-" * 70)
    for variant, stats in variants.items():
        success_rate = (stats['valid'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"{variant:30s}: {stats['valid']:3d}/{stats['total']:3d} ({success_rate:5.1f}%)")
        if stats['failures']:
            print(f"  ⚠️  {len(stats['failures'])} failures")
    print()
    
    # Detailed failure analysis
    all_failures = [r for r in data['detailed_results'] if not r['valid']]
    if all_failures:
        print("="*70)
        print("DETAILED FAILURE ANALYSIS")
        print("="*70)
        
        for i, failure in enumerate(all_failures, 1):
            print(f"\n{i}. FAILURE #{i}")
            print("-" * 70)
            print(f"Variant:      {failure['variant']}")
            print(f"Sample ID:    {failure['sample_id']}")
            print(f"Task:         {failure['task_description']}")
            print(f"Error:        {failure['error']}")
            print(f"Extraneous %: {failure['extraneous_text_pct']:.2f}%")
            print(f"Output length: {failure['original_length']} chars")
            print(f"\nFull output:")
            print(f"{'─'*70}")
            print(failure['output'])
            print(f"{'─'*70}")
        
        # Error type analysis
        print("\n" + "="*70)
        print("ERROR TYPE BREAKDOWN")
        print("="*70)
        error_types = {}
        for failure in all_failures:
            error = failure['error']
            # Categorize errors
            if 'Extra data' in error:
                error_type = 'Extra data after JSON'
            elif 'Expecting' in error or 'value' in error.lower():
                error_type = 'JSON parse error'
            elif 'schema' in error.lower():
                error_type = 'Schema validation error'
            else:
                error_type = 'Other'
            
            if error_type not in error_types:
                error_types[error_type] = []
            error_types[error_type].append(failure)
        
        for error_type, failures in error_types.items():
            print(f"\n{error_type}: {len(failures)} occurrence(s)")
            for f in failures:
                print(f"  - {f['variant']} sample {f['sample_id']}: {f['error'][:60]}")
    else:
        print("✅ No failures found!")

if __name__ == "__main__":
    # Find latest results file
    result_files = sorted(Path('.').glob('results_exp1_*.json'), reverse=True)
    
    if result_files:
        print(f"Using latest results file: {result_files[0]}")
        analyze_results(result_files[0])
    elif len(sys.argv) > 1:
        analyze_results(sys.argv[1])
    else:
        print("No results file found. Run eval_adherence.py first or specify a file.")
        print("Usage: python3 analyze_failures.py [results_file.json]")

