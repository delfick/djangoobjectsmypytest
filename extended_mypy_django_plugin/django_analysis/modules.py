import dataclasses
import types
from collections.abc import Sequence
from typing import TYPE_CHECKING, Protocol, cast

from django.db import models
from typing_extensions import Self

from extended_mypy_django_plugin.django_analysis import protocols


class ModelCreator(Protocol):
    def __call__(self, *, model: type[models.Model]) -> protocols.Model: ...


@dataclasses.dataclass(frozen=True, kw_only=True)
class Module:
    @classmethod
    def create(
        cls,
        *,
        model_creator: ModelCreator,
        import_path: protocols.ImportPath,
        module: types.ModuleType | None,
        models: Sequence[type[models.Model]],
    ) -> Self:
        return cls(
            installed=module is not None,
            import_path=import_path,
            defined_models_by_name={
                protocols.ImportPath(f"{model.__module__}.{model.__qualname__}"): model_creator(
                    model=model
                )
                for model in models
            },
        )

    installed: bool
    import_path: protocols.ImportPath
    defined_models_by_name: protocols.DefinedModelsMap


if TYPE_CHECKING:
    _M: protocols.Module = cast(Module, None)