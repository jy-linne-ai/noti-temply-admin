from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Callable, Type

from jinja2 import nodes
from jinja2schema.exceptions import InvalidExpression
from jinja2schema.macro import Macro, MacroCall
from jinja2schema.model import (
    Boolean,
    Dictionary,
    List,
    Number,
    Scalar,
    String,
    Tuple,
    Unknown,
    Variable,
)

from ..mergers import merge, merge_bool_expr_structs, merge_rtypes
from ..model import AdditionalProperties, Integer

if TYPE_CHECKING:
    from .context import Context

EXPR_VISITORS: dict[
    Type[nodes.Expr], Callable[[Context, nodes.Expr], tuple[Variable, Variable]]
] = {}


def expr(
    cls: Type[nodes.Expr],
) -> Callable[
    [Callable[..., tuple[Variable, Variable]]],
    Callable[[Context, nodes.Expr], tuple[Variable, Variable]],
]:
    def decorator(
        func: Callable[[Context, nodes.Expr], tuple[Variable, Variable]],
    ) -> Callable[[Context, nodes.Expr], tuple[Variable, Variable]]:
        EXPR_VISITORS[cls] = func

        @functools.wraps(func)
        def wrapper(ctx: Context, node: nodes.Expr) -> tuple[Variable, Variable]:
            assert isinstance(node, cls)
            return func(ctx, node)

        return wrapper

    return decorator


def visit_expr(ctx: Context, node: nodes.Expr) -> tuple[Variable, Variable]:
    visitor = EXPR_VISITORS.get(type(node))
    if visitor is None:
        for k, v in EXPR_VISITORS.items():
            if isinstance(node, k):
                visitor = v
                break
    if visitor is None:
        raise NotImplementedError(f"Expression visitor for {type(node)} not implemented")

    return visitor(ctx, node)


@expr(nodes.BinExpr)
def visit_bin_expr(ctx: Context, node: nodes.BinExpr) -> tuple[Variable, Variable]:
    # determine the predicted type
    l_rtype, _ = visit_expr(ctx, node.left)
    r_rtype, _ = visit_expr(ctx, node.right)
    rtype = merge_rtypes(l_rtype, r_rtype, operator=node.operator)
    # re-visit the expression with the predicted type
    ctx = ctx.clone(predicted=rtype)
    _, l_struct = visit_expr(ctx, node.left)
    _, r_struct = visit_expr(ctx, node.right)
    return rtype, merge_bool_expr_structs(l_struct, r_struct)


