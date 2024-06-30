#!/bin/bash

set -e

cd "$(git rev-parse --show-toplevel)"

exec ./run.sh tests "$@"
