"""Template parsing and schema generation module.

This module provides functionality for parsing Jinja2 templates and generating JSON schemas
from the parsed templates. It includes utilities for handling references, namespaces,
and schema generation.
"""

import re
from typing import Any, Union, get_origin

from jinja2 import Environment, nodes
from jinja2schema.model import Scalar, Unknown, Variable
from pydantic import BaseModel, RootModel, create_model
from pydantic.json_schema import CoreModeRef, DefsRef, GenerateJsonSchema
from typing_extensions import override

from .schema import variable_to_type
from .visitors.context import Context


def remove_namespace(ref: str) -> str:
    """Dynamically removes namespace from schema reference.

    Args:
        ref: The reference string containing namespace.

    Returns:
        str: The reference string with namespace removed.

    Examples:
        >>> remove_namespace("app.utils.temply.schema.tenant.settings")
        'tenant.settings'
        >>> remove_namespace("app.utils.temply.schema")
        'schema'
    """
    print(f"[remove_namespace] input: {ref}")
    # Return only the part after .schema.
    if ".schema." in ref:
        result = ref.split(".schema.", 1)[1]
        print(f"[remove_namespace] .schema. found, result: {result}")
        return result
    # Return 'schema' if it ends with .schema
    if ref.endswith(".schema"):
        print(f"[remove_namespace] .schema ends, result: schema")
        return "schema"

    print(f"[remove_namespace] no change, result: {ref}")
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
    print(f"[normalize_ref] input: {ref}")
    # Remove ID
    components = re.split(r"([\][,])", ref)
    components = [x.split(":")[0] for x in components]
    ref_no_id = "".join(components)
    print(f"[normalize_ref] after id remove: {ref_no_id}")
    # Remove namespace
    result = remove_namespace(ref_no_id)
    print(f"[normalize_ref] after remove_namespace: {result}")
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


class _CustomGenerator(GenerateJsonSchema):
    """Custom JSON schema generator that handles reference normalization.

    This class extends GenerateJsonSchema to provide custom reference handling
    for schema generation, including namespace removal and mode-specific naming.
    """

    @override
    def get_defs_ref(self, core_mode_ref: CoreModeRef) -> DefsRef:
        """Generates a reference for schema definitions.

        Args:
            core_mode_ref: A tuple containing the core reference and mode.

        Returns:
            DefsRef: The generated reference for schema definitions.
        """
        core_ref, mode = core_mode_ref
        short_ref = normalize_ref(core_ref)
        mode_title = get_mode_title(mode)

        module_qualname = DefsRef(self.normalize_name(short_ref))
        module_qualname_mode = DefsRef(f"{module_qualname}-{mode_title}")
        module_qualname_id = DefsRef(self.normalize_name(core_ref))

        occurrence_index = self._collision_index.get(module_qualname_id)
        if occurrence_index is None:
            self._collision_counter[module_qualname] += 1
            occurrence_index = self._collision_index[module_qualname_id] = self._collision_counter[
                module_qualname
            ]

        module_qualname_occurrence_mode = DefsRef(f"{module_qualname_mode}__{occurrence_index}")

        # Use reference without namespace
        custom_name = DefsRef(short_ref)
        self._prioritized_defsref_choices[module_qualname_occurrence_mode] = [
            custom_name,
            module_qualname_occurrence_mode,
        ]
        return module_qualname_occurrence_mode


def infer_from_ast(ast: nodes.Template, env: Environment) -> Variable:
    """Infers variable structure from Jinja2 AST.

    Args:
        ast: The Jinja2 template AST.
        env: The Jinja2 environment.

    Returns:
        Variable: The inferred variable structure.
    """
    ctx = Context(env, return_cls=Unknown, predicted=Scalar.from_ast(ast), macros={})
    return ctx.visit(ast)


def to_json_schema(variable: Variable) -> dict[str, Any]:
    """Converts a variable structure to JSON schema.

    Args:
        variable: The variable structure to convert.

    Returns:
        dict: The generated JSON schema.
    """
    base = variable_to_type(variable, [])
    if get_origin(base) == Union:
        base = RootModel[base]  # type: ignore

    model: type[BaseModel] = create_model("Schema", __base__=base)  # type: ignore
    return model.model_json_schema(schema_generator=_CustomGenerator)
