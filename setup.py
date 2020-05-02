from setuptools import setup, find_packages

with open("README.md") as f:
    readme = f.read()

setup(
    name="django-sri",
    version="0.1.1",
    url="https://github.com/RealOrangeOne/django-sri",
    author="Jake Howard",
    description="Subresource Integrity for Django",
    long_description=readme,
    long_description_content_type="text/markdown",
    license="BSD",
    packages=find_packages(include=["sri"]),
    package_data={"sri": ["py.typed"]},
    install_requires=["Django>=2.2"],
    python_requires=">=3.6",
)
