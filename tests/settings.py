import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "sri",
    "tests",
    "django.contrib.admin",
    "django.contrib.contenttypes",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {},
    },
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"environment": "tests.utils.create_jinja2_environment"},
    },
]

SECRET_KEY = "abcde12345"

STATIC_ROOT = os.path.join(BASE_DIR, "tests", "collected-static")
STATIC_URL = "/static/"
