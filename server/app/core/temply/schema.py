from typing import Any, Type, Union

from jinja2schema.model import Boolean, Dictionary, List, Number, Scalar, Tuple, Variable
from pydantic import BaseModel, Field, create_model

from .model import AdditionalProperties, AnyOf, Integer


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
