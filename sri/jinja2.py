from jinja2 import Environment
from jinja2.ext import Extension

from sri.templatetags.sri import sri_integrity_static, sri_static


class SRIExtension(Extension):
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)

        environment.globals["sri_static"] = sri_static
        environment.globals["sri_integrity_static"] = sri_integrity_static


# Shorthand
sri = SRIExtension
