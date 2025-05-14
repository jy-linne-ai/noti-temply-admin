import re
from typing import Any, Type, Union

from jinja2schema.model import Boolean, Dictionary, List, Number, Scalar, Tuple, Variable
from pydantic import BaseModel, Field, create_model

from .model import AdditionalProperties, AnyOf, Integer


def remove_namespace(ref: str) -> str:
    """Dynamically removes namespace from schema reference.

    Args:
        ref: The reference string containing namespace.

    Returns:
        str: The reference string with namespace removed.
    """
    # print(f"[remove_namespace] input: {ref}")
    # Return only the part after .schema.
    if __name__ in ref:
        result = ref.split(__name__, 1)[1].lstrip(".")
        # print(f"[remove_namespace] {__name__} found, result: {result}")
        return result

    # print(f"[remove_namespace] no change, result: {ref}")
    return ref


def normalize_ref(ref: str) -> str:
    """Normalizes reference string by removing IDs and namespaces.

    Args:
        ref: The reference string to normalize.

    Returns:
        str: The normalized reference string.

    Examples:
        >>> normalize_ref("app.utils.temply.schema.user:123")
        'user'
        >>> normalize_ref("app.utils.temply.schema.order.items:456")
        'order.items'
    """
    # print(f"[normalize_ref] input: {ref}")
    # Remove ID
    components = re.split(r"([\][,])", ref)
    components = [x.split(":")[0] for x in components]
    ref_no_id = "".join(components)
    # print(f"[normalize_ref] after id remove: {ref_no_id}")
    # Remove namespace
    result = remove_namespace(ref_no_id)
    # print(f"[normalize_ref] after remove_namespace: {result}")
    return result


def get_mode_title(mode: str) -> str:
    """Returns title based on mode.

    Args:
        mode: The mode string ('input' or 'output').

    Returns:
        str: The title corresponding to the mode.

    Examples:
        >>> get_mode_title("input")
        'Input'
        >>> get_mode_title("output")
        'Output'
    """
    return "Input" if mode == "input" else "Output"


def variable_to_type(variable: Variable, namespaces: list[str]) -> object:
    if isinstance(variable, Dictionary):
        return dict_to_model(variable, namespaces)
    if isinstance(variable, AdditionalProperties):
        t = variable_to_type(variable.item, namespaces + ["additionalProperties"])
        return dict[str, t]  # type: ignore
    if isinstance(variable, List):
        t = list[variable_to_type(variable.item, namespaces)]  # type: ignore
        return t
    if isinstance(variable, AnyOf):
        types = tuple(
            variable_to_type(item, namespaces + [f"anyOf.{idx}"])
            for idx, item in enumerate(variable.items)
        )
        return Union[types]  # type: ignore[unused-ignore]
    if isinstance(variable, Tuple):
        types = tuple(
            variable_to_type(item, namespaces + [f"items.{idx}"])
            for idx, item in enumerate(variable.items)
        )
        return tuple[types]  # type: ignore
    if isinstance(variable, Boolean):
        return bool
    if isinstance(variable, Integer):
        return int
    if isinstance(variable, Number):
        return float
    if isinstance(variable, Scalar):
        return str
    return Any


def dict_to_model(dictionary: Dictionary, namespaces: list[str]) -> Type[BaseModel]:
    fields: dict[str, Any] = {}
    for k, v in sorted(dictionary.items()):
        if v.required:
            fields[k] = (variable_to_type(v, namespaces + [k]), ...)
        else:
            fields[k] = (
                variable_to_type(v, namespaces + [k]),
                Field(default_factory=lambda: None),
            )
    return create_model(".".join(namespaces), **fields)
