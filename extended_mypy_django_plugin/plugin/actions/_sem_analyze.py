from mypy.nodes import (
    GDEF,
    StrExpr,
    SymbolTableNode,
    TypeInfo,
    TypeVarExpr,
)
from mypy.plugin import (
    DynamicClassDefContext,
)
from mypy.semanal import SemanticAnalyzer
from mypy.types import (
    AnyType,
    TypeOfAny,
    TypeVarType,
)
from mypy.types import Type as MypyType

from .. import _store


class SemAnalyzing:
    def __init__(self, store: _store.Store) -> None:
        self.store = store

    def transform_type_var_classmethod(
        self,
        ctx: DynamicClassDefContext,
        api: SemanticAnalyzer,
        mypy_version_tuple: tuple[int, int],
    ) -> None:
        if not isinstance(ctx.call.args[0], StrExpr):
            api.fail(
                "First argument to Concrete.type_var must be a string of the name of the variable",
                ctx.call,
            )
            return

        name = ctx.call.args[0].value
        if name != ctx.name:
            api.fail(
                f"First argument {name} was not the name of the variable {ctx.name}",
                ctx.call,
            )
            return

        module = api.modules[api.cur_mod_id]
        if isinstance(module.names.get(name), TypeVarType):
            return

        parent: SymbolTableNode | None = None
        try:
            parent = api.lookup_type_node(ctx.call.args[1])
        except AssertionError:
            parent = None

        if parent is None:
            api.fail(
                "Second argument to Concrete.type_var must be the abstract model class to find concrete instances of",
                ctx.call,
            )
            return

        if not isinstance(parent.node, TypeInfo):
            api.fail("Second argument to Concrete.type_var was not pointing at a class", ctx.call)
            return

        object_type = api.named_type("builtins.object")
        values: list[MypyType] = []
        for instance in self.store.concrete_for(parent.node).instances(api):
            values.append(instance)

        if mypy_version_tuple >= (1, 4):
            type_var_expr = TypeVarExpr(
                name=name,
                fullname=f"{api.cur_mod_id}.{name}",
                values=values,
                upper_bound=object_type,
                default=AnyType(TypeOfAny.from_omitted_generics),
            )
        else:
            type_var_expr = TypeVarExpr(  # type: ignore[call-arg]
                name=name,
                fullname=f"{api.cur_mod_id}.{name}",
                values=values,
                upper_bound=object_type,
            )

        module.names[name] = SymbolTableNode(GDEF, type_var_expr, plugin_generated=True)
        return None
