"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject

As much as possible has been moved into setup.cfg and pyproject.toml.
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
        long_description=long_description,
        py_modules=['pwm_lightness'],  # Why doesn't this work in setup.cfg?!?
)
