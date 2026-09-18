from jinja2 import Environment
from jinja2.ext import Extension

from sri.templatetags.sri import sri_attrs, sri_integrity


class SRIExtension(Extension):
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)

        environment.globals["sri_attrs"] = sri_attrs
        environment.globals["sri_integrity"] = sri_integrity


# Shorthand
sri = SRIExtension
