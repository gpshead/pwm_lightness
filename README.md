Provides lightness correction tables for eyeball pleasing LED brightness.

Want a smooth fade on your pulsing LEDs or get lovely antialiasing on LED
matrix fonts?  You need to correct your raw linear brightness values for
human eyeball persistence of vision perception sensitivity.

Otherwise known as the [CIE 1931 Lightness curve](https://www.photonstophotos.net/GeneralTopics/Exposure/Psychometric_Lightness_and_Gamma.htm).

It is also [covered in many books](https://www.google.com/search?q=903.3+116+formula&tbm=bks).

Fade a PWM LED out smoothly:

```
PWM = pwm_lightness.get_pwm_table(0xffff, max_input=100)
output_pin = pulseio.PWMOut(...)  # or analogio.AnalogOut(...)
for v in range(100, -1, -1):
    output_pin.value = PWM[v]
    time.sleep(0.01)
```

Usage with Pillow to make those antialiased fonts shine:

```
BRIGHTNESS = 120  # Out of 255, the default max_input.
PWM = pwm_lightness.get_pwm_table(BRIGHTNESS)
font = PIL.ImageFont.truetype('fonts/RobotoCondensed-Regular.ttf', 15)
image = PIL.Image.new('L', (16,9), 0)
draw = PIL.ImageDraw.Draw(image)
# fill=255 gives us the most antialiasing detail, we control overall
# brightness via our PWM table.
draw.text((0,0), '?', fill=255, font=font)
image = image.point(PWM)  # Corrects linear values for PWM lightness.
adafruit_is31fl3731_matrix.image(image)  # Send pixels to your LED display.
```

This code should work fine on a CircuitPython or MicroPython microcontroller so
long as you have floating point enabled in your build.  Though for those
environments recomputing a table on device may be considered silly.  Precompute
the ones you need and store them as data to save precious RAM.
