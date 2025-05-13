"""Template generation utilities.

This module provides utilities for generating random data based on JSON schemas
and handling variable merging in template contexts.
"""

from typing import Any, Dict, List

from faker import Faker
from jinja2schema.model import Variable  # type: ignore

fake = Faker()


def merge_checked(fst: Variable, snd: Variable, result: Variable) -> Variable:
    """Merges checked state from first variable to result.

    Args:
        fst: First variable to check.
        snd: Second variable (unused).
        result: Result variable to update.

    Returns:
        Variable: Updated result variable.
    """
    # If the `fst` is checked as defined, then the result is checked as defined
    if fst.checked_as_defined:
        result.checked_as_defined = True
    return result


def _generate_value_for_type(type_info: Dict[str, Any]) -> Any:
    """Generates appropriate random value based on type information."""
    if "type" not in type_info:
        return None

    type_name = type_info["type"]
    title = type_info.get("title", "").lower()

    if type_name == "string":
        if "name" in title:
            return fake.name()
        elif "email" in title:
            return fake.email()
        elif "phone" in title:
            return fake.phone_number()
        elif "url" in title:
            return fake.url()
        elif "address" in title or "addr" in title:
            return fake.address()
        elif "date" in title:
            return fake.date()
        elif "time" in title:
            return fake.time()
        elif "company" in title:
            return fake.company()
        elif "job" in title:
            return fake.job()
        elif "code" in title:
            return fake.uuid4()
        elif "id" in title:
            return fake.uuid4()
        elif "memo" in title or "notice" in title or "message" in title:
            return fake.text()
        return fake.word()

    elif type_name == "boolean":
        return fake.boolean()

    elif type_name == "number":
        return fake.random_number()

    elif type_name == "integer":
        if "quantity" in title:
            return fake.random_int(min=1, max=10)
        elif "price" in title:
            return fake.random_int(min=1000, max=1000000)
        return fake.random_int()

    return None


def generate_array(
    schema: Dict[str, Any], root_schema: Dict[str, Any] | None = None
) -> List[Dict[str, Any]]:
    """Generates array data according to schema."""
    items = schema.get("items", {})
    return [generate_object(items, root_schema) for _ in range(2)]


def generate_object(schema: Dict[str, Any], root_schema: Dict[str, Any] | None = None) -> Any:
    """Generates object data according to schema."""
    # Use current schema if root_schema is not provided
    if root_schema is None:
        root_schema = schema

    # Handle $ref
    if "$ref" in schema:
        ref_path = schema["$ref"].split("/")[1:]
        current = root_schema
        for part in ref_path:
            if part not in current:
                raise ValueError(f"Reference path not found: {part}")
            current = current[part]
        return generate_object(current, root_schema)

    # Handle array type
    if schema.get("type") == "array":
        return generate_array(schema, root_schema)

    # Handle object type
    if schema.get("type") == "object":
        result = {}
        if "properties" in schema:
            required_fields = schema.get("required", [])
            for prop_name, prop_schema in schema["properties"].items():
                if prop_name in required_fields:
                    result[prop_name] = generate_object(prop_schema, root_schema)
        return result

    # Handle primitive types
    return _generate_value_for_type(schema)
