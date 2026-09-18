import shutil
from pathlib import Path
from typing import Any

import pytest
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.cache import caches
from django.core.management import call_command
from django.template import engines

import sri
from sri import Algorithm
from sri.templatetags import sri as templatetags

TEST_FILES = ["index.css", "index.js", "admin/js/core.js"]


def setup_function(*_: Any) -> None:
    for cache in caches.all():
        cache.clear()  # Clear cache between each test method
    shutil.rmtree(settings.STATIC_ROOT, ignore_errors=True)


def test_uses_default_algorithm() -> None:
    val = templatetags.sri_integrity("index.js")
    assert val.startswith(f"{Algorithm.get_default().value}-"), val


@pytest.mark.parametrize("file", TEST_FILES)
def test_get_static_path(file: str) -> None:
    file_path = sri.utils.get_static_path(file)

    assert file_path.exists()
    assert file_path.is_file()

    if "site-packages" not in str(file_path):
        assert file_path == Path("tests/static").joinpath(file).resolve()


def test_default_algorithm_exists() -> None:
    assert Algorithm.get_default() in sri.HASHERS


@pytest.mark.parametrize("algorithm", sri.Algorithm)
@pytest.mark.parametrize("file", TEST_FILES)
def test_hashes_are_consistent(algorithm: Algorithm, file: str) -> None:
    digest = sri.calculate_integrity_of_static(file, algorithm)
    caches["default"].clear()
    digest_2 = sri.calculate_integrity_of_static(file, algorithm)
    assert digest == digest_2


@pytest.mark.parametrize("algorithm", sri.Algorithm)
@pytest.mark.parametrize("file", TEST_FILES)
def test_integrity(algorithm: Algorithm, file: str) -> None:
    integrity = sri.calculate_integrity_of_static(file, algorithm)
    assert integrity.startswith(algorithm.value)


@pytest.mark.parametrize("file", TEST_FILES)
def test_disable_sri(settings: Any, file: str) -> None:
    settings.USE_SRI = False
    assert templatetags.sri_attrs(file) == ""


@pytest.mark.parametrize("file", TEST_FILES)
def test_unknown_algorithm(file: str) -> None:
    with pytest.raises(ValueError) as e:
        templatetags.sri_integrity(file, algorithm="md5")
    assert e.value.args[0] == "'md5' is not a valid Algorithm"


def test_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        templatetags.sri_integrity("foo.js")


def test_app_file() -> None:
    assert templatetags.sri_integrity("admin/js/core.js").startswith("sha256-")


@pytest.mark.parametrize("algorithm", sri.Algorithm)
@pytest.mark.parametrize("file", TEST_FILES)
def test_caches_hash(algorithm: Algorithm, file: str) -> None:
    file_path = sri.utils.get_static_path(file)
    cache_key = sri.utils.get_cache_key(file_path, algorithm)
    cache = caches["default"]

    assert cache.get(cache_key) is None
    digest = sri.calculate_hash(file_path, algorithm)
    assert cache.get(cache_key) == digest


@pytest.mark.parametrize("file", TEST_FILES)
def test_manifest_storage(settings: Any, file: str) -> None:
    settings.STORAGES = {
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
        }
    }
    call_command("collectstatic", interactive=False, clear=True, verbosity=0)

    file_path = sri.utils.get_static_path(file)

    assert file_path.exists()
    assert file_path.is_file()

    assert str(file_path).startswith(settings.STATIC_ROOT)
    assert not str(file_path).endswith(file)
    assert str(file_path).endswith(staticfiles_storage.stored_name(file))  # type: ignore[attr-defined]


@pytest.mark.parametrize("file", TEST_FILES)
def test_default_storage(file: str) -> None:
    # Test for issue #70
    call_command("collectstatic", interactive=False, clear=True, verbosity=0)

    file_path = sri.utils.get_static_path(file)

    assert file_path.exists()
    assert file_path.is_file()
    # If you rollback the changes outlined in issue #70, this
    # will fail as the path returned will be the source path
    # and not the destination path.
    assert str(file_path).startswith(settings.STATIC_ROOT)


