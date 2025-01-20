from jinja2 import Environment


def create_jinja2_environment(**options):
    env = Environment(**options)
    env.add_extension("sri.jinja2.sri")
    return env
