"""Variable merging utilities.

This module provides functionality for merging variables in template contexts,
handling different types of variables and their properties.
"""

import itertools
import json
from typing import Callable, Optional

from jinja2schema.exceptions import MergeException  # type: ignore
from jinja2schema.model import Dictionary, List, Scalar, Tuple, Unknown, Variable  # type: ignore
from pydantic import BaseModel, create_model

from .model import AdditionalProperties, AnyOf
from .schema import variable_to_type


def merge(
    fst: Variable,
    snd: Variable,
    custom_merger: Optional[Callable[[Variable, Variable, Variable], Variable]] = None,
) -> Variable:
    """Merges two variables with optional custom merger function.

    Args:
        fst: First variable to merge.
        snd: Second variable to merge.
        custom_merger: Optional custom merger function.

    Returns:
        Variable: Merged variable.

    Raises:
        MergeException: If variables cannot be merged.

    Examples:
        >>> merge(Scalar(), Scalar())
        <Scalar>
        >>> merge(Dictionary(), Dictionary())
        <Dictionary>
    """
    if isinstance(fst, Unknown):
        result = snd.clone()
    elif isinstance(snd, Unknown):
        result = fst.clone()
    elif isinstance(fst, Scalar) and isinstance(snd, Scalar):
        fst_type = type(fst)
        snd_type = type(snd)
        if issubclass(fst_type, snd_type):
            result = fst_type()
        elif issubclass(snd_type, fst_type):
            result = snd_type()
        else:
            raise MergeException(fst, snd)
    elif isinstance(fst, AdditionalProperties):
        if isinstance(snd, AdditionalProperties):
            result = AdditionalProperties(merge(fst.item, snd.item, custom_merger=custom_merger))
        elif isinstance(snd, Dictionary):
            result = snd.clone()
            # All items in fst are additional properties
            for _, v in result.items():
                v.checked_as_undefined = True
        else:
            raise MergeException(fst, snd)
    elif isinstance(snd, AdditionalProperties):
        return merge(snd, fst, custom_merger=custom_merger)
    elif isinstance(fst, AnyOf):
        if isinstance(snd, AnyOf):
            d = {}
            for item in *fst.items, *snd.items:
                d[variable2key(item)] = item
            result = AnyOf([v for _, v in sorted(d.items())])
        else:

            def mergable(item: Variable) -> bool:
                return merge(item, snd) == item  # type: ignore

            if all(map(mergable, fst.items)):
                result = fst.clone()
            else:
                # Remove duplicates
                items = list(
                    {
                        variable2key(item): item
                        for item in [
                            merge(item, snd, custom_merger=custom_merger) for item in fst.items
                        ]
                    }.values()
                )
                # Then if there is only one item, return it
                if len(items) == 1:
                    result = items[0]
                else:
                    result = AnyOf(items)

    elif isinstance(snd, AnyOf):
        return merge(snd, fst, custom_merger=custom_merger)
    elif isinstance(fst, Dictionary) and isinstance(snd, Dictionary):
        result = Dictionary()
        for k in set(itertools.chain(fst.iterkeys(), snd.iterkeys())):
            if k in fst and k in snd:
                result[k] = merge(fst[k], snd[k], custom_merger=custom_merger)
            elif k in fst:
                result[k] = fst[k].clone()
            elif k in snd:
                result[k] = snd[k].clone()
    elif isinstance(fst, List) and isinstance(snd, List):
        result = List(merge(fst.item, snd.item))
    elif isinstance(fst, Tuple) and isinstance(snd, Tuple):
        result = Tuple(
            [merge(fst_item, snd_item) for fst_item, snd_item in zip(fst.items, snd.items)]
        )
    else:
        raise MergeException(fst, snd)
    result.label = fst.label or snd.label
    result.linenos = list(sorted(set(fst.linenos + snd.linenos)))
    result.constant = fst.constant
    result.may_be_defined = fst.may_be_defined
    result.used_with_default = fst.used_with_default and snd.used_with_default
    result.checked_as_defined = fst.checked_as_defined and snd.checked_as_defined
    result.checked_as_undefined = fst.checked_as_undefined and snd.checked_as_undefined
    if fst.value == snd.value:
        result.value = fst.value
    result.order_nr = fst.order_nr
    if callable(custom_merger):
        result = custom_merger(fst, snd, result)
    return result


def merge_many(fst: Variable, snd: Variable, *args: Variable) -> Variable:
    """Merges multiple variables.

    Args:
        fst: First variable to merge.
        snd: Second variable to merge.
        *args: Additional variables to merge.

    Returns:
        Variable: Merged variable.

    Examples:
        >>> merge_many(Scalar(), Scalar(), Scalar())
        <Scalar>
    """
    struct = merge(fst, snd)
    if args:
        return merge_many(struct, *args)
    else:
        return struct


def merge_bool_expr_structs(fst: Variable, snd: Variable) -> Variable:
    """Merges boolean expression structures.

    Args:
        fst: First boolean expression structure.
        snd: Second boolean expression structure.

    Returns:
        Variable: Merged boolean expression structure.
    """

    def merger(fst: Variable, snd: Variable, result: Variable) -> Variable:
        result.checked_as_defined = fst.checked_as_defined
        result.checked_as_undefined = fst.checked_as_undefined and snd.checked_as_undefined
        return result

    return merge(fst, snd, custom_merger=merger)


def merge_rtypes(fst: Variable, snd: Variable, operator: Optional[str] = None) -> Variable:
    """Merges return types with optional operator.

    Args:
        fst: First return type.
        snd: Second return type.
        operator: Optional operator ('+' or '-').

    Returns:
        Variable: Merged return type.

    Raises:
        MergeException: If types cannot be merged with the given operator.
    """
    if operator in ("+", "-"):
        fst_type = type(fst)
        snd_type = type(snd)
        if (
            type(fst) is not type(snd)
            and not (isinstance(fst, Unknown) or isinstance(snd, Unknown))
            and not (issubclass(fst_type, snd_type) or issubclass(snd_type, fst_type))
        ):
            raise MergeException(fst, snd)
    return merge(fst, snd)


def variable2key(v: Variable) -> str:
    """Converts variable to key string.

    Args:
        v: Variable to convert.

    Returns:
        str: JSON string representation of the variable's schema.
    """
    model: type[BaseModel] = create_model(
        "Schema", __base__=variable_to_type(v, [])
    )  # type: ignore
    return json.dumps(model.model_json_schema(), sort_keys=True)
