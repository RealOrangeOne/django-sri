# Django SRI

![CI](https://github.com/RealOrangeOne/django-sri/workflows/CI/badge.svg)
![PyPI](https://img.shields.io/pypi/v/django-sri.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-sri.svg)
![PyPI - Status](https://img.shields.io/pypi/status/django-sri.svg)
![PyPI - License](https://img.shields.io/pypi/l/django-sri.svg)


[Subresource Integrity](https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity) for Django.


## Installation

```
pip install django-sri
```

And add `sri` to your `INSTALLED_APPS`.

## Usage

### Template Tags

`django-sri` is designed to primarily be used through template tags:

```html
{% load sri %}

{% sri "index.js" %} <!-- Will output "<script src='/static/index.js' integrity='sha256-...'></script>" -->
{% sri "index.css" %} <!-- Will output "<link rel='stylesheet' href='/static/index.css' integrity='sha256-...'/>" -->
```

For performance, the hashes of files are cached in memory using [`lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache) for future requests.

__Note__: By default, integrity hashes are not output when `DEBUG` is `True`, as static files change a lot during local development. To override this, set `USE_SRI` to `True`.

#### Algorithms

The SRI standard supports 3 algorithms: sha256, sha384 and sha512. By default, SHA256 is used. To override this, supply an additional argument to the `sri` template tag (or the specific ones):

```html
{% load sri %}

{% sri "index.js" "sha512" %} <!-- Will output "<script src='/static/index.js' integrity='sha512-...'></script>" -->
```

The default algorithm can be changed by setting `SRI_ALGORITHM` to the required algorithm.

#### Just the integrity value

To retrieve just the integrity hash (the contents of the `integrity` attribute), you can use the `{% sri_integrity_static %}` tag, which supports the same arguments as the other tags.

### API

```python
from sri import calculate_integrity

calculate_integrity("/path/to/myfile.txt")  # "sha256-..."
```

### _"Does this work with [whitenoise](https://whitenoise.evans.io/en/stable/) or alike?"_

Yes. `django-sri` outputs the static file URL in the same way the builtin `static` template tag does. This means the correct cachebusted URLs are output.
