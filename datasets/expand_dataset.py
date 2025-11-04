import json
import random

# Base templates for the 3 task types
templates = [
    {
        "task_description": "Extract a user profile from the text.",
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "email": {"type": "string"}
            },
            "required": ["name", "age", "email"]
        },
        "example_inputs": [
            "Mark Lee, 41, mark@work.io",
            "Sarah Johnson, 28, sarah.j@email.com",
            "John Smith, 35, johnsmith123@gmail.com",
            "Emily Davis, 22, emily.d@university.edu",
            "Michael Brown, 45, mike.brown@company.com",
            "Jessica Wilson, 31, jessica.w@mail.com",
            "David Miller, 52, david.m@business.org",
            "Lisa Anderson, 29, lisa.a@email.net",
            "Robert Taylor, 38, robert.t@work.com",
            "Amanda White, 26, amanda.w@email.com",
        ]
    },
    {
        "task_description": "Normalize a log entry.",
        "schema": {
            "type": "object",
            "properties": {
                "timestamp": {"type": "string"},
                "level": {"type": "string"},
                "message": {"type": "string"}
            },
            "required": ["timestamp", "level", "message"]
        },
        "example_inputs": [
            "2024-02-01 ERROR Disk full",
            "2024-03-15 WARNING Memory usage high",
            "2024-01-10 INFO Server started",
            "2024-04-22 ERROR Connection timeout",
            "2024-05-08 DEBUG Processing request",
            "2024-06-12 ERROR Database connection failed",
            "2024-07-20 WARNING CPU usage at 90%",
            "2024-08-05 INFO User logged in",
            "2024-09-15 ERROR File not found",
            "2024-10-30 DEBUG Cache cleared",
        ]
    },
    {
        "task_description": "Convert product info into structured JSON.",
        "schema": {
            "type": "object",
            "properties": {
                "product_name": {"type": "string"},
                "price": {"type": "number"},
                "currency": {"type": "string"}
            },
            "required": ["product_name", "price"]
        },
        "example_inputs": [
            "AirPods Pro, $249",
            "iPhone 15, $999",
            "MacBook Pro, $1999",
            "iPad Air, $599",
            "Apple Watch, $399",
            "Sony Headphones, $299",
            "Samsung TV, $1299",
            "Nintendo Switch, $299",
            "PlayStation 5, $499",
            "Xbox Series X, $499",
        ]
    }
]

# Generate 200 samples
samples = []
for i in range(200):
    template = random.choice(templates)
    example_input = random.choice(template["example_inputs"])
    
    sample = {
        "task_description": template["task_description"],
        "schema": template["schema"],
        "example_input": example_input
    }
    samples.append(sample)

# Write to file
output_file = "json_schema_tasks_1000.jsonl"
with open(output_file, "w") as f:
    for sample in samples:
        f.write(json.dumps(sample) + "\n")

print(f"✅ Generated {len(samples)} samples in {output_file}")

