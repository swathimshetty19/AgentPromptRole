import json, yaml, time
from tqdm import tqdm
from builders.adherence import VARIANTS
from validators.json_schema import validate_json
from models.openai_compat import OpenAICompatClient
from datetime import datetime
import os

# Load config
cfg = yaml.safe_load(open("configs/exp1.yaml"))
client = OpenAICompatClient(cfg["model"])

print(f"Running Experiment with model: {cfg['model']}")
print(f"Variants: {cfg['variants']}")
print(f"Sample limit: {cfg['sample_limit']}")
print(f"Total API calls: {cfg['sample_limit'] * len(cfg['variants'])}\n")

# Store detailed results
results = {}
detailed_results = []  # For CSV/JSON export

# Loop through prompt variants
for variant in cfg["variants"]:
    total, valid = 0, 0
    errors = []
    print(f"\n### Testing variant: {variant}")

    # Read all lines first to get count
    with open(cfg["dataset"]) as f:
        lines = [line for i, line in enumerate(f) if i < cfg["sample_limit"]]
    
    # Process with progress bar
    for line in tqdm(lines, desc=f"  {variant}", unit="sample"):
        row = json.loads(line)
        msgs = VARIANTS[variant](
            row["task_description"],
            row["schema"],
            row["example_input"]
        )

        try:
            output = client.chat(msgs)
            ok, err, extraneous_pct, json_len, orig_len = validate_json(output, row["schema"])
            total += 1
            
            # Store detailed result
            detailed_results.append({
                "variant": variant,
                "sample_id": total,
                "task_description": row["task_description"],
                "valid": ok,
                "error": err if not ok else "",
                "extraneous_text_pct": extraneous_pct,
                "json_length": json_len,
                "original_length": orig_len,
                "output": output[:500] if len(output) > 500 else output  # Truncate long outputs
            })
            
            if ok: 
                valid += 1
            else:
                errors.append({
                    "sample": total,
                    "error": err,
                    "extraneous_pct": extraneous_pct,
                    "output_preview": output[:200]
                })
            
            # Small delay to avoid rate limiting (0.1s = ~10 req/sec)
            time.sleep(0.1)
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate limit" in error_msg.lower():
                print(f"\n⚠️  Rate limit hit! Waiting 60 seconds...")
                time.sleep(60)
                # Retry once
                try:
                    output = client.chat(msgs)
                    ok, err, extraneous_pct, json_len, orig_len = validate_json(output, row["schema"])
                    total += 1
                    detailed_results.append({
                        "variant": variant,
                        "sample_id": total,
                        "task_description": row["task_description"],
                        "valid": ok,
                        "error": err if not ok else "",
                        "extraneous_text_pct": extraneous_pct,
                        "json_length": json_len,
                        "original_length": orig_len,
                        "output": output[:500]
                    })
                    if ok: valid += 1
                    time.sleep(0.1)
                except Exception as retry_err:
                    errors.append({
                        "sample": total+1,
                        "error": f"Retry failed: {str(retry_err)[:100]}",
                        "extraneous_pct": 0,
                        "output_preview": ""
                    })
            else:
                errors.append({
                    "sample": total+1,
                    "error": error_msg[:100],
                    "extraneous_pct": 0,
                    "output_preview": ""
                })
            continue

    if total > 0:
        # Calculate average extraneous text percentage
        variant_results = [r for r in detailed_results if r["variant"] == variant]
        avg_extraneous = sum(r["extraneous_text_pct"] for r in variant_results) / len(variant_results) if variant_results else 0
        
        result = {
            "valid": valid,
            "total": total,
            "percentage": valid/total * 100,
            "avg_extraneous_text_pct": avg_extraneous,
            "errors": errors[:10]  # Store first 10 errors
        }
        results[variant] = result
        print(f"  ✅ {variant}: {valid}/{total} valid ({valid/total * 100:.1f}%)")
        print(f"  📊 Avg extraneous text: {avg_extraneous:.2f}%")
        if errors:
            print(f"  ⚠️  {len(errors)} errors encountered")
            if len(errors) <= 5:
                for err in errors:
                    print(f"     Sample {err['sample']}: {err['error'][:80]}")
    else:
        print(f"  ⚠️  {variant}: No successful API calls (all failed)")

# Final summary
print("\n" + "="*50)
print("FINAL RESULTS")
print("="*50)
print(f"{'Variant':<30} {'Valid/Total':<15} {'Success %':<12} {'Avg Extraneous %':<18}")
print("-" * 75)
for variant, result in results.items():
    print(f"{variant:<30} {result['valid']:3d}/{result['total']:<11} {result['percentage']:>5.1f}%      {result['avg_extraneous_text_pct']:>5.2f}%")

# Save detailed results to JSON
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
results_file = f"results_exp1_{timestamp}.json"
with open(results_file, "w") as f:
    json.dump({
        "experiment": "Experiment 1: Prompt Adherence",
        "model": cfg["model"],
        "variants": cfg["variants"],
        "sample_limit": cfg["sample_limit"],
        "timestamp": timestamp,
        "summary": results,
        "detailed_results": detailed_results
    }, f, indent=2)

print(f"\n💾 Detailed results saved to: {results_file}")
print(f"   Total samples: {len(detailed_results)}")
