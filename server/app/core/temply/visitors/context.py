from typing import Optional, Sequence, Type

from jinja2 import Environment, nodes
from jinja2schema.exceptions import UnexpectedExpression
from jinja2schema.macro import Macro
from jinja2schema.mergers import MergeException
from jinja2schema.model import Dictionary, Unknown, Variable

from ..mergers import merge
from ..utils import merge_checked
from .expr import visit_expr
from .stmt import visit_stmt


class Context:
    def __init__(
        self,
        env: Environment,
        return_cls: Type[Variable] = Unknown,
        predicted: Optional[Variable] = None,
        macros: dict[str, Macro] = {},
        assigned: list[tuple[str, list[nodes.Expr]]] = [],
    ) -> None:
        self.env = env
        self.return_cls = return_cls
        self.predicted = predicted
        self.macros = macros
        self.assigned = assigned

    def clone(
        self,
        return_cls: Optional[Type[Variable]] = None,
        predicted: Optional[Variable] = None,
        macros: Optional[dict[str, Macro]] = None,
        assigned: Optional[list[tuple[str, list[nodes.Expr]]]] = None,
    ) -> "Context":
        if return_cls is None:
            return_cls = self.return_cls
        if predicted is None:
            predicted = self.predicted
        if macros is None:
            macros = self.macros
        if assigned is None:
            assigned = self.assigned
        return Context(
            self.env,
            return_cls=return_cls,
            predicted=predicted,
            macros=macros,
            assigned=assigned,
        )

    def get_predicted(self, label: Optional[str] = None) -> Variable:
        assert self.predicted is not None
        rv = self.predicted.clone()
        if label:
            rv.label = label
        return rv

    def test(self, actual_struct: Variable, actual_ast: nodes.Node) -> None:
        try:
            merge(self.predicted, actual_struct)
        except MergeException:
            raise UnexpectedExpression(self.predicted, actual_ast, actual_struct)

    def visit(
        self,
        node: nodes.Node,
    ) -> Variable:
        if isinstance(node, nodes.Stmt):
            return visit_stmt(self, node)
        elif isinstance(node, nodes.Expr):
            _, structure = visit_expr(self, node)
            return structure
        elif isinstance(node, nodes.Template):
            return self.visit_many(node.body)

    def visit_many(self, body: Sequence[nodes.Node], new_scope: bool = True) -> Variable:
        if new_scope:
            new_ctx = self.clone(assigned=[])
        else:
            new_ctx = self.clone()
        rv = Dictionary()
        for node in body:
            rv = merge(rv, new_ctx.visit(node))

        # resolve assigned variables
        if new_scope and isinstance(rv, Dictionary):
            for var_name, var_nodes in reversed(new_ctx.assigned):
                if var_name not in rv.keys():
                    continue
                predicted = rv.pop(var_name)
                struct = Unknown()
                for expr in var_nodes:
                    _, expr_struct = visit_expr(self.clone(predicted=predicted), expr)
                    struct = merge(struct, expr_struct)
                rv = merge(rv, struct, custom_merger=merge_checked)
        return rv
