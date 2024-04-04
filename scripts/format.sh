#!/usr/bin/env bash

set -e
set -x

ruff ghost tests scripts --fix
black ghost tests scripts
