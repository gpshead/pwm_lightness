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
 https://www.photonstophotos.net/GeneralTopics/Exposure/Psychometric_Lightness_and_Gamma.htm
Also covered in many books
 https://www.google.com/search?q=903.3+116+formula&tbm=bks

Fade a PWM LED out smoothly:

>>> PWM = pwm_lightness.get_pwm_table(0xffff, max_input=100)
>>> output_pin = pulseio.PWMOut(...)  # or analogio.AnalogOut(...)
>>> for v in range(100, -1, -1):
...     output_pin.value = PWM[v]
...     time.sleep(0.01)

Usage with Pillow:

>>> BRIGHTNESS = 120  # Out of 255, the default max_input.
>>> PWM = pwm_lightness.get_pwm_table(BRIGHTNESS)
>>> font = PIL.ImageFont.truetype('fonts/RobotoCondensed-Regular.ttf', 15)
>>> image = PIL.Image.new('L', (16,9), 0)
>>> draw = PIL.ImageDraw.Draw(image)
>>> # fill=255 gives us the most antialiasing detail, we control overall
>>> # brightness via our PWM table.
>>> draw.text((0,0), '?', fill=255, font=font)
>>> image = image.point(PWM)  # Corrects linear values for PWM lightness.
>>> adafruit_is31fl3731_matrix.image(image)  # Send pixels to your LED display.
"""

_pwm_tables = {}  # Our cache.


def get_pwm_table(max_output: int,
                  max_input: int = 255) -> 'typing.Sequence[int]':
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
