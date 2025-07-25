"""Custom variable types for template schema generation.

This module defines additional variable types that extend the base types from jinja2schema
to support more complex schema generation scenarios.
"""

import pprint

from jinja2schema.model import List, Number, Tuple  # type: ignore


class Integer(Number):  # type: ignore
    """A integer."""

    def __repr__(self) -> str:
        return "<integer>"


class AdditionalProperties(List):  # type: ignore
    def __repr__(self) -> str:
        return pprint.pformat({"[string]": self.item})


class AnyOf(Tuple):  # type: ignore
    def __repr__(self) -> str:
        return f"anyOf{pprint.pformat(self.items)})"
