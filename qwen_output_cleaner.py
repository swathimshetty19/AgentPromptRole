import json
import re
from typing import Any, Dict, Optional

def extract_parameters_from_qwen_output(output: str) -> str:
    """
    Extract the actual parameters from Qwen's tool-wrapped output.
    
    Qwen sometimes wraps the output in:
    {
        "tool_name": "ToolName",
        "parameters": {
            ... actual parameters ...
        }
    }
    
    This function extracts just the parameters part.
    """
    if not output:
        return output
    
    try:
        # First try to parse as JSON
        data = json.loads(output)
        
        # Check if it has the Qwen wrapper structure
        if isinstance(data, dict) and "parameters" in data:
            # Extract just the parameters
            parameters = data["parameters"]
            # Return as JSON string
            return json.dumps(parameters)
        
        # If it doesn't have the wrapper, return as-is
        return output
        
    except (json.JSONDecodeError, TypeError):
        # If it's not valid JSON, return as-is
        return output


def clean_qwen_output(output: str) -> str:
    """
    Clean Qwen's output to match expected format.
    Handles multiple possible wrapper formats.
    """
    if not output:
        return output
    
    # Remove markdown code blocks if present
    cleaned = output.strip()
    cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'\n?```\s*$', '', cleaned, flags=re.MULTILINE)
    
    try:
        # Parse the JSON
        data = json.loads(cleaned)
        
        # Handle different wrapper formats Qwen might use
        if isinstance(data, dict):
            # Case 1: {"tool_name": "X", "parameters": {...}}
            if "parameters" in data and "tool_name" in data:
                return json.dumps(data["parameters"])
            
            # Case 2: {"name": "X", "arguments": {...}}
            elif "arguments" in data and "name" in data:
                return json.dumps(data["arguments"])
            
            # Case 3: {"function": {"name": "X", "arguments": {...}}}
            elif "function" in data and isinstance(data["function"], dict):
                if "arguments" in data["function"]:
                    return json.dumps(data["function"]["arguments"])
            
            # Case 4: Already in correct format
            else:
                return json.dumps(data)
        
        # If it's not a dict, return as-is
        return json.dumps(data)
        
    except (json.JSONDecodeError, TypeError):
        # If we can't parse it, return original
        return output


def preprocess_qwen_output_for_validation(output: str, expected_schema: Dict[str, Any]) -> str:
    """
    Preprocess Qwen's output before validation.
    
    Args:
        output: Raw output from Qwen
        expected_schema: The expected schema (can be used to determine what fields to extract)
    
    Returns:
        Cleaned output ready for validation
    """
    # First clean the output
    cleaned = clean_qwen_output(output)
    
    # Optional: Additional validation-specific cleaning
    try:
        data = json.loads(cleaned)
        
        # If the schema expects specific fields, ensure they're at the top level
        if "required_parameters" in expected_schema:
            required_fields = {param["name"] for param in expected_schema["required_parameters"]}
            
            # Check if all required fields are present at top level
            if isinstance(data, dict):
                missing_fields = required_fields - set(data.keys())
                if missing_fields:
                    # Try to find them nested
                    for key, value in data.items():
                        if isinstance(value, dict):
                            for field in missing_fields.copy():
                                if field in value:
                                    data[field] = value[field]
                                    missing_fields.remove(field)
        
        return json.dumps(data)
        
    except:
        return cleaned


# Integration with your validator
def validate_with_qwen_preprocessing(output: str, schema: Dict[str, Any]) -> Any:
    """
    Wrapper for your existing validator that preprocesses Qwen output.
    """
    # Import your existing validator
    from experiments.validators.json_validator import validate_json_with_pydantic
    
    # Preprocess the output
    cleaned_output = clean_qwen_output(output)
    
    # Run validation on cleaned output
    return validate_json_with_pydantic(cleaned_output, schema)


# Example usage in your pipeline
def modified_call_model_with_retry(client, messages, builder_name=None):
    """
    Modified version that cleans Qwen output for specific builders.
    """
    output = client.chat(messages)
    
    # Clean output for builders that tend to get wrapped
    if builder_name and "assistant" in builder_name.lower():
        output = clean_qwen_output(output)
    
    return output
