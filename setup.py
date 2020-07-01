"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject

As much as possible has been moved into setup.cfg and pyproject.toml.
"""

from setuptools import setup, find_packages

setup(
        py_modules=['pwm_lightness'],  # Why doesn't this work in setup.cfg?!?
)
