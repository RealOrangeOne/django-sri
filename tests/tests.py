from pathlib import Path

import pytest
from django.template.loader import render_to_string

from sri import utils
from sri.templatetags import sri as templatetags

TEST_FILES = ["index.css", "index.js", "admin/js/core.js"]


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


@pytest.mark.parametrize("algorithm", utils.Algorithm)
@pytest.mark.parametrize("file", TEST_FILES)
def test_generic_algorithm(algorithm, file):
    assert f'integrity="{algorithm.value}-' in templatetags.sri_static(file, algorithm)


@pytest.mark.parametrize("file", TEST_FILES)
def test_get_static_path(file):
    file_path = utils.get_static_path(file)

    assert file_path.exists()
    assert file_path.is_file()

    if "site-packages" not in str(file_path):
        assert file_path == Path("tests/static").joinpath(file).resolve()


def test_default_algorithm_exists():
    assert utils.DEFAULT_ALGORITHM in utils.HASHERS


@pytest.mark.parametrize("algorithm", utils.Algorithm)
@pytest.mark.parametrize("file", TEST_FILES)
def test_hashes_are_consistent(algorithm, file):
    digest = utils.calculate_hash.__wrapped__(utils.get_static_path(file), algorithm)
    digest_2 = utils.calculate_hash.__wrapped__(utils.get_static_path(file), algorithm)
    assert digest == digest_2


@pytest.mark.parametrize("algorithm", utils.Algorithm)
@pytest.mark.parametrize("file", TEST_FILES)
def test_integrity(algorithm, file):
    integrity = utils.calculate_integrity(utils.get_static_path(file), algorithm)
    assert integrity.startswith(algorithm.value)


@pytest.mark.parametrize("file", TEST_FILES)
def test_disable_sri(file):
    original_value = templatetags.USE_SRI
    try:
        templatetags.USE_SRI = False
        assert "integrity" not in templatetags.sri_static(file)
    finally:
        templatetags.USE_SRI = original_value


@pytest.mark.parametrize("algorithm", utils.Algorithm)
@pytest.mark.parametrize("file", TEST_FILES)
def test_sri_integrity_static(algorithm, file):
    assert templatetags.sri_integrity_static(file, algorithm).startswith(
        f"{algorithm.value}-"
    )


@pytest.mark.parametrize("file", TEST_FILES)
def test_unknown_algorithm(file):
    with pytest.raises(ValueError) as e:
        templatetags.sri_static(file, "md5")
    assert e.value.args[0] == "'md5' is not a valid Algorithm"


def test_unknown_extension():
    with pytest.raises(KeyError) as e:
        templatetags.sri_static("index.md", utils.DEFAULT_ALGORITHM)
    assert e.value.args[0] == "md"


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        templatetags.sri_static("foo.js", utils.DEFAULT_ALGORITHM)


def test_app_file():
    templatetags.sri_static("admin/js/core.js", utils.DEFAULT_ALGORITHM)
