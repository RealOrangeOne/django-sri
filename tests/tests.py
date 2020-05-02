import os

import pytest
from django.template.loader import render_to_string

from sri import utils


def test_simple():
    rendered = render_to_string("simple.html")
    assert (
        "<script src='/static/index.js' integrity='sha256-VROI/fAMCWgkTthVtzzvHtPkkxvpysdZbcqLdVMtwOI='></script>"
        in rendered
    )
    assert (
        "<link rel='stylesheet' href='/static/index.css' integrity='sha256-fsqAKvNYgo9VQgSc4rD93SiW/AjKFwLtWlPi6qviBxY='/>"
        in rendered
    )


def test_generic():
    rendered = render_to_string("generic.html")
    assert (
        "<script src='/static/index.js' integrity='sha256-VROI/fAMCWgkTthVtzzvHtPkkxvpysdZbcqLdVMtwOI='></script>"
        in rendered
    )
    assert (
        "<link rel='stylesheet' href='/static/index.css' integrity='sha256-fsqAKvNYgo9VQgSc4rD93SiW/AjKFwLtWlPi6qviBxY='/>"
        in rendered
    )


def test_get_static_path():
    index_js_path = utils.get_static_path("index.js")
    assert index_js_path == os.path.abspath("tests/static/index.js")
    assert os.path.isfile(index_js_path)


def test_default_algorithm_exists():
    assert utils.DEFAULT_ALGORITHM in utils.HASHERS


@pytest.mark.parametrize("algorithm", utils.HASHERS.keys())
def test_hashes_are_consistent(algorithm):
    digest = utils.calculate_hash(utils.get_static_path("index.js"), algorithm)
    digest_2 = utils.calculate_hash(utils.get_static_path("index.js"), algorithm)
    assert digest == digest_2


@pytest.mark.parametrize("algorithm", utils.HASHERS.keys())
def test_integrity(algorithm):
    integrity = utils.calculate_integrity(utils.get_static_path("index.js"), algorithm)
    assert integrity.startswith(algorithm)
