import os

import pytest
from django.template.loader import render_to_string

from sri import utils
from sri.templatetags import sri as templatetags


def test_simple_template():
    rendered = render_to_string("simple.html")
    assert (
        "<script src='/static/index.js' integrity='sha256-VROI/fAMCWgkTthVtzzvHtPkkxvpysdZbcqLdVMtwOI='></script>"
        in rendered
    )
    assert (
        "<link rel='stylesheet' href='/static/index.css' integrity='sha256-fsqAKvNYgo9VQgSc4rD93SiW/AjKFwLtWlPi6qviBxY='/>"
        in rendered
    )


def test_generic_template():
    rendered = render_to_string("generic.html")
    assert (
        "<script src='/static/index.js' integrity='sha256-VROI/fAMCWgkTthVtzzvHtPkkxvpysdZbcqLdVMtwOI='></script>"
        in rendered
    )
    assert (
        "<link rel='stylesheet' href='/static/index.css' integrity='sha256-fsqAKvNYgo9VQgSc4rD93SiW/AjKFwLtWlPi6qviBxY='/>"
        in rendered
    )


def test_algorithms_template():
    rendered = render_to_string("algorithms.html")
    assert (
        "<script src='/static/index.js' integrity='sha384-dExnf54EbXTQ1VmweBEJRWX3MPT4xeDV5p71GIX2hpvV+8B/kzo3SObynuveYt9w'></script>"
        in rendered
    )
    assert (
        "<link rel='stylesheet' href='/static/index.css' integrity='sha512-7v9G7AKwpjnlEYhw9GdXu/9G8bq0PqM427/QmgH2TufqEUcjsANEoyCoOkpV8TBCnbQigwNKpMaZNskJG8Ejdw=='/>"
        in rendered
    )


@pytest.mark.parametrize("algorithm", utils.HASHERS.keys())
def test_js_algorithm(algorithm):
    assert f"integrity='{algorithm}-" in templatetags.sri_js("index.js", algorithm)


@pytest.mark.parametrize("algorithm", utils.HASHERS.keys())
def test_css_algorithm(algorithm):
    assert f"integrity='{algorithm}-" in templatetags.sri_css("index.css", algorithm)


@pytest.mark.parametrize("algorithm", utils.HASHERS.keys())
def test_generic_algorithm(algorithm):
    assert f"integrity='{algorithm}-" in templatetags.sri("index.css", algorithm)
    assert f"integrity='{algorithm}-" in templatetags.sri("index.js", algorithm)


def test_js():
    assert (
        templatetags.sri_js("index.js")
        == "<script src='/static/index.js' integrity='sha256-VROI/fAMCWgkTthVtzzvHtPkkxvpysdZbcqLdVMtwOI='></script>"
    )


def test_css():
    assert (
        templatetags.sri_css("index.css")
        == "<link rel='stylesheet' href='/static/index.css' integrity='sha256-fsqAKvNYgo9VQgSc4rD93SiW/AjKFwLtWlPi6qviBxY='/>"
    )


def test_generic():
    assert templatetags.sri_js("index.js") == templatetags.sri("index.js")
    assert templatetags.sri_css("index.css") == templatetags.sri("index.css")


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
