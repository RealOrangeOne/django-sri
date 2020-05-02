#!/usr/bin/env bash

export PATH=env/bin:${PATH}

set -ex


python manage.py test

if hash black 2>/dev/null;
then
    black sri tests setup.py --check
fi

flake8 sri tests setup.py

isort -rc -c sri tests setup.py

mypy sri tests setup.py
