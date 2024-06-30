import os
import pathlib
import shutil
import subprocess

from venvstarter import cli

here = pathlib.Path(__file__).parent


register = cli.Register()


@register.command
def install(*, command: cli.Command, args: list[str]) -> None:
    """
    Install this project into the virtual env
    """
    if "--venvstarter-force-deps" not in args:
        args.append("--venvstarter-force-deps")

    os.execv(
        str(command.python_path),
        [
            str(command.python_path),
            str(command.project_root / "tools" / "manage_deps.py"),
            *args,
        ],
    )


@register.command
def format(*, command: cli.Command, args: list[str]) -> None:
    """
    Run ruff format and ruff check fixing I and UP rules
    """
    if not args:
        args = [".", *args]
    subprocess.run([command.path_for("ruff"), "format", *args], check=True)
    subprocess.run(
        [command.path_for("ruff"), "check", "--fix", "--select", "I,UP", *args],
        check=True,
    )


@register.command
def lint(*, command: cli.Command, args: list[str]) -> None:
    """
    Run ruff check
    """
    os.execv(command.path_for("ruff"), [command.path_for("ruff"), "check", *args])


@register.command
def types(*, command: cli.Command, args: list[str]) -> None:
    """
    Run mypy
    """
    specified: bool = True
    locations: list[str] = [a for a in args if not a.startswith("-")]
    args = [a for a in args if a.startswith("-")]

    if not locations:
        specified = False
        locations.append(str((here / "..").resolve()))
    else:
        cwd = pathlib.Path.cwd()
        paths: list[pathlib.Path] = []
        for location in locations:
            from_current = cwd / location
            from_root = here.parent / location

            if from_current.exists():
                paths.append(from_current)
            elif from_root.exists():
                paths.append(from_root)
            else:
                raise ValueError(f"Couldn't find path for {location}")

        example_root = here.parent / "example"
        if any(path.is_relative_to(example_root) for path in paths):
            if not all(path.is_relative_to(example_root) for path in paths):
                raise ValueError("If specifying an example path, all paths must be from there")
            os.chdir(example_root)
        locations = [str(path) for path in paths]

    subprocess.run(
        [command.path_for("mypy"), *locations, *args, "--enable-incomplete-feature=Unpack"],
        check=True,
    )

    if not specified:
        os.chdir(here.parent / "example")
        subprocess.run([command.path_for("mypy"), ".", *args], check=True)


@register.command
def tests(*, command: cli.Command, args: list[str]) -> None:
    """
    Run pytest
    """
    os.execv(command.path_for("pytest"), [command.path_for("pytest"), *args])


@register.command
def docs(*, command: cli.Command, args: list[str]) -> None:
    """
    Create the docs.

    > ./run.sh docs [fresh] [view]

    Where fresh and view are optional. Fresh will clear the cache before building,
    view will start a webserver hosting the docs
    """
    docs_path = here / ".." / "docs"
    build_path = docs_path / "_build"
    cmd: list[pathlib.Path | str] = [command.path_for("sphinx-build")]

    other_args: list[str] = []
    for arg in args:
        if arg == "fresh":
            if build_path.exists():
                shutil.rmtree(build_path)
        elif arg == "view":
            cmd = [command.path_for("sphinx-autobuild"), "--port", "9876"]
        else:
            other_args.append(arg)

    os.chdir(docs_path)

    os.execv(
        command.path_for(str(cmd[0])),
        [
            command.path_for(str(cmd[0])),
            *(str(c) for c in cmd[1:]),
            ".",
            "_build/html",
            "-b",
            "html",
            "-d",
            "_build/doctrees",
            *other_args,
        ],
    )


if __name__ == "__main__":
    cli.Command.from_cli(register).run()
