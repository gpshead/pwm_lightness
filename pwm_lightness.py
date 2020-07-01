# Copyright 2020 Gregory P. Smith
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Provides lightness correction tables for eyeball pleasing LED brightness.

Want a smooth fade on your pulsing LEDs or get lovely antialiasing on LED
matrix fonts?  You need to correct your raw linear brightness values for
human eyeball persistence of vision perception sensitivity.

Otherwise known as the CIE 1931 Lightness curve.

Usage:

>>> pwm_lightness.get_pwm_table(42)

Returns a table mapping integer values 0-255 to brightness adjusted values
in the range 0-42.  Parameters control both the table size (range of input
values) and the range of output values.  All integers.  Tables are cached
to avoid recomputation.
"""

try:
    from typing import Sequence
except ImportError:
    pass

_pwm_tables = {}  # Our cache.


def get_pwm_table(max_output: int,
                  max_input: int = 255) -> 'Sequence[int]':
    """Returns a table mapping 0..max_input to int PWM values.

    Computed upon the first call with given value, cached thereafter.
    """
    assert max_output > 0
    assert max_input > 0
    table = _pwm_tables.get((max_output, max_input))
    if table:
        return table
    value_gen = (round(_cie1931(l_star/max_input) * max_output)
                 for l_star in range(max_input+1))
    table = bytes(value_gen) if max_output <= 255 else tuple(value_gen)
    _pwm_tables[(max_output, max_input)] = table
    return table


def clear_table_cache():
    """Empties the cache of get_pwm_tables() return values."""
    _pwm_tables.clear()


# CIE 1931 Lightness curve calculation.
# derived from https://jared.geek.nz/2013/feb/linear-led-pwm @ 2020-06
# License: MIT
# additional reference
# https://www.photonstophotos.net/GeneralTopics/Exposure/Psychometric_Lightness_and_Gamma.htm
def _cie1931(l_star: float) -> float:
    l_star *= 100
    if l_star <= 8:
        return l_star/903.3  # Anything suggesting 902.3 has a typo.
    return ((l_star+16)/116)**3
