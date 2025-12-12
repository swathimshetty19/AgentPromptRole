"""
Experiment 3: Agentic Decision-Making with Long Context

Tests how different role configurations for encoding history affect:
- Decision-making accuracy
- Context retention
- Task completion
"""

import json, yaml, time
from tqdm import tqdm
from builders.agentic import VARIANTS
from models.openai_compat import OpenAICompatClient
from datetime import datetime
import re

# Load config
cfg = yaml.safe_load(open("configs/exp3.yaml"))
client = OpenAICompatClient(cfg["model"])

print("="*70)
print("EXPERIMENT 3: AGENTIC DECISION-MAKING WITH LONG CONTEXT")
print("="*70)
print(f"Running Experiment with model: {cfg['model']}")
print(f"Variants: {cfg['variants']}")
print(f"Sample limit: {cfg['sample_limit']}")
print(f"Total API calls: {cfg['sample_limit'] * len(cfg['variants'])}\n")

# Store detailed results
results = {}
detailed_results = []

def extract_answer(output):
    """Extract the answer from model output (heuristic-based)"""
    output = output.strip()
    
    # Try to find the answer in various formats
    # Look for patterns like "Answer: X", "The answer is X", etc.
    patterns = [
        r"(?:answer|result|solution)[:\s]+([^\n\.]+)",
        r"(?:is|are|was|were)[:\s]+([^\n\.]+)",
        r"^([^\n\.]+)$",  # Single line answer
    ]
    
    for pattern in patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # If no pattern matches, return first line or first 50 chars
    return output.split('\n')[0][:100].strip()

def check_answer_correct(predicted, expected, task_type):
    """Check if predicted answer matches expected answer"""
    predicted = str(predicted).strip().lower()
    expected = str(expected).strip().lower()
    
    # Exact match
    if predicted == expected:
        return True
    
    # Numeric comparison (for math problems)
    try:
        pred_num = float(re.sub(r'[^\d\.]', '', predicted))
        exp_num = float(re.sub(r'[^\d\.]', '', expected))
        if abs(pred_num - exp_num) < 0.01:  # Allow small floating point differences
            return True
    except:
        pass
    
    # Substring match (for descriptive answers)
    if expected in predicted or predicted in expected:
        return True
    
    # Check if key numbers match
    pred_numbers = re.findall(r'\d+\.?\d*', predicted)
    exp_numbers = re.findall(r'\d+\.?\d*', expected)
    if pred_numbers and exp_numbers:
        if any(pn == en for pn in pred_numbers for en in exp_numbers):
            return True
    
    return False

