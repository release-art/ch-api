#!/bin/bash -xe

THIS_DIR=$(readlink -f $(dirname "${BASH_SOURCE[0]}"))

PROJECT_ROOT_DIR=$(dirname "${BASH_SOURCE[0]}")/..

cd "${PROJECT_ROOT_DIR}"

exec "${THIS_DIR}/run.sh" pdm run pytest "$@"