@expr(nodes.Call)
def visit_call(ctx: Context, node: nodes.Call) -> tuple[Variable, Variable]:
    def call_macro(macro: Macro) -> tuple[Variable, Variable]:
        def match_passed_kwargs(call: MacroCall, to_args: list[tuple[str, Variable]]) -> Variable:
            rv = Dictionary()
            for kwarg_name, (kwarg_ast, kwarg_type) in list(call.passed_kwargs.items()):
                for expected_arg_name, expected_arg_struct in to_args:
                    if kwarg_name == expected_arg_name:
                        _, s = visit_expr(
                            ctx.clone(predicted=merge(kwarg_type, expected_arg_struct)),
                            kwarg_ast.value,
                        )
                        rv = merge(rv, s)
                        to_args.remove((expected_arg_name, expected_arg_struct))
                        del call.passed_kwargs[kwarg_name]
            return rv

        call = MacroCall(macro, node.args, node.kwargs)
        args_struct = call.match_passed_args_to_expected_args()
        if call.passed_args:
            # TODO
            args_struct = merge(args_struct, call.match_passed_args_to_expected_kwargs())
        if call.passed_kwargs:
            args_struct = merge(args_struct, match_passed_kwargs(call, call.expected_args))
            args_struct = merge(args_struct, match_passed_kwargs(call, call.expected_kwargs))
        return Unknown(), args_struct

    if isinstance(node.node, nodes.Name):
        if node.node.name in ctx.macros:
            macro = ctx.macros[node.node.name]
            return call_macro(macro)
        elif node.node.name == "dict":
            # load assigned variables as a base dictionary
            def load_assigned(name: str) -> Variable:
                struct = Unknown.from_ast(node)
                for var_name, var_nodes in ctx.assigned:
                    if var_name == name:
                        for dict in var_nodes:
                            struct = merge(struct, ctx.visit(dict))
                return struct

            rtype = Dictionary()
            struct = Unknown.from_ast(node)
            if node.args:
                if len(node.args) > 1:
                    raise InvalidExpression(node, "dict() takes at most 1 argument")
                if isinstance(node.args[0], nodes.Name):
                    struct = merge(struct, load_assigned(node.args[0].name))
                else:
                    struct = merge(struct, ctx.visit(node.args[0]))
            if node.dyn_kwargs:
                if isinstance(node.dyn_kwargs, nodes.Name):
                    struct = merge(struct, load_assigned(node.dyn_kwargs.name))
                else:
                    struct = merge(struct, ctx.visit(node.dyn_kwargs))
            ret_rtype, ret_strct = _visit_dict(
                ctx, node.node, [(item.key, item.value) for item in node.kwargs]
            )
            return merge(rtype, ret_rtype), merge(struct, ret_strct)
        elif node.node.name == "caller":
            # TODO: check if inside a macro
            # TODO: with args
            return Unknown(), Dictionary()
    elif isinstance(node.node, nodes.Getattr):
        predicted = Unknown.from_ast(node.node)
        # TODO: macro call?
        if node.node.attr == "split":
            predicted = String()
        if node.node.attr == "update":
            target = []
            # find the variable to update
            # TODO: not assigned variables
            if isinstance(node.node.node, nodes.Name):
                for var_name, var_nodes in ctx.assigned:
                    if var_name == node.node.node.name:
                        target = var_nodes
                        break
            for dict in node.args:
                target.append(dict)
        return visit_expr(ctx.clone(predicted=predicted), node.node.node)

    raise NotImplementedError(f"Call expressions for {node.node} are not supported")


@expr(nodes.Compare)
def visit_compare(ctx: Context, node: nodes.Compare) -> tuple[Variable, Variable]:
    ctx.test(Boolean(), node)
    struct = ctx.clone(predicted=Unknown.from_ast(node.expr)).visit(node.expr)
    optypes = set()
    for op in node.ops:
        if op.op == "in":
            predicted = AdditionalProperties.from_ast(node.expr, Unknown())
        else:
            predicted = Unknown.from_ast(node.expr)
        optype, op_struct = visit_expr(ctx.clone(predicted=predicted), op.expr)
        optypes.add(type(optype))
        struct = merge(struct, op_struct)
    assert len(optypes) == 1
    # predict the type of the expression and re-visit expr
    predicted = next(iter(optypes)).from_ast(node.expr)
    expr_struct = ctx.clone(predicted=predicted).visit(node.expr)
    struct = merge(struct, expr_struct)

    return Boolean.from_ast(node), struct


@expr(nodes.Concat)
def visit_concat(ctx: Context, node: nodes.Concat) -> tuple[Variable, Variable]:
    struct = Dictionary()
    for n in node.nodes:
        n_struct = ctx.visit(n)
        struct = merge(struct, n_struct)
    return String(), struct


@expr(nodes.CondExpr)
def visit_cond_expr(ctx: Context, node: nodes.CondExpr) -> tuple[Variable, Variable]:
    def custom_merger(fst: Variable, snd: Variable, result: Variable) -> Variable:
        # if the `fst` is checked as defined, then the result is checked as defined
        if fst.checked_as_defined:
            result.checked_as_defined = True
        return result

    test_predicted_struct = Boolean.from_ast(node.test)
    test_struct = ctx.clone(predicted=test_predicted_struct).visit(node.test)
    if_rtype, if_struct = visit_expr(ctx, node.expr1)
    struct = merge(test_struct, if_struct, custom_merger=custom_merger)
    rtype = if_rtype
    if node.expr2 is not None:
        else_rtype, else_struct = visit_expr(ctx, node.expr2)
        # re-visit the expression with the expr2's return type
        if_struct = ctx.clone(predicted=else_rtype).visit(node.expr1)
        struct = merge(struct, if_struct, custom_merger=custom_merger)

        struct = merge(struct, else_struct)
        rtype = merge_rtypes(rtype, else_rtype)
    # TODO: check test_struct items
    return rtype, struct


