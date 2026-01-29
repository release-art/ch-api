#!/bin/bash -xe

PROJECT_ROOT_DIR=$(dirname "${BASH_SOURCE[0]}")/..

# test env key
# export CH_API_KEY="${CH_API_KEY:-op://ov3y3t5l4bclacuzqqenf4t7iy/iioqmlvidd6k7mt2ctgh4omnde/Api Key}"

# live end key
export CH_API_KEY="${CH_API_KEY:-op://Employee/xur7xnbmzohggfqilxs5nrnbfi/credential}"

cd "${PROJECT_ROOT_DIR}"

exec op run --no-masking -- "${@}"