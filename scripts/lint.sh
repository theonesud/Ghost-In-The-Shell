#!/usr/bin/env bash

set -e
set -x

mypy ghost
ruff ghost tests scripts
black ghost tests --check