@expr(nodes.Const)
def visit_const(ctx: Context, node: nodes.Const) -> tuple[Variable, Variable]:
    ctx.test(Scalar(), node)
    if isinstance(node.value, str):
        rtype = String.from_ast(node, constant=True)
    elif isinstance(node.value, bool):
        rtype = Boolean.from_ast(node, constant=True)
    elif isinstance(node.value, int):
        rtype = Integer.from_ast(node, constant=True)
    elif isinstance(node.value, float):
        rtype = Number.from_ast(node, constant=True)
    elif node.value is None:
        rtype = Unknown.from_ast(node, constant=True)
    else:
        rtype = Scalar.from_ast(node, constant=True)
    return rtype, Dictionary()


@expr(nodes.Dict)
def visit_dict(ctx: Context, node: nodes.Dict) -> tuple[Variable, Variable]:
    return _visit_dict(ctx, node, [(item.key, item.value) for item in node.items])


def _visit_dict(
    ctx: Context, node: nodes.Expr, items: list[tuple[str | nodes.Expr, nodes.Expr]]
) -> tuple[Variable, Variable]:
    ctx.test(Dictionary(), node)
    rtype = Dictionary.from_ast(node, constant=True)
    struct = Dictionary()
    p = ctx.get_predicted()
    for key, value in items:
        predicted = Unknown.from_ast(value)

        # already predicted?
        if isinstance(key, nodes.Const):
            key_name = key.value
        elif isinstance(key, str):
            key_name = key
        else:
            raise NotImplementedError("Dict key is not str or Const")
        if key_name in p.data:
            predicted = p[key_name]

        value_rtype, value_struct = visit_expr(ctx.clone(predicted=predicted), value)
        rtype[key_name] = value_rtype
        struct = merge(struct, value_struct)
    return rtype, struct


@expr(nodes.Filter)
def visit_filter(ctx: Context, node: nodes.Filter) -> tuple[Variable, Variable]:
    return_cls = None
    other_struct = Unknown()
    if node.name in {"e", "replace", "safe", "truncate"} or node.name.startswith("escape"):
        ctx.test(Scalar(), node)
        return_cls = String
        predicted = String.from_ast(node.node)
    elif node.name in {"abs"}:
        ctx.test(Number(), node)
        return_cls = Number
        predicted = Number.from_ast(node.node)
    elif node.name in {"dictsort"}:
        ctx.test(List(item=Tuple(items=[String(), Unknown()])), node)
        predicted = Dictionary.from_ast(node.node)
    elif node.name in {"first", "last", "length", "sum", "abs"}:
        if node.name in {"length"}:
            ctx.test(Scalar(), node)
            return_cls = Integer
            struct = Unknown.from_ast(node.node)
        else:
            struct = ctx.get_predicted()

        for kwarg in node.kwargs:
            if kwarg.key == "attribute":
                struct = Dictionary.from_ast(node.node, {kwarg.value.as_const(): Number()})

        # `length` filter accepts sized objects such as `str`, `dict`, ...
        # but at the moment it is assumed to apply only to `list`.
        predicted = List.from_ast(node.node, struct)
    elif node.name in {"join"}:
        return_cls = String
        predicted = List.from_ast(node.node, String())
    elif node.name in {"select", "selectattr", "sort"}:
        ctx.test(List(item=Unknown()), node)
        struct = Unknown()
        if node.name == "selectattr":
            if isinstance(node.args[0], nodes.Const):
                if node.args[1].as_const() in {"==", "eq"} and len(node.args) > 2:
                    rtype, rstruct = visit_expr(ctx.clone(predicted=Unknown()), node.args[2])
                    struct = Dictionary.from_ast(
                        node.node,
                        {node.args[0].value: rtype},
                    )
                    other_struct = merge(other_struct, rstruct)
        predicted = merge(List.from_ast(node.node, item=struct), ctx.get_predicted())
    elif node.name in ("list"):
        ctx.test(List(item=Unknown()), node)
        predicted = merge(List.from_ast(node.node, item=Unknown()), ctx.get_predicted())
    else:
        raise NotImplementedError(f"Filter `{node.name}` is not supported")

    if node.node:
        rtype, rstruct = visit_expr(
            ctx.clone(return_cls=return_cls, predicted=predicted), node.node
        )
        return rtype, merge(rstruct, other_struct)
    else:
        raise NotImplementedError("Filter has no node")


