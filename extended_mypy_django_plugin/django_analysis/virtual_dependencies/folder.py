import dataclasses
import pathlib
from typing import TYPE_CHECKING, Generic, cast

from .. import project, protocols
from . import dependency


@dataclasses.dataclass(frozen=True, kw_only=True)
class VirtualDependencyGenerator(Generic[protocols.T_Project, protocols.T_CO_VirtualDependency]):
    discovered_project: protocols.Discovered[protocols.T_Project]
    virtual_dependency_maker: protocols.VirtualDependencyMaker[
        protocols.T_Project, protocols.T_CO_VirtualDependency
    ]

    def generate(self) -> protocols.GeneratedVirtualDependencies[protocols.T_CO_VirtualDependency]:
        return GeneratedVirtualDependencies(
            virtual_dependencies={
                import_path: self.virtual_dependency_maker(
                    discovered_project=self.discovered_project, module=module
                )
                for import_path, module in self.discovered_project.installed_models_modules.items()
            }
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class GeneratedVirtualDependencies(Generic[protocols.T_CO_VirtualDependency]):
    virtual_dependencies: protocols.VirtualDependencyMap[protocols.T_CO_VirtualDependency]

    def install(
        self, *, scratch_root: pathlib.Path, destination: pathlib.Path, hasher: protocols.Hasher
    ) -> None:
        pass


if TYPE_CHECKING:
    C_VirtualDependencyGenerator = VirtualDependencyGenerator[
        project.C_Project, dependency.C_VirtualDependency
    ]
    C_GeneratedVirtualDependencies = GeneratedVirtualDependencies[dependency.C_VirtualDependency]

    _VDN: protocols.P_VirtualDependencyGenerator = cast(
        VirtualDependencyGenerator[protocols.P_Project, protocols.P_VirtualDependency], None
    )
    _GVD: protocols.P_GeneratedVirtualDependencies = cast(
        GeneratedVirtualDependencies[protocols.P_VirtualDependency], None
    )

    _CVDN: protocols.VirtualDependencyGenerator[
        project.C_Project, dependency.C_VirtualDependency
    ] = cast(C_VirtualDependencyGenerator, None)
    _CGVD: protocols.GeneratedVirtualDependencies[dependency.C_VirtualDependency] = cast(
        C_GeneratedVirtualDependencies, None
    )
