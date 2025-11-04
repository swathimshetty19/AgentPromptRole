# Experiment 1: Prompt Adherence Analysis

## Current Results

| Variant | Valid/Total | Success Rate |
|---------|------------|--------------|
| `user_only` | 200/200 | 100.0% |
| `system_plus_user` | 200/200 | 100.0% |
| `user_plus_assistant_seed` | 198/200 | 99.0% |

## Key Findings

### 1. **Role Structure Has Minimal Impact on Simple Tasks**
- All three variants achieved >99% adherence
- System messages don't provide advantage over user-only for simple JSON extraction
- Suggests role structure matters more for complex/adversarial scenarios

### 2. **Assistant Seeding is Slightly Less Reliable**
- 2 failures in `user_plus_assistant_seed` variant
- Seed `"{"` can interfere if model doesn't complete correctly
- Needs investigation: what were the failure modes?

### 3. **Baseline Established**
- Strong baseline for Experiment 1
- Can compare against adversarial scenarios (Experiment 2)
- Can test with more complex schemas/long contexts (Experiments 2 & 3)

## Limitations of Current Experiment

1. **Task Complexity**: Only simple JSON extraction (3-4 fields)
2. **Schema Diversity**: Limited to 3 schema types (user profile, logs, products)
3. **No Adversarial Testing**: All prompts are benign
4. **Single Model**: Only tested `gpt-4.1-mini`
5. **No Error Analysis**: Don't know why the 2 failures occurred

## Recommendations for Experiment 1 Expansion

### 1. **Investigate Failure Cases**
- Capture and analyze the 2 failures in `user_plus_assistant_seed`
- Understand failure patterns

### 2. **Add More Complex Schemas**
- Nested objects
- Arrays with constraints
- Conditional schemas (if/then)
- Union types

### 3. **Test Multiple Models**
- LLaMA, Qwen, Mistral, DeepSeek (as per research plan)
- Compare role sensitivity across models

### 4. **Add Metrics Beyond Validation**
- Extraneous text percentage (as mentioned in research plan)
- Pydantic error rate breakdown
- Response time analysis

### 5. **ToolBench Integration**
- Test with ToolBench's structured tool-call schemas
- Multi-turn scenarios
- More realistic real-world conditions

## Bridge to Experiment 2 (Adversarial Robustness)

The current results show **baseline adherence is high**. This is important because:
- Experiment 2 will test if role structure helps resist adversarial prompts
- If system messages don't help with simple tasks, will they help with adversarial ones?
- Hypothesis: System messages may provide better resistance to "ignore all previous instructions" attacks

### Preparation for Experiment 2:
1. Use PromptRobust dataset (4,788 adversarial prompts)
2. Test same variants but with adversarial user inputs
3. Measure attack success rate vs. safe completion rate
4. Compare: does `system_plus_user` resist attacks better than `user_only`?

## Bridge to Experiment 3 (Decision-Making in Long Context)

Current experiment doesn't test long contexts. For Experiment 3:
1. Test with LongBench / L-Eval datasets
2. Compare System summaries vs. Assistant chains
3. Measure task accuracy and step efficiency
4. Test ToolBench history encoding

## Conclusions

**For simple prompt adherence**: Role structure has minimal impact. However, this establishes a strong baseline that will be valuable when testing:
- Adversarial robustness (Experiment 2)
- Long-context decision-making (Experiment 3)

**Next Steps**:
1. Expand Experiment 1 with more complex schemas and multiple models
2. Proceed to Experiment 2 (adversarial testing) - this is where role structure likely matters more
3. Prepare Experiment 3 infrastructure for long-context evaluation

