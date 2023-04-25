# SPDX-FileCopyrightText: Copyright (c) 2020 Gregory P. Smith
# SPDX-License-Identifier: Apache-2.0
#
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

"""`pwm_lightness`
=================================================

Provides lightness correction tables for eyeball pleasing LED brightness.

Want a smooth fade on your pulsing LEDs or get lovely antialiasing on LED
matrix fonts?  You need to correct your raw linear brightness values for
human eyeball persistence of vision perception sensitivity.

Otherwise known as the CIE 1931 Lightness curve.

code-block:: python

   >>> pwm_lightness.get_pwm_table(42)
   [0, ..., 42]

Returns a table mapping integer values 0-255 to brightness adjusted values in
the range 0-42.  Parameters control both the range of output values and the
table size (range of lookup table indices aka "input" values).  All integers.
Tables are cached to avoid recomputation.
"""

try:
    from typing import Sequence
except ImportError:
    pass

__version__ = "1.1.0beta1"
__repo__ = "https://github.com/gpshead/pwm_lightness.git"

_pwm_tables = {}  # Our cache.


def get_pwm_table(max_output: int, max_input: int = 255) -> "Sequence[int]":
    """Returns a table mapping 0..max_input to int PWM values.

    Computed upon the first call with given values, cached thereafter.

    :param int max_output: The maximum output value; think of this as raw PWM
       duty cycle or brightness when using this with LEDs.
    :param int max_input: The maximum index into the lookup table. Indices are
       zero based so the returned table will have max_input+1 length.  Defaults
       to :const:`255`.
    """
    assert max_output > 0
    assert max_input > 0
    table = _pwm_tables.get((max_output, max_input))
    if table:
        return table
    value_gen = (
        round(_cie1931(l_star / max_input) * max_output)
        for l_star in range(max_input + 1)
    )
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
        return l_star / 903.3  # Anything suggesting 902.3 has a typo.
    return ((l_star + 16) / 116) ** 3


if __name__ == "__main__":
    import sys

    try:
        _table = get_pwm_table(*(int(arg) for arg in sys.argv[1:]))
    except Exception:
        # pylint: disable=raise-missing-from
        raise RuntimeError(
            " Usage:  python3 -m pwm_lightness MAX_OUTPUT [MAX_INPUT]\n"
            "    MAX_OUTPUT:  The maximum integer output value (brightness).\n"
            "    MAX_INPUT:   The maximum index into the lookup table.\n"
        )
    print(",".join(str(v) for v in _table))
