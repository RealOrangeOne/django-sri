from django.template.loader import render_to_string


def test_simple():
    rendered = render_to_string("simple.html")
    assert "<script src='/static/index.js'></script>" in rendered
    assert "<link rel='stylesheet' href='/static/index.css' />" in rendered
