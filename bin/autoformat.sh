#!/bin/bash -xe

PROJECT_ROOT_DIR=$(dirname "${BASH_SOURCE[0]}")/..

cd "${PROJECT_ROOT_DIR}"

pdm run ruff format src tests
pdm run ruff check src tests --fix