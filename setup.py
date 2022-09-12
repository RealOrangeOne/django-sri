from setuptools import find_packages, setup

with open("README.md") as f:
    readme = f.read()

setup(
    name="django-sri",
    version="0.5.0",
    url="https://github.com/RealOrangeOne/django-sri",
    author="Jake Howard",
    description="Subresource Integrity for Django",
    long_description=readme,
    long_description_content_type="text/markdown",
    license="BSD",
    packages=find_packages(include=["sri*"]),
    package_data={"sri": ["py.typed"]},
    install_requires=["Django>=3.2"],
    python_requires=">=3.8",
    keywords="django subresource integrity sri",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development",
        "Typing :: Typed",
    ],
)