@pytest.mark.parametrize(
    "template,result",
    [
        (
            "{% sri_attrs 'index.js' %}",
            ' crossorigin="anonymous" integrity="sha256-VROI/fAMCWgkTthVtzzvHtPkkxvpysdZbcqLdVMtwOI="',
        ),
        (
            "{% sri_attrs 'index.js' 'sha512' %}",
            ' crossorigin="anonymous" integrity="sha512-cw/Y369hULp54riZ5vM+t1Q/AkacZnq+JyqpmjXQox0gJKosqpa6CD3mqC2fQHokN13H0fqBQgnfb91lSFAOGQ=="',
        ),
        (
            "{% sri_attrs 'index.css' %}",
            ' crossorigin="anonymous" integrity="sha256-fsqAKvNYgo9VQgSc4rD93SiW/AjKFwLtWlPi6qviBxY="',
        ),
        (
            "{% sri_attrs 'index.woff2' %}",
            ' crossorigin="anonymous" integrity="sha256-hWU2c2zzSsvKYN7tGMnt3t3Oj7GwQZB2aLRhCWYbFSE="',
        ),
    ],
)
def test_attrs(template: str, result: str) -> None:
    assert (
        engines["django"].from_string("{% load sri %}" + template).render({}) == result
    )


@pytest.mark.parametrize(
    "template,result",
    [
        (
            "{{ sri_attrs('index.js') }}",
            ' crossorigin="anonymous" integrity="sha256-VROI/fAMCWgkTthVtzzvHtPkkxvpysdZbcqLdVMtwOI="',
        ),
        (
            "{{ sri_attrs('index.js', 'sha512') }}",
            ' crossorigin="anonymous" integrity="sha512-cw/Y369hULp54riZ5vM+t1Q/AkacZnq+JyqpmjXQox0gJKosqpa6CD3mqC2fQHokN13H0fqBQgnfb91lSFAOGQ=="',
        ),
        (
            "{{ sri_attrs('index.css') }}",
            ' crossorigin="anonymous" integrity="sha256-fsqAKvNYgo9VQgSc4rD93SiW/AjKFwLtWlPi6qviBxY="',
        ),
        (
            "{{ sri_attrs('index.woff2') }}",
            ' crossorigin="anonymous" integrity="sha256-hWU2c2zzSsvKYN7tGMnt3t3Oj7GwQZB2aLRhCWYbFSE="',
        ),
    ],
)
def test_attrs_jinja2(template: str, result: str) -> None:
    assert engines["jinja2"].from_string(template).render({}) == result


@pytest.mark.parametrize(
    "template,result",
    [
        (
            "{% sri_integrity 'index.js' %}",
            "sha256-VROI/fAMCWgkTthVtzzvHtPkkxvpysdZbcqLdVMtwOI=",
        ),
        (
            "{% sri_integrity 'index.js' 'sha512' %}",
            "sha512-cw/Y369hULp54riZ5vM+t1Q/AkacZnq+JyqpmjXQox0gJKosqpa6CD3mqC2fQHokN13H0fqBQgnfb91lSFAOGQ==",
        ),
        (
            "{% sri_integrity 'index.css' %}",
            "sha256-fsqAKvNYgo9VQgSc4rD93SiW/AjKFwLtWlPi6qviBxY=",
        ),
        (
            "{% sri_integrity 'index.woff2' %}",
            "sha256-hWU2c2zzSsvKYN7tGMnt3t3Oj7GwQZB2aLRhCWYbFSE=",
        ),
    ],
)
def test_integrity_tag(template: str, result: str) -> None:
    assert (
        engines["django"].from_string("{% load sri %}" + template).render({}) == result
    )


@pytest.mark.parametrize(
    "template,result",
    [
        (
            "{{ sri_integrity('index.js') }}",
            "sha256-VROI/fAMCWgkTthVtzzvHtPkkxvpysdZbcqLdVMtwOI=",
        ),
        (
            "{{ sri_integrity('index.js', 'sha512') }}",
            "sha512-cw/Y369hULp54riZ5vM+t1Q/AkacZnq+JyqpmjXQox0gJKosqpa6CD3mqC2fQHokN13H0fqBQgnfb91lSFAOGQ==",
        ),
        (
            "{{ sri_integrity('index.css') }}",
            "sha256-fsqAKvNYgo9VQgSc4rD93SiW/AjKFwLtWlPi6qviBxY=",
        ),
        (
            "{{ sri_integrity('index.woff2') }}",
            "sha256-hWU2c2zzSsvKYN7tGMnt3t3Oj7GwQZB2aLRhCWYbFSE=",
        ),
    ],
)
def test_integrity_tag_jinja2(template: str, result: str) -> None:
    assert engines["jinja2"].from_string(template).render({}) == result
