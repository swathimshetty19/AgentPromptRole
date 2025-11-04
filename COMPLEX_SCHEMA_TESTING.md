# Complex Schema Testing - Experiment 1 Expansion

## Overview

Extended Experiment 1 to test **complex schemas** to determine if message role structure has more impact when schemas are more complex.

## Complex Schema Types Tested

### 1. **Nested Objects**
- User profiles with nested address objects
- Location data with nested venue information
- Transaction data with nested sender/receiver objects

**Example Schema**:
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "address": {
      "type": "object",
      "properties": {
        "street": {"type": "string"},
        "city": {"type": "string"},
        "zipcode": {"type": "string"}
      }
    }
  }
}
```

### 2. **Arrays with Constraints**
- Product catalogs with arrays of products
- Order items with arrays of ordered items
- Event attendees as arrays
- Transaction metadata as arrays

**Example Schema**:
```json
{
  "type": "object",
  "properties": {
    "products": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "price": {"type": "number"}
        }
      }
    }
  }
}
```

### 3. **Nested Arrays**
- Orders with customer objects and items arrays
- Events with location objects and attendees arrays
- User profiles with hobbies arrays and preferences objects

**Example Schema**:
```json
{
  "type": "object",
  "properties": {
    "order_id": {"type": "string"},
    "customer": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "email": {"type": "string"}
      }
    },
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "product": {"type": "string"},
          "quantity": {"type": "integer"}
        }
      },
      "minItems": 1
    }
  }
}
```

### 4. **Conditional Schemas** (if/then)
- Server/client configurations with conditional properties
- Different required fields based on type

**Example Schema**:
```json
{
  "type": "object",
  "properties": {
    "type": {"type": "string", "enum": ["server", "client"]},
    "host": {"type": "string"},
    "port": {"type": "integer"}
  },
  "if": {"properties": {"type": {"const": "server"}}},
  "then": {
    "properties": {"max_connections": {"type": "integer"}},
    "required": ["max_connections"]
  }
}
```

### 5. **Union Types** (oneOf)
- API responses with error or success variants
- Different structures based on status

**Example Schema**:
```json
{
  "oneOf": [
    {
      "type": "object",
      "properties": {
        "status": {"type": "string", "const": "error"},
        "error": {
          "type": "object",
          "properties": {
            "code": {"type": "integer"},
            "message": {"type": "string"}
          }
        }
      }
    },
    {
      "type": "object",
      "properties": {
        "status": {"type": "string", "const": "success"},
        "data": {
          "type": "object",
          "properties": {
            "id": {"type": "string"},
            "value": {"type": "number"}
          }
        }
      }
    }
  ]
}
```

## Dataset

- **File**: `datasets/complex_schema_tasks_100.jsonl`
- **Samples**: 100 samples across 7 complex schema templates
- **Generation**: `datasets/generate_complex_dataset.py`

## Experiment Setup

- **Config**: `configs/exp1_complex.yaml`
- **Script**: `eval_adherence_complex.py`
- **Model**: `openai/gpt-4.1-mini`
- **Variants**: Same 3 variants as simple schema test
  - `user_only`
  - `system_plus_user`
  - `user_plus_assistant_seed`
- **Samples**: 100 (all samples in dataset)

## Running the Experiment

```bash
# Generate complex schema dataset (if needed)
cd datasets
python3 generate_complex_dataset.py

# Run complex schema experiment
cd ..
python3 eval_adherence_complex.py
```

## Expected Insights

### Research Questions
1. **Do complex schemas reduce adherence rates?**
   - If yes: Role structure may matter more for complex tasks
   - If no: Models handle complexity well regardless of role structure

2. **Does role structure have more impact with complex schemas?**
   - Compare simple vs complex results
   - Check if differences between variants are larger

3. **Which schema types are hardest?**
   - Conditional (if/then) schemas
   - Union types (oneOf)
   - Deeply nested structures

## Comparison Tool

After running both experiments, use:
```bash
python3 compare_simple_vs_complex.py
```

This will:
- Compare success rates across variants
- Show extraneous text differences
- Break down results by schema type
- Provide key insights on role structure impact

## Results Files

- Simple schemas: `results_exp1_YYYYMMDD_HHMMSS.json`
- Complex schemas: `results_exp1_complex_YYYYMMDD_HHMMSS.json`

Both files include:
- Summary statistics per variant
- Schema type breakdown (complex only)
- Detailed per-sample results
- Error analysis

## Next Steps

1. **Run the complex schema experiment** (currently running or completed)
2. **Compare results** using `compare_simple_vs_complex.py`
3. **Analyze failures** by schema type to identify patterns
4. **Document findings** on whether role structure matters more with complexity

