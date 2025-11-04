# Experiment 1: Prompt Adherence - Summary & Results

## Research Question Component
**"To what extent do LLM message roles (System, User, Assistant) affect the LLM's prompt adherence?"**

## Experimental Setup

### Variants Tested
1. **`user_only`**: All instructions in a single user message
2. **`system_plus_user`**: Instructions split between system (JSON constraint) and user (task details)
3. **`user_plus_assistant_seed`**: User message with instructions, assistant message starting with `"{"`

### Dataset
- 200 samples across 3 task types:
  - User profile extraction
  - Log entry normalization
  - Product info conversion
- All tasks require JSON schema adherence

### Model
- `openai/gpt-4.1-mini` (via OpenRouter)

## Results

| Variant | Valid/Total | Success Rate | Avg Extraneous Text % |
|---------|------------|--------------|----------------------|
| `user_only` | 200/200 | **100.0%** | TBD (run with enhanced metrics) |
| `system_plus_user` | 200/200 | **100.0%** | TBD |
| `user_plus_assistant_seed` | 198/200 | **99.0%** | TBD |

### Key Findings

1. **Role structure has minimal impact on simple prompt adherence**
   - All variants achieved >99% success
   - System messages don't provide advantage for simple JSON extraction tasks
   - Suggests role structure matters more for complex/adversarial scenarios

2. **Assistant seeding is slightly less reliable**
   - 2 failures in `user_plus_assistant_seed` variant
   - Need to investigate failure cases

3. **Strong baseline established**
   - High adherence across all variants
   - Good foundation for comparison with more complex scenarios

## Enhanced Metrics (Now Available)

The evaluation script has been enhanced to capture:

1. **Extraneous Text Percentage** ✅
   - Measures text outside the JSON structure
   - Aligns with research plan requirement

2. **Detailed Error Tracking** ✅
   - Captures specific validation errors
   - Pydantic-style error reporting

3. **Full Results Export** ✅
   - JSON export with all sample-level data
   - Enables deeper analysis

## Next Steps for Experiment 1

### Immediate Actions
1. **Re-run experiment** with enhanced metrics to get extraneous text percentages
2. **Investigate the 2 failures** in `user_plus_assistant_seed` variant
3. **Analyze error patterns** if any emerge

### Expansion Options
1. **Test more complex schemas**
   - Nested objects
   - Arrays with constraints
   - Conditional schemas (if/then)
   - Union types

2. **Test multiple models** (as per research plan)
   - LLaMA, Qwen, Mistral, DeepSeek
   - Compare role sensitivity across models

3. **Integrate ToolBench**
   - Structured tool-call schemas
   - Multi-turn scenarios
   - More realistic real-world conditions

## Files Generated

- `results_exp1_YYYYMMDD_HHMMSS.json`: Complete results with all metrics
- Contains:
  - Summary statistics per variant
  - Detailed per-sample results
  - Error details
  - Extraneous text measurements

## Conclusion

Experiment 1 establishes that for **simple, well-specified JSON schema tasks**, message role structure has minimal impact on prompt adherence. All variants perform excellently (>99%), suggesting that:

- Role structure differences will be more apparent in:
  - Complex schemas
  - Adversarial scenarios (Experiment 2 by other team members)
  - Long-context decision-making (Experiment 3 by other team members)

- The current results provide a strong baseline for understanding when role structure matters and when it doesn't.

