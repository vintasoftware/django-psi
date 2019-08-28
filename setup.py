import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

setup(
    name='django-psi',
    version='0.0.1',
    packages=['djangopsi'],
    description='TODO description', # XXX
    long_description=README,
    author='Tiago da Costa Melo',
    author_email='tiagodacostamelo@gmail.com',
    url='https://github.com/tcostam/django-psi/',
    license='MIT',
    install_requires=[
        'Django>=2.0',
        'django-model-utils',
        'google-api-python-client',
    ]
)
