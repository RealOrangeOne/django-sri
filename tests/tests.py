from django.template.loader import render_to_string
from django.test import SimpleTestCase


class SRITestCase(SimpleTestCase):
    def test_simple(self):
        rendered = render_to_string("simple.html")
        self.assertIn("<script src='/static/index.js'></script>", rendered)
        self.assertIn("<link rel='stylesheet' href='/static/index.css' />", rendered)
