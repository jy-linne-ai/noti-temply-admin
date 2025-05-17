"""Custom variable types for template schema generation.

This module defines additional variable types that extend the base types from jinja2schema
to support more complex schema generation scenarios.
"""

import pprint

from jinja2schema.model import Dictionary, List, Number, Unknown, Variable  # type: ignore


class Integer(Number):
    """A integer."""

    def __repr__(self) -> str:
        return "<integer>"


class AdditionalProperties(Dictionary):
    """Represents a dictionary with additional properties.

    This class extends Dictionary to support schema generation for objects
    that can have arbitrary additional properties beyond those explicitly defined.
    """

    def __init__(self, item: Variable = Unknown()) -> None:
        """Initialize AdditionalProperties with an item type.

        Args:
            item: The type of values that can be used as additional properties.
        """
        super().__init__()
        self.item = item

    def __repr__(self) -> str:
        return pprint.pformat({"[string]": self.item})


class AnyOf(List):
    """Represents a variable that can be one of several types.

    This class extends List to support schema generation for variables
    that can have multiple possible types (union types).
    """

    def __init__(self, items: list[Variable] = []) -> None:
        """Initialize AnyOf with a list of possible types.

        Args:
            items: List of possible variable types.
        """
        super().__init__()
        self.items = items

    def __repr__(self) -> str:
        return f"anyOf{pprint.pformat(self.items)})"
