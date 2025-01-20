import shutil
from pathlib import Path

import pytest
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.cache import caches
from django.core.management import call_command
from django.template.loader import render_to_string

import sri
from sri.algorithm import Algorithm
from sri.templatetags import sri as templatetags

TEST_FILES = ["index.css", "index.js", "admin/js/core.js"]


def setup_function(*_):
    for cache in caches.all():
        cache.clear()  # Clear cache between each test method
    shutil.rmtree(settings.STATIC_ROOT, ignore_errors=True)


def test_simple_template():
    rendered = render_to_string("simple.html")
    assert (
        '<script crossorigin="anonymous" integrity="sha256-VROI/fAMCWgkTthVtzzvHtPkkxvpysdZbcqLdVMtwOI=" src="/static/index.js"></script>'
        in rendered
    )
    assert (
        '<link crossorigin="anonymous" href="/static/index.css" integrity="sha256-fsqAKvNYgo9VQgSc4rD93SiW/AjKFwLtWlPi6qviBxY=" rel="stylesheet" type="text/css">'
        in rendered
    )


def test_complex_template():
    rendered = render_to_string("complex.html")
    assert (
        '<script crossorigin="anonymous" integrity="sha256-VROI/fAMCWgkTthVtzzvHtPkkxvpysdZbcqLdVMtwOI=" src="/static/index.js" defer async></script>'
        in rendered
    )
    assert (
        '<link as="font" crossorigin="anonymous" href="/static/index.woff2" integrity="sha256-hWU2c2zzSsvKYN7tGMnt3t3Oj7GwQZB2aLRhCWYbFSE=" preload>'
        in rendered
    ), rendered


def test_algorithms_template():
    rendered = render_to_string("algorithms.html")
    assert (
        '<script crossorigin="anonymous" integrity="sha384-dExnf54EbXTQ1VmweBEJRWX3MPT4xeDV5p71GIX2hpvV+8B/kzo3SObynuveYt9w" src="/static/index.js"></script>'
        in rendered
    )
    assert (
        '<link crossorigin="anonymous" href="/static/index.css" integrity="sha512-7v9G7AKwpjnlEYhw9GdXu/9G8bq0PqM427/QmgH2TufqEUcjsANEoyCoOkpV8TBCnbQigwNKpMaZNskJG8Ejdw==" rel="stylesheet" type="text/css">'
        in rendered
    )


def test_jinja2_template():
    rendered = render_to_string("complex.j2")
    assert (
        '<script crossorigin="anonymous" integrity="sha256-VROI/fAMCWgkTthVtzzvHtPkkxvpysdZbcqLdVMtwOI=" src="/static/index.js" defer async></script>'
        in rendered
    )
    assert (
        '<link as="font" crossorigin="anonymous" href="/static/index.woff2" integrity="sha256-hWU2c2zzSsvKYN7tGMnt3t3Oj7GwQZB2aLRhCWYbFSE=" preload>'
        in rendered
    )


@pytest.mark.parametrize("algorithm", sri.Algorithm)
@pytest.mark.parametrize("file", TEST_FILES)
def test_generic_algorithm(algorithm, file):
    val = templatetags.sri_integrity_static(file, algorithm)
    assert val.startswith(f"{algorithm.value}-"), val


def test_default_algorithm():
    val = templatetags.sri_integrity_static("index.js")
    assert val.startswith(f"{Algorithm.get_default().value}-"), val


@pytest.mark.parametrize("file", TEST_FILES)
def test_get_static_path(file):
    file_path = sri.utils.get_static_path(file)

    assert file_path.exists()
    assert file_path.is_file()

    if "site-packages" not in str(file_path):
        assert file_path == Path("tests/static").joinpath(file).resolve()


def test_default_algorithm_exists():
    assert Algorithm.get_default() in sri.hashers.HASHERS


@pytest.mark.parametrize("algorithm", sri.Algorithm)
@pytest.mark.parametrize("file", TEST_FILES)
def test_hashes_are_consistent(algorithm, file):
    digest = sri.hashers.calculate_hash(sri.utils.get_static_path(file), algorithm)
    caches["default"].clear()
    digest_2 = sri.hashers.calculate_hash(sri.utils.get_static_path(file), algorithm)
    assert digest == digest_2


@pytest.mark.parametrize("algorithm", sri.Algorithm)
@pytest.mark.parametrize("file", TEST_FILES)
def test_integrity(algorithm, file):
    integrity = sri.integrity.calculate_integrity(
        sri.utils.get_static_path(file), algorithm
    )
    assert integrity.startswith(algorithm.value)


@pytest.mark.parametrize("file", TEST_FILES)
def test_disable_sri(file):
    original_value = templatetags.USE_SRI
    try:
        templatetags.USE_SRI = False
        assert "integrity" not in templatetags.sri_static(file)
    finally:
        templatetags.USE_SRI = original_value


@pytest.mark.parametrize("algorithm", sri.Algorithm)
@pytest.mark.parametrize("file", TEST_FILES)
def test_sri_integrity_static(algorithm, file):
    assert templatetags.sri_integrity_static(file, algorithm).startswith(
        f"{algorithm.value}-"
    )


@pytest.mark.parametrize("file", TEST_FILES)
def test_unknown_algorithm(file):
    with pytest.raises(ValueError) as e:
        templatetags.sri_static(file, algorithm="md5")
    assert e.value.args[0] == "'md5' is not a valid Algorithm"


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        templatetags.sri_static("foo.js")


def test_app_file():
    templatetags.sri_static("admin/js/core.js")


@pytest.mark.parametrize("algorithm", sri.Algorithm)
@pytest.mark.parametrize("file", TEST_FILES)
def test_caches_hash(algorithm, file):
    file_path = sri.utils.get_static_path(file)
    cache_key = sri.hashers.get_cache_key(file_path, algorithm)
    cache = caches["default"]

    assert cache.get(cache_key) is None
    digest = sri.hashers.calculate_hash(file_path, algorithm)
    assert cache.get(cache_key) == digest


@pytest.mark.parametrize("file", TEST_FILES)
def test_manifest_storage(settings, file):
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
    assert str(file_path).endswith(staticfiles_storage.stored_name(file))


@pytest.mark.parametrize("file", TEST_FILES)
def test_default_storage(file):
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
    "empty,extra,output",
    [
        ([], {}, ""),
        (["defer"], {}, " defer"),
        (["defer", "async"], {}, " defer async"),
        ([], {"type": "text/javascript"}, ' type="text/javascript"'),
        (["defer"], {"type": "text/javascript"}, ' type="text/javascript" defer'),
    ],
)
def test_format_attrs(empty, extra, output: str) -> None:
    elem = templatetags.format_attrs(*empty, **extra)
    assert elem == output, elem
