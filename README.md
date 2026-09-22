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

`django-sri` is intended to primarily be used through template tags:

```html
{% load sri %}

<!-- Add the required integrity attributes to the relevant tag -->
<link rel="stylesheet" href="{% static 'index.css' %}" {% sri_attrs 'index.css' %} />
<script src="{% static 'index.js %}" {% sri_attrs 'index.js' %}></script>

<!-- Or, get the integrity value directly -->
<script src="{% static 'index.js %}" integrity="{% sri_integrity 'index.js' %}" crossorigin="anonymous"></script>
<link rel="stylesheet" href="{% static 'index.css' %}" integrity="{% sri_integrity 'index.css' %}" crossorigin="anonymous" />
```

__Note__: By default, `sri_attrs` does not output when `DEBUG` is `True`, as static files change a lot during local development. To override this, set `USE_SRI` to `True`. `sri_integrity` always outputs.

For performance, the hashes of files are caches in Django's [caching framework](https://docs.djangoproject.com/en/dev/topics/cache/). It will attempt to use the "sri" cache, but fall back to "default" if it doesn't exist. The cache keys are the hash of the file path in the specified algorithm in hex. Caches are stored for as long as `DEFAULT_TIMEOUT` is set to.

### Algorithms

The SRI standard supports 3 algorithms: SHA256, SHA384 and SHA512. By default, SHA256 is used. To override this, supply an additional `algorithm` argument to the template tag:

```html
{% load sri %}

{% sri_integrity "index.js" algorithm="sha512" %} <!-- Will output "integrity='sha512-...'" -->
```

The default algorithm can be changed by setting `SRI_ALGORITHM` to the required algorithm.

### API

Outside of templates, the relevant integrity values can be retrieved using `get_sri` or `get_sri_of_static`.

`get_sri` accepts the path to any file, whereas `get_sri_of_static` resolves static files similar to `{% static %}`.

```python
from pathlib import Path
from sri import get_sri, get_sri_of_static

get_sri(Path("/path/to/myfile.txt"))  # "sha256-..."
get_sri(Path("/path/to/myfile.txt"), "sha512")  # "sha512-..."

get_sri_of_static("index.js")  # "sha256-..."
get_sri_of_static("index.js", "sha512")  # "sha512-..."
```

### _"Does this work with [whitenoise](https://whitenoise.evans.io/en/stable/) or alike?"_

Yes. `django-sri` outputs the static file URL in the same way the builtin `static` template tag does. This means the correct cachebusted URLs are output.

When using a manifest `STATICFILES_STORAGE`, `django-sri` will automatically retrieve the hashed and post-processed file as opposed to the original.

### `jinja2`

Support for `jinja2` templates is provided using the `sri.jinja2.sri` extension, which adds the documented Django template tags as global functions. These functions work identically to the Django template versions.