# Loop through prompt variants
for variant in cfg["variants"]:
    total, correct = 0, 0
    errors = []
    total_tokens_estimate = 0  # Rough estimate based on message length
    
    print(f"\n### Testing variant: {variant}")

    # Read all lines first
    with open(cfg["dataset"]) as f:
        lines = [line for i, line in enumerate(f) if i < cfg["sample_limit"]]
    
    # Process with progress bar
    for line in tqdm(lines, desc=f"  {variant}", unit="sample"):
        row = json.loads(line)
        
        try:
            # Build messages using variant
            msgs = VARIANTS[variant](
                row["task_description"],
                row["history"],
                row["current_query"]
            )
            
            # Estimate tokens (rough: 1 token ≈ 4 chars)
            total_tokens_estimate += sum(len(msg.get("content", "")) for msg in msgs) / 4
            
            # Make API call
            output = client.chat(msgs)
            total += 1
            
            # Extract and check answer
            predicted = extract_answer(output)
            is_correct = check_answer_correct(predicted, row["expected_answer"], row.get("task_type", ""))
            
            if is_correct:
                correct += 1
            
            # Store detailed result
            detailed_results.append({
                "variant": variant,
                "sample_id": total,
                "task_id": row.get("task_id", ""),
                "task_type": row.get("task_type", ""),
                "current_query": row["current_query"],
                "expected_answer": row["expected_answer"],
                "predicted_answer": predicted,
                "correct": is_correct,
                "output": output[:500] if len(output) > 500 else output,
                "num_history_steps": len(row["history"]),
                "context_length": row.get("context_length", "medium")
            })
            
            if not is_correct:
                errors.append({
                    "sample": total,
                    "task_id": row.get("task_id", ""),
                    "expected": row["expected_answer"],
                    "predicted": predicted,
                    "output_preview": output[:200]
                })
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
            
        except Exception as e:
            error_msg = str(e)
            # Print first few errors for debugging
            if len(errors) < 3:
                print(f"\n⚠️  Error on sample {total+1}: {error_msg[:200]}")
            
            if "429" in error_msg or "rate limit" in error_msg.lower():
                print(f"\n⚠️  Rate limit hit! Waiting 60 seconds...")
                time.sleep(60)
                # Retry once
                try:
                    msgs = VARIANTS[variant](
                        row["task_description"],
                        row["history"],
                        row["current_query"]
                    )
                    output = client.chat(msgs)
                    total += 1
                    predicted = extract_answer(output)
                    is_correct = check_answer_correct(predicted, row["expected_answer"], row.get("task_type", ""))
                    if is_correct:
                        correct += 1
                    detailed_results.append({
                        "variant": variant,
                        "sample_id": total,
                        "task_id": row.get("task_id", ""),
                        "task_type": row.get("task_type", ""),
                        "current_query": row["current_query"],
                        "expected_answer": row["expected_answer"],
                        "predicted_answer": predicted,
                        "correct": is_correct,
                        "output": output[:500],
                        "num_history_steps": len(row["history"]),
                        "context_length": row.get("context_length", "medium")
                    })
                    time.sleep(0.1)
                except Exception as retry_err:
                    errors.append({
                        "sample": total+1,
                        "error": f"Retry failed: {str(retry_err)[:100]}",
                        "output_preview": ""
                    })
            else:
                errors.append({
                    "sample": total+1,
                    "error": error_msg[:200],
                    "output_preview": ""
                })
            continue

    if total > 0:
        accuracy = correct / total * 100
        avg_tokens = total_tokens_estimate / total if total > 0 else 0
        
        result = {
            "correct": correct,
            "total": total,
            "accuracy": accuracy,
            "avg_tokens_estimate": avg_tokens,
            "errors": errors[:10]  # Store first 10 errors
        }
        results[variant] = result
        print(f"  ✅ {variant}: {correct}/{total} correct ({accuracy:.1f}%)")
        print(f"  📊 Avg tokens (estimate): {avg_tokens:.0f}")
        if errors:
            print(f"  ⚠️  {len(errors)} incorrect answers")
            if len(errors) <= 5:
                for err in errors[:5]:
                    print(f"     Sample {err['sample']}: Expected '{err.get('expected', 'N/A')}', Got '{err.get('predicted', 'N/A')[:50]}'")
    else:
        print(f"  ⚠️  {variant}: No successful API calls (all failed)")

# Final summary
print("\n" + "="*70)
print("FINAL RESULTS - AGENTIC DECISION-MAKING")
print("="*70)
print(f"{'Variant':<30} {'Correct/Total':<15} {'Accuracy %':<12} {'Avg Tokens':<12}")
print("-" * 70)
for variant, result in results.items():
    print(f"{variant:<30} {result['correct']:3d}/{result['total']:<11} {result['accuracy']:>5.1f}%      {result['avg_tokens_estimate']:>8.0f}")

# Results by task type
print("\n" + "="*70)
print("RESULTS BY TASK TYPE")
print("="*70)
task_types = set(r.get("task_type", "unknown") for r in detailed_results)
for task_type in sorted(task_types):
    print(f"\n{task_type.upper()}:")
    for variant in cfg["variants"]:
        variant_results = [r for r in detailed_results if r["variant"] == variant and r.get("task_type") == task_type]
        if variant_results:
            correct = sum(1 for r in variant_results if r["correct"])
            total = len(variant_results)
            print(f"  {variant}: {correct}/{total} ({correct/total*100:.1f}%)")

# Save detailed results
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
results_file = f"results_exp3_{timestamp}.json"
with open(results_file, "w") as f:
    json.dump({
        "experiment": "Experiment 3: Agentic Decision-Making with Long Context",
        "model": cfg["model"],
        "variants": cfg["variants"],
        "sample_limit": cfg["sample_limit"],
        "timestamp": timestamp,
        "summary": results,
        "detailed_results": detailed_results
    }, f, indent=2)

print(f"\n💾 Detailed results saved to: {results_file}")
print(f"   Total samples: {len(detailed_results)}")

