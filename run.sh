#!/bin/bash
#
# https://stackoverflow.com/questions/2683279/how-to-detect-if-a-script-is-being-sourced
sourced=0
if [ -n "$ZSH_VERSION" ]; then 
    case $ZSH_EVAL_CONTEXT in *:file) sourced=1;; esac
elif [ -n "$KSH_VERSION" ]; then
    # shellcheck disable=SC2296
    [ "$(cd -- "$(dirname -- "$0")" && pwd -P)/$(basename -- "$0")" != "$(cd -- "$(dirname -- "${.sh.file}")" && pwd -P)/$(basename -- "${.sh.file}")" ] && sourced=1
elif [ -n "$BASH_VERSION" ]; then
    (return 0 2>/dev/null) && sourced=1 
else
    # All other shells: examine $0 for known shell binary filenames.
    # Detects `sh` and `dash`; add additional shell filenames as needed.
    case ${0##*/} in sh|-sh|dash|-dash)
        if [ -z "$VENVSTARTER_PROJECT_ROOT" ]; then
            echo "POSIX environments need VENVSTARTER_PROJECT_ROOT in the environment for 'source run.sh activate' to work"
            echo "This must be set to the root of this repository"
            return 1
        fi
    ;;
    esac
fi

# Bash does not make it easy to find where this file is
# Here I'm making it so it doesn't matter what directory you are in
# when you execute this script. And it doesn't matter whether you're
# executing a symlink to this script
# Note the `-h` in the while loop asks if this path is a symlink
pushd . >'/dev/null'
find_here() {
    SCRIPT_PATH="${BASH_SOURCE[0]:-$0}"
    while [ -h "$SCRIPT_PATH" ]; do
        cd "$(dirname -- "$SCRIPT_PATH")" || return 1
        SCRIPT_PATH="$(readlink -f -- "$SCRIPT_PATH")"
    done
    cd "$(dirname -- "$SCRIPT_PATH")" >'/dev/null' || return 1
}

if ! find_here; then
    if [ "$sourced" = "1" ]; then
        return 1
    else
        exit 1
    fi
fi

VENVSTARTER_PROJECT_ROOT=$(pwd)
export VENVSTARTER_PROJECT_ROOT

if [ "$sourced" = "1" ]; then
    if ! ./tools/venv --venvstarter-venv-only; then
        return 1
    else
        ./tools/venv --venvstarter-get-activate-script ./tools/deps/where-is-activate
        if [ -f ./tools/deps/where-is-activate ]; then
            activate=$(cat ./tools/deps/where-is-activate)
        fi

        if [ -z "$activate" ]; then
            echo "!!! Failed to activate virtualenv"
        else
            # shellcheck source=/dev/null
            source "$activate"
        fi
    fi
else
    exec ./tools/venv "$@"
fi
