#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]:-$0}" )" && pwd )"

mkdir -p "$DIR/deps"

export UV_VENV="$DIR/deps/uv-venv"

if which uv >/dev/null; then
    UV="$(which uv)"
else
    if [ -f "$DIR/deps/bin/uv" ]; then
        UV="$DIR/deps/bin/uv"
    fi

    if [ ! -d "$UV_VENV" ]; then
        echo "## uv not found on PATH, bootstrapping one"

        if which python3 >/dev/null; then
            python3 -m venv "$UV_VENV"
        elif which python >/dev/null; then
            python -m venv "$UV_VENV"
        elif which pip3 >/dev/null; then
            pip3 install uv -t "$DIR/deps" --disable-pip-version-check
            UV="$DIR/deps/bin/uv"
        elif which pip >/dev/null; then
            pip install uv -t "$DIR/deps" --disable-pip-version-check
            UV="$DIR/deps/bin/uv"
        fi
    fi

    if [ -z "$UV" ]; then
        if [ -f "$UV_VENV/bin/uv" ]; then
            UV="$UV_VENV/bin/uv"
        fi

        if [ -z "$UV" ]; then
            if [ ! -f "$UV_VENV/bin/pip" ]; then
                "$UV_VENV/bin/python" -m ensurepip
            fi

            if [ ! -f "$UV_VENV/bin/pip3" ]; then
                echo "Failed to bootstrap a 'uv' to use"
            else
                "$UV_VENV/bin/pip3" install uv
                UV="$UV_VENV/bin/uv"
            fi
        fi
    fi


    if [ -z "$UV" ]; then
        exit 1
    fi
fi

exec "$UV" "$@"
