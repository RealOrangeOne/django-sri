#!/usr/bin/env bash

export PATH=env/bin:${PATH}

set -ex


pytest --verbose --cov sri/ --cov-report term --cov-report html

if hash black 2>/dev/null;
then
    black sri tests setup.py --check
fi

ruff check sri tests setup.py

mypy sri tests setup.py
