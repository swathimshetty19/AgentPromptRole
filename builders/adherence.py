import json

def user_only(task, schema, text):
    schema_str = json.dumps(schema, indent=2) if isinstance(schema, dict) else str(schema)
    return [
        {
            "role": "user",
            "content": f"{task}\nYour output must be valid JSON:\n{schema_str}\nInput: {text}\nOnly return JSON."
        }
    ]

def system_plus_user(task, schema, text):
    schema_str = json.dumps(schema, indent=2) if isinstance(schema, dict) else str(schema)
    return [
        {"role": "system", "content": f"You only output JSON. Schema:\n{schema_str}"},
        {"role": "user", "content": f"{task}\nInput: {text}\nReturn JSON only."}
    ]

def user_plus_assistant_seed(task, schema, text):
    schema_str = json.dumps(schema, indent=2) if isinstance(schema, dict) else str(schema)
    return [
        {"role": "user", "content": f"{task}\nSchema:\n{schema_str}\nInput: {text}\nOnly JSON."},
        {"role": "assistant", "content": "{"}
    ]

VARIANTS = {
    "user_only": user_only,
    "system_plus_user": system_plus_user,
    "user_plus_assistant_seed": user_plus_assistant_seed,
}
