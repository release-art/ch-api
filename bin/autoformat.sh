#!/bin/bash -xe

PROJECT_ROOT_DIR=$(dirname "${BASH_SOURCE[0]}")/..

cd "${PROJECT_ROOT_DIR}"

pdm run ruff format src tests ./conftest.py 
pdm run ruff check src tests ./conftest.py --fix