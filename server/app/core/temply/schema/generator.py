"""Template parsing and schema generation module.

This module provides functionality for parsing Jinja2 templates and generating JSON schemas
from the parsed templates. It includes utilities for handling references, namespaces,
and schema generation.
"""

from typing import Any, Union, get_origin

from jinja2 import Environment, nodes
from jinja2schema.model import Scalar, Unknown, Variable  # type: ignore
from pydantic import BaseModel, RootModel, create_model
from pydantic.json_schema import CoreModeRef, DefsRef, GenerateJsonSchema
from typing_extensions import override

from .parser import get_mode_title, normalize_ref, variable_to_type
from .visitors.context import Context


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
