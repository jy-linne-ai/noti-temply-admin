from __future__ import annotations

import functools
from itertools import zip_longest
from typing import TYPE_CHECKING, Callable, Type

from jinja2 import nodes
from jinja2schema.macro import Macro
from jinja2schema.model import Boolean, Dictionary, List, Scalar, Tuple, Unknown, Variable

from ..mergers import merge
from ..model import AnyOf
from ..utils import merge_checked
from ..visitors.expr import visit_expr

if TYPE_CHECKING:
    from .context import Context

STMT_VISITORS: dict[Type[nodes.Stmt], Callable[..., Variable]] = {}


def stmt(
    cls: Type[nodes.Stmt],
) -> Callable[[Callable[..., Variable]], Callable[[Context, nodes.Stmt], Variable]]:
    def decorator(
        func: Callable[[Context, nodes.Stmt], Variable],
    ) -> Callable[[Context, nodes.Stmt], Variable]:
        STMT_VISITORS[cls] = func

        @functools.wraps(func)
        def wrapper(ctx: Context, node: nodes.Stmt) -> Variable:
            assert isinstance(node, cls)
            return func(ctx, node)

        return wrapper

    return decorator


def visit_stmt(ctx: Context, node: nodes.Stmt) -> Variable:
    visitor = STMT_VISITORS.get(type(node))
    if visitor is None:
        raise NotImplementedError(f"Statement visitor for {type(node)} not implemented")

    return visitor(ctx, node)


@stmt(nodes.Assign)
def visit_assign(ctx: Context, node: nodes.Assign) -> Variable:
    if isinstance(node.target, nodes.Name):
        struct = Dictionary()
        variables = [(node.target.name, node.node)]
        # TODO: tuples, etc.
        for var_name, var_node in variables:
            assert isinstance(var_node, nodes.Expr)
            for name, var_nodes in ctx.assigned:
                if name == var_name:
                    var_nodes.append(var_node)
                    break
            else:
                ctx.assigned.append((var_name, [var_node]))
        return struct
    else:
        raise NotImplementedError("Unsupported assignment")


@stmt(nodes.Block)
def visit_block(ctx: Context, node: nodes.Block) -> Variable:
    return ctx.visit_many(node.body)


@stmt(nodes.CallBlock)
def visit_call_block(ctx: Context, node: nodes.CallBlock) -> Variable:
    # TODO: with arguments
    call_struct = ctx.visit(node.call)
    struct = ctx.visit_many(node.body)
    return merge(call_struct, struct)


@stmt(nodes.Continue)
def visit_continue(ctx: Context, node: nodes.Continue) -> Variable:
    return Dictionary()


@stmt(nodes.ExprStmt)
def visit_expr_stmt(ctx: Context, node: nodes.ExprStmt) -> Variable:
    return ctx.visit(node.node)


@stmt(nodes.Extends)
def visit_extends(ctx: Context, node: nodes.Extends) -> Variable:
    if ctx.env.loader is None:
        raise RuntimeError("No loader for Jinja2 environment")
    source, _, _ = ctx.env.loader.get_source(ctx.env, node.template.as_const())
    template = ctx.env.parse(source)
    return ctx.visit_many(template.body)


@stmt(nodes.For)
def visit_for(ctx: Context, node: nodes.For) -> Variable:
    body_struct = ctx.visit_many(node.body)
    if "loop" in body_struct:
        del body_struct["loop"]
    if isinstance(node.target, nodes.Name):
        target_struct = body_struct.pop(node.target.name, Unknown.from_ast(node.target))
    elif isinstance(node.target, nodes.Tuple):
        assert isinstance(body_struct, Dictionary)
        items = []
        for item in node.target.items:
            assert isinstance(item, nodes.Name)
            items.append(body_struct.pop(item.name, Unknown.from_ast(node.target)))
        target_struct = Tuple.from_ast(node.target, items)
    else:
        raise NotImplementedError("only `Name` and `Tuple` targets are implemented")

    iter_struct = ctx.clone(predicted=List.from_ast(node, target_struct)).visit(node.iter)
    return merge(body_struct, iter_struct)


