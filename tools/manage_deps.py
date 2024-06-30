from venvstarter import dependencies


class Deps(dependencies.Deps):
    def set_requirements(self) -> None:
        self.add_local_dep(
            path=self.project_root,
            version_file=self.project_root / "extended_mypy_django_plugin" / "version.py",
            name="extended_mypy_django_plugin[stubs-latest]=={version}",
        )

        self.add_local_dep(
            path=self.project_root / "scripts" / "test_helpers",
            version_file=self.project_root
            / "scripts"
            / "test_helpers"
            / "extended_mypy_django_plugin_test_driver"
            / "version.py",
            name="extended_mypy_django_plugin_test_driver=={version}",
        )

        self.add_local_dep(
            path=self.project_root / "example",
            version_file=self.project_root / "example" / "djangoexample" / "version.py",
            name="djangoexample=={version}",
        )

        in_tox = self.respect_tox()

        if not in_tox:
            self.add_requirements_file(
                self.project_root / "tools" / "requirements.local.txt", missing_ok=True
            )
            self.add_requirements_file(self.project_root / "tools" / "requirements.dev.txt")
            self.add_requirements_file(self.project_root / "tools" / "requirements.docs.txt")


if __name__ == "__main__":
    Deps.from_cli().apply()
