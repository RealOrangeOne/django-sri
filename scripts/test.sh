#!/usr/bin/env bash

export PATH=env/bin:${PATH}
export PYTHONPATH=$PWD

set -ex


pytest --verbose --cov sri/ --cov-report term --cov-report html

ruff format sri tests setup.py --check

ruff check sri tests setup.py

mypy sri tests setup.py