@stmt(nodes.FromImport)
def visit_from_import(ctx: Context, node: nodes.FromImport) -> Variable:
    if ctx.env.loader is None:
        raise RuntimeError("No loader for Jinja2 environment")
    source, _, _ = ctx.env.loader.get_source(ctx.env, node.template.as_const())
    template = ctx.env.parse(source)

    new_ctx = ctx.clone(macros={})
    struct = new_ctx.visit_many(template.body)
    for name in node.names:
        if isinstance(name, tuple):
            macro_name, alias = name
            ctx.macros[alias] = new_ctx.macros[macro_name]
        else:
            raise NotImplementedError("only `Tuple` targets for FromImport are implemented")
    if node.with_context:
        return struct
    else:
        return Dictionary()


@stmt(nodes.If)
def visit_if(ctx: Context, node: nodes.If) -> Variable:
    def merge_as_anyof(fst: Variable, snd: Variable, result: Variable) -> Variable:
        if isinstance(fst, Dictionary) and isinstance(snd, Dictionary):
            if set(fst.keys()) == set(snd.keys()):
                for key in fst.keys():
                    result[key] = merge_as_anyof(fst[key], snd[key], result[key])
            else:
                result = AnyOf([fst, snd])
        elif not (
            isinstance(fst, type(snd))
            or isinstance(fst, Unknown)
            or isinstance(snd, Unknown)
            or fst == snd
        ):
            result = AnyOf([fst, snd])
        return result

    test_struct = ctx.clone(predicted=Boolean.from_ast(node.test)).visit(node.test)
    if_struct = ctx.visit_many(node.body, new_scope=False)
    if_struct = merge(test_struct, if_struct, custom_merger=merge_checked)
    else_struct = ctx.visit_many(node.else_, new_scope=False)
    else_struct = merge(test_struct, else_struct, custom_merger=merge_checked)
    # TODO
    if node.else_:
        merged = merge(if_struct, else_struct, custom_merger=merge_as_anyof)
    else:
        merged = if_struct
    struct = merge(test_struct, merged, custom_merger=merge_checked)
    # TODO: elif

    return struct


@stmt(nodes.Import)
def visit_import(ctx: Context, node: nodes.Import) -> Variable:
    if ctx.env.loader is None:
        raise RuntimeError("No loader for Jinja2 environment")
    source, _, _ = ctx.env.loader.get_source(ctx.env, node.template.as_const())
    template = ctx.env.parse(source)

    new_ctx = ctx.clone(macros={})
    new_ctx.visit_many(template.body)
    ctx.macros[node.target] = new_ctx.macros
    return Dictionary()


@stmt(nodes.Include)
def visit_include(ctx: Context, node: nodes.Include) -> Variable:
    if ctx.env.loader is None:
        raise RuntimeError("No loader for Jinja2 environment")
    source, _, _ = ctx.env.loader.get_source(ctx.env, node.template.as_const())
    template = ctx.env.parse(source)
    return ctx.visit_many(template.body)


@stmt(nodes.Macro)
def visit_macro(ctx: Context, node: nodes.Macro) -> Variable:
    args = []
    kwargs = []
    body_struct = ctx.clone(predicted=Scalar()).visit_many(node.body)
    for arg, default_value_ast in reversed(
        list(zip_longest(reversed(node.args), reversed(node.defaults)))
    ):
        has_default_value = default_value_ast is not None
        if has_default_value:
            default_rtype, _ = visit_expr(
                ctx.clone(predicted=Unknown()),
                default_value_ast,
            )
        else:
            default_rtype = Unknown()

        if arg.name in body_struct:
            default_rtype = merge(default_rtype, body_struct[arg.name])

        if has_default_value:
            kwargs.append((arg.name, default_rtype))
        else:
            args.append((arg.name, default_rtype))
    ctx.macros[node.name] = Macro(node.name, args, kwargs)

    args_struct = Dictionary(dict(args) | dict(kwargs))
    for arg in args_struct.iterkeys():
        body_struct.pop(arg, None)
    return body_struct


@stmt(nodes.Output)
def visit_output(ctx: Context, node: nodes.Output) -> Variable:
    return ctx.visit_many(node.nodes)
