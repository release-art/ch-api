#!/bin/bash -xe

PROJECT_ROOT_DIR=$(dirname "${BASH_SOURCE[0]}")/..

cd "${PROJECT_ROOT_DIR}"

if [ $# -eq 0 ]; then
    ARGS=( check src/ )
else
    ARGS=( "$@" )
fi

pdm run ty "${ARGS[@]}"