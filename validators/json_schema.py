import json, jsonschema
import re

def validate_json(output, schema):
    """
    Validates JSON output against schema and measures extraneous text.
    Returns: (is_valid, error_message, extraneous_text_percentage, cleaned_json_length, original_length)
    """
    original_length = len(output)
    original_cleaned = output.strip()
    
    try:
        # Remove markdown fences if present (handle multiline code blocks)
        cleaned = original_cleaned
        # Remove ```json or ``` at start and end of lines
        cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'\n?```\s*$', '', cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()
        
        # Also handle single-line cases
        if cleaned.startswith('```'):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
        if cleaned.endswith('```'):
            cleaned = re.sub(r'\s*```$', '', cleaned)
        cleaned = cleaned.strip()
        
        # Find JSON boundaries (first { to last })
        json_start = cleaned.find('{')
        json_end = cleaned.rfind('}')
        
        if json_start == -1 or json_end == -1 or json_end <= json_start:
            # Try to find array boundaries
            json_start = cleaned.find('[')
            json_end = cleaned.rfind(']')
            if json_start == -1 or json_end == -1 or json_end <= json_start:
                raise ValueError("No valid JSON structure found")
        
        # Extract just the JSON part
        json_only = cleaned[json_start:json_end+1]
        
        # Calculate extraneous text percentage
        text_before = cleaned[:json_start].strip()
        text_after = cleaned[json_end+1:].strip()
        extraneous_chars = len(text_before) + len(text_after)
        extraneous_pct = (extraneous_chars / original_length * 100) if original_length > 0 else 0
        
        # Parse JSON
        data = json.loads(json_only)

        # Validate schema
        jsonschema.validate(data, schema)
        return True, "", extraneous_pct, len(json_only), original_length
    except Exception as e:
        # Calculate extraneous text even for invalid JSON
        extraneous_pct = 0
        try:
            # Try to find any JSON-like structure in the cleaned output
            json_start = cleaned.find('{')
            if json_start == -1:
                json_start = cleaned.find('[')
            if json_start != -1:
                json_end = cleaned.rfind('}')
                if json_end <= json_start:
                    json_end = cleaned.rfind(']')
                if json_end > json_start:
                    extraneous_chars = len(cleaned[:json_start].strip()) + len(cleaned[json_end+1:].strip())
                    extraneous_pct = (extraneous_chars / original_length * 100) if original_length > 0 else 100
                else:
                    extraneous_pct = 100  # No valid JSON found
            else:
                extraneous_pct = 100  # No JSON structure found
        except:
            extraneous_pct = 100  # If we can't parse, assume all text is extraneous
        
        return False, str(e), extraneous_pct, 0, original_length
