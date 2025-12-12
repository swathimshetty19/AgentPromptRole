"""
Generate dataset for Experiment 3: Agentic Decision-Making with Long Context

Creates tasks with:
- Multiple steps/tool calls (history)
- Long context (previous outputs)
- Final decision/question requiring context retention
- Expected answer for validation
"""

import json
import random

# Task templates for agentic decision-making
TASK_TEMPLATES = [
    {
        "task_type": "data_analysis",
        "task_description": "You are a data analyst. Analyze the provided information and answer questions based on your previous findings.",
        "scenarios": [
            {
                "history": [
                    {"user_query": "What is the total sales for Q1?", "assistant_output": "Q1 total sales: $125,000"},
                    {"user_query": "What is the total sales for Q2?", "assistant_output": "Q2 total sales: $145,000"},
                    {"user_query": "What is the total sales for Q3?", "assistant_output": "Q3 total sales: $138,000"},
                ],
                "current_query": "What is the average quarterly sales?",
                "expected_answer": "$136,000",
                "context_length": "medium"
            },
            {
                "history": [
                    {"user_query": "Find the top 3 products by revenue", "assistant_output": "Top 3 products: Product A ($50k), Product B ($45k), Product C ($40k)"},
                    {"user_query": "What is the total revenue of these top 3?", "assistant_output": "Total revenue of top 3: $135,000"},
                    {"user_query": "What percentage does Product A represent?", "assistant_output": "Product A represents 37.0% of the top 3 revenue"},
                ],
                "current_query": "If Product A's revenue increases by 20%, what will be the new total for top 3?",
                "expected_answer": "$145,000",
                "context_length": "medium"
            }
        ]
    },
    {
        "task_type": "code_review",
        "task_description": "You are a code reviewer. Review code changes and answer questions about the codebase.",
        "scenarios": [
            {
                "history": [
                    {"user_query": "Review function calculate_total()", "assistant_output": "Found: calculate_total() uses sum() correctly, returns float"},
                    {"user_query": "Review function validate_input()", "assistant_output": "Found: validate_input() checks for None and empty strings"},
                    {"user_query": "Review function process_data()", "assistant_output": "Found: process_data() calls calculate_total() and validate_input()"},
                ],
                "current_query": "Which function is called by process_data()?",
                "expected_answer": "calculate_total() and validate_input()",
                "context_length": "medium"
            }
        ]
    },
    {
        "task_type": "research_assistant",
        "task_description": "You are a research assistant. Gather information and synthesize findings.",
        "scenarios": [
            {
                "history": [
                    {"user_query": "Find papers on transformer architectures", "assistant_output": "Found 5 papers: Attention Is All You Need (2017), BERT (2018), GPT-3 (2020), T5 (2020), GPT-4 (2023)"},
                    {"user_query": "Which paper introduced the transformer?", "assistant_output": "Attention Is All You Need (2017) introduced the transformer architecture"},
                    {"user_query": "What year was GPT-3 published?", "assistant_output": "GPT-3 was published in 2020"},
                ],
                "current_query": "How many years passed between the transformer paper and GPT-3?",
                "expected_answer": "3 years",
                "context_length": "medium"
            },
            {
                "history": [
                    {"user_query": "Search for information about climate change impacts", "assistant_output": "Found: Global temperature rise of 1.1°C since pre-industrial era, sea level rise of 20cm"},
                    {"user_query": "What are the main causes?", "assistant_output": "Main causes: CO2 emissions (76%), methane (16%), other greenhouse gases (8%)"},
                    {"user_query": "What is the largest contributor?", "assistant_output": "CO2 emissions are the largest contributor at 76%"},
                ],
                "current_query": "If CO2 emissions are reduced by 50%, what percentage of total greenhouse gases would they represent?",
                "expected_answer": "38%",
                "context_length": "medium"
            }
        ]
    },
    {
        "task_type": "multi_step_reasoning",
        "task_description": "You are solving a multi-step reasoning problem. Use information from previous steps.",
        "scenarios": [
            {
                "history": [
                    {"user_query": "Step 1: Calculate 15 * 8", "assistant_output": "15 * 8 = 120"},
                    {"user_query": "Step 2: Add 45 to the result", "assistant_output": "120 + 45 = 165"},
                    {"user_query": "Step 3: Divide by 3", "assistant_output": "165 / 3 = 55"},
                ],
                "current_query": "What was the original number multiplied by 8 in Step 1?",
                "expected_answer": "15",
                "context_length": "short"
            },
            {
                "history": [
                    {"user_query": "Find the population of New York", "assistant_output": "New York population: 8.5 million"},
                    {"user_query": "Find the population of Los Angeles", "assistant_output": "Los Angeles population: 4.0 million"},
                    {"user_query": "Find the population of Chicago", "assistant_output": "Chicago population: 2.7 million"},
                ],
                "current_query": "What is the combined population of all three cities?",
                "expected_answer": "15.2 million",
                "context_length": "short"
            }
        ]
    },
    {
        "task_type": "tool_use_tracking",
        "task_description": "You are using various tools. Track your tool calls and answer based on results.",
        "scenarios": [
            {
                "history": [
                    {"user_query": "Use search tool: 'weather in NYC'", "assistant_output": "Tool result: Temperature 72°F, Sunny, Humidity 65%"},
                    {"user_query": "Use calculator: 72 * 1.8 + 32", "assistant_output": "Tool result: 161.6"},
                    {"user_query": "Use search tool: 'convert 72F to Celsius'", "assistant_output": "Tool result: 72°F = 22.2°C"},
                ],
                "current_query": "What was the temperature in Celsius from the first search?",
                "expected_answer": "22.2°C",
                "context_length": "medium"
            }
        ]
    }
]

def generate_agentic_dataset(num_samples=50, output_file="./datasets/agentic_tasks.jsonl"):
    """Generate agentic decision-making tasks with long context"""
    samples = []
    
    for i in range(num_samples):
        # Pick a random task type and scenario
        task_template = random.choice(TASK_TEMPLATES)
        scenario = random.choice(task_template["scenarios"])
        
        # Create sample
        sample = {
            "task_id": f"agentic_{i+1:03d}",
            "task_type": task_template["task_type"],
            "task_description": task_template["task_description"],
            "history": scenario["history"],
            "current_query": scenario["current_query"],
            "expected_answer": scenario["expected_answer"],
            "context_length": scenario.get("context_length", "medium"),
            "num_history_steps": len(scenario["history"])
        }
        
        samples.append(sample)
    
    # Write to JSONL
    with open(output_file, "w") as f:
        for sample in samples:
            f.write(json.dumps(sample) + "\n")
    
    print(f"✅ Generated {num_samples} agentic tasks")
    print(f"💾 Saved to: {output_file}")
    
    # Print distribution
    task_type_counts = {}
    for sample in samples:
        task_type = sample["task_type"]
        task_type_counts[task_type] = task_type_counts.get(task_type, 0) + 1
    
    print("\n📊 Task type distribution:")
    for task_type, count in task_type_counts.items():
        print(f"   {task_type}: {count}")

if __name__ == "__main__":
    import sys
    num_samples = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    generate_agentic_dataset(num_samples)

