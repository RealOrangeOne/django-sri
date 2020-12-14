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
]

SECRET_KEY = "abcde12345"

STATIC_ROOT = os.path.join(BASE_DIR, "tests", "static")
STATIC_URL = "/static/"
