import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.md")).read()

setup(
    name="django-psi",
    version="0.0.1",
    packages=["djangopsi"],
    description="TODO description",  # XXX
    long_description=README,
    author="Tiago da Costa Melo",
    author_email="tiago@vinta.com.br",
    url="https://github.com/vintasoftware/django-psi/",
    license="MIT",
    install_requires=["django-model-utils>=3.2.0", "google-api-python-client>=1.7.11"],
)
