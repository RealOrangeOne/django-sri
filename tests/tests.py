import os

import pytest
from django.template.loader import render_to_string

from sri import utils
from sri.templatetags import sri as templatetags


def test_simple_template():
    rendered = render_to_string("simple.html")
    assert (
        '<script crossorigin="anonymous" integrity="sha256-VROI/fAMCWgkTthVtzzvHtPkkxvpysdZbcqLdVMtwOI=" src="/static/index.js" type="text/javascript"></script>'
        in rendered
    )
    assert (
        '<link crossorigin="anonymous" href="/static/index.css" integrity="sha256-fsqAKvNYgo9VQgSc4rD93SiW/AjKFwLtWlPi6qviBxY=" rel="stylesheet" type="text/css"/>'
        in rendered
    )


def test_algorithms_template():
    rendered = render_to_string("algorithms.html")
    assert (
        '<script crossorigin="anonymous" integrity="sha384-dExnf54EbXTQ1VmweBEJRWX3MPT4xeDV5p71GIX2hpvV+8B/kzo3SObynuveYt9w" src="/static/index.js" type="text/javascript"></script>'
        in rendered
    )
    assert (
        '<link crossorigin="anonymous" href="/static/index.css" integrity="sha512-7v9G7AKwpjnlEYhw9GdXu/9G8bq0PqM427/QmgH2TufqEUcjsANEoyCoOkpV8TBCnbQigwNKpMaZNskJG8Ejdw==" rel="stylesheet" type="text/css"/>'
        in rendered
    )


@pytest.mark.parametrize("algorithm", utils.HASHERS.keys())
def test_generic_algorithm(algorithm):
    assert f'integrity="{algorithm}-' in templatetags.sri_static("index.css", algorithm)
    assert f'integrity="{algorithm}-' in templatetags.sri_static("index.js", algorithm)


def test_get_static_path():
    index_js_path = utils.get_static_path("index.js")
    assert index_js_path == os.path.abspath("tests/static/index.js")
    assert os.path.isfile(index_js_path)


def test_default_algorithm_exists():
    assert utils.DEFAULT_ALGORITHM in utils.HASHERS


@pytest.mark.parametrize("algorithm", utils.HASHERS.keys())
def test_hashes_are_consistent(algorithm):
    digest = utils.calculate_hash.__wrapped__(
        utils.get_static_path("index.js"), algorithm
    )
    digest_2 = utils.calculate_hash.__wrapped__(
        utils.get_static_path("index.js"), algorithm
    )
    assert digest == digest_2


@pytest.mark.parametrize("algorithm", utils.HASHERS.keys())
def test_integrity(algorithm):
    integrity = utils.calculate_integrity(utils.get_static_path("index.js"), algorithm)
    assert integrity.startswith(algorithm)


def test_disable_sri():
    original_value = templatetags.USE_SRI
    try:
        templatetags.USE_SRI = False
        assert "integrity" not in templatetags.sri_static("index.js")
    finally:
        templatetags.USE_SRI = original_value


@pytest.mark.parametrize("algorithm", utils.HASHERS.keys())
def test_sri_integrity(algorithm):
    assert templatetags.sri_integrity("index.js", algorithm).startswith(f"{algorithm}-")
