import os
import shutil
from typing import Any

import pytest
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.cache import caches
from django.core.management import call_command
from django.template import engines

import sri
from sri.templatetags import sri as templatetags
from sri.utils import HASHERS

TEST_FILES = ["index.css", "index.js", "admin/js/core.js"]


def setup_function(*_: Any) -> None:
    shutil.rmtree(settings.STATIC_ROOT, ignore_errors=True)


def test_uses_default_algorithm() -> None:
    val = templatetags.sri_integrity("index.js")
    assert val.startswith(f"{sri.get_default_algorithm()}-"), val


@pytest.mark.parametrize("file", TEST_FILES)
def test_get_static_path(file: str) -> None:
    file_path = sri.utils.get_static_path(file)

    assert os.path.exists(file_path)
    assert os.path.isfile(file_path)

    if "site-packages" not in str(file_path):
        assert file_path == os.path.realpath(
            os.path.join(__file__, "../", "static", file)
        )


def test_default_algorithm_exists() -> None:
    assert sri.get_default_algorithm() in HASHERS


@pytest.mark.parametrize("algorithm", HASHERS.keys())
@pytest.mark.parametrize("file", TEST_FILES)
def test_hashes_are_consistent(algorithm: str, file: str) -> None:
    digest = sri.get_sri_of_static(file, algorithm)
    caches["default"].clear()
    digest_2 = sri.get_sri_of_static(file, algorithm)
    assert digest == digest_2


@pytest.mark.parametrize("algorithm", HASHERS.keys())
@pytest.mark.parametrize("file", TEST_FILES)
def test_integrity(algorithm: str, file: str) -> None:
    integrity = sri.get_sri_of_static(file, algorithm)
    assert integrity.startswith(f"{algorithm}-")


@pytest.mark.parametrize("file", TEST_FILES)
def test_disable_sri(settings: Any, file: str) -> None:
    settings.USE_SRI = False
    assert templatetags.sri_attrs(file) == ""


@pytest.mark.parametrize("algorithm", HASHERS.keys())
def test_unknown_algorithm(algorithm: str) -> None:
    assert templatetags.sri_integrity(TEST_FILES[0], algorithm.upper()).startswith(
        algorithm
    )
    assert templatetags.sri_integrity(TEST_FILES[0], algorithm.title()).startswith(
        algorithm
    )


@pytest.mark.parametrize("file", TEST_FILES)
def test_case_insensitive_algorithm(file: str) -> None:
    with pytest.raises(ValueError) as e:
        templatetags.sri_integrity(file, algorithm="md5")
    assert e.value.args[0] == "Unknown algorithm: md5"


def test_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        templatetags.sri_integrity("foo.js")


def test_app_file() -> None:
    assert templatetags.sri_integrity("admin/js/core.js").startswith("sha256-")


@pytest.mark.parametrize("algorithm", HASHERS.keys())
@pytest.mark.parametrize("file", TEST_FILES)
@pytest.mark.parametrize("use_sri", [True, False])
def test_caches_hash(settings: Any, algorithm: str, file: str, use_sri: bool) -> None:
    settings.USE_SRI = use_sri

    sri.utils._cached_get_sri_for_file.cache_clear()

    for _ in range(3):
        templatetags.sri_integrity(file, algorithm)

    cache_info = sri.utils._cached_get_sri_for_file.cache_info()

    if use_sri:
        assert cache_info.hits == 2
        assert cache_info.misses == 1
        assert cache_info.currsize == 1
    else:
        assert cache_info.currsize == 0


@pytest.mark.parametrize("file", TEST_FILES)
def test_manifest_storage(settings: Any, file: str) -> None:
    settings.STORAGES = {
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
        }
    }
    call_command("collectstatic", interactive=False, clear=True, verbosity=0)

    file_path = sri.utils.get_static_path(file)

    assert os.path.exists(file_path)
    assert os.path.isfile(file_path)

    assert file_path.startswith(settings.STATIC_ROOT)
    assert not file_path.endswith(file)
    assert file_path.endswith(staticfiles_storage.stored_name(file))  # type: ignore[attr-defined]


@pytest.mark.parametrize("file", TEST_FILES)
def test_default_storage(file: str) -> None:
    # Test for issue #70
    call_command("collectstatic", interactive=False, clear=True, verbosity=0)

    file_path = sri.utils.get_static_path(file)

    assert os.path.exists(file_path)
    assert os.path.isfile(file_path)
    # If you rollback the changes outlined in issue #70, this
    # will fail as the path returned will be the source path
    # and not the destination path.
    assert file_path.startswith(settings.STATIC_ROOT)


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