@expr(nodes.Getattr)
def visit_getattr(ctx: Context, node: nodes.Getattr) -> tuple[Variable, Variable]:
    return visit_expr(
        ctx.clone(
            predicted=Dictionary.from_ast(
                node,
                {
                    node.attr: ctx.get_predicted(label=node.attr),
                },
            )
        ),
        node.node,
    )


@expr(nodes.Getitem)
def visit_getitem(ctx: Context, node: nodes.Getitem) -> tuple[Variable, Variable]:
    if isinstance(node.arg, nodes.Const):
        if isinstance(node.arg.value, str):
            predicted = Dictionary.from_ast(
                node, {node.arg.value: ctx.get_predicted(label=node.arg.value)}
            )
        else:
            raise NotImplementedError("Getitem (arg.value: not str) not implemented")
    elif isinstance(node.arg, nodes.Name):
        predicted = AdditionalProperties.from_ast(node, ctx.get_predicted(label=node.arg.name))
    elif isinstance(node.arg, nodes.Slice):
        raise NotImplementedError("Getitem (arg: Slice) not implemented")
    elif isinstance(node.arg, nodes.Getattr):
        predicted = AdditionalProperties.from_ast(node, ctx.get_predicted(label=node.arg.attr))
    else:
        # TODO: configuration for prediction as a list
        predicted = Dictionary.from_ast(node)

    arg_struct = ctx.clone(predicted=String.from_ast(node.arg)).visit(node.arg)
    rtype, struct = visit_expr(ctx.clone(predicted=predicted), node.node)
    return rtype, merge(struct, arg_struct)


@expr(nodes.List)
def visit_list(ctx: Context, node: nodes.List) -> tuple[Variable, Variable]:
    ctx.test(List(Unknown()), node)
    struct = Dictionary()

    predicted_struct = merge(List(Unknown()), ctx.get_predicted())
    el_rtype = None
    for item in node.items:
        item_rtype, item_struct = visit_expr(ctx.clone(predicted=predicted_struct), item)
        struct = merge(struct, item_struct)
        if el_rtype is None:
            el_rtype = item_rtype
        else:
            el_rtype = merge_rtypes(el_rtype, item_rtype)
    rtype = List.from_ast(node, el_rtype or Unknown(), constant=True)
    return rtype, struct


@expr(nodes.Name)
def visit_name(ctx: Context, node: nodes.Name) -> tuple[Variable, Variable]:
    return ctx.return_cls.from_ast(node), Dictionary(
        {
            node.name: ctx.get_predicted(label=node.name),
        }
    )


@expr(nodes.Test)
def visit_test(ctx: Context, node: nodes.Test) -> tuple[Variable, Variable]:
    ctx.test(Boolean(), node)
    if node.name in {"defined", "none", "undefined", "eq", "equalto"}:
        predicted = Unknown.from_ast(node.node)

        if node.name in {"eq", "equalto"}:
            rtype, _ = visit_expr(ctx.clone(predicted=predicted), node.args[0])
            predicted = merge(predicted, rtype)

        if node.name == "defined":
            predicted.checked_as_defined = True
        elif node.name == "undefined":
            predicted.checked_as_undefined = True
    elif node.name in {"true", "false"}:
        predicted = Boolean.from_ast(node.node)
    else:
        raise InvalidExpression(node, f"unknown test `{node.name}`")

    return visit_expr(ctx.clone(return_cls=Boolean, predicted=predicted), node.node)


@expr(nodes.TemplateData)
def visit_template_data(ctx: Context, node: nodes.TemplateData) -> tuple[Variable, Variable]:
    return Scalar(), Dictionary()


@expr(nodes.UnaryExpr)
def visit_unary_expr(ctx: Context, node: nodes.UnaryExpr) -> tuple[Variable, Variable]:
    return visit_expr(ctx, node.node)
