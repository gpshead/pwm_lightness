#!/usr/bin/env python3
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
#
# SPDX-FileCopyrightText: 2020 Gregory P. Smith
# SPDX-License-Identifier: Apache-2.0

"""Unittests for pwm_lightness."""

import sys
import unittest
import pwm_lightness


class TestPWMLightness(unittest.TestCase):
    def tearDown(self):
        pwm_lightness.clear_table_cache()
        self.assertFalse(pwm_lightness._pwm_tables)  # pylint: disable=protected-access

    def test_get_pwm_table_defaults(self):
        byte_curve = pwm_lightness.get_pwm_table(255)
        self.assertEqual(byte_curve[0], 0)
        self.assertEqual(byte_curve[255], 255)
        self.assertEqual(len(byte_curve), 256)
        self.assertIsInstance(byte_curve, bytes)  # Space efficient.

    def test_get_pwm_table_2345(self):
        curve = pwm_lightness.get_pwm_table(max_output=2345, max_input=99)
        self.assertEqual(curve[0], 0)
        self.assertEqual(curve[99], 2345)
        self.assertEqual(len(curve), 100)
        self.assertNotIsInstance(curve, bytes)  # tuple, list, don't care.

    def test_18_percent_grey(self):
        """18% lightness is the 50%-light/dark visual reference."""
        curve_100 = pwm_lightness.get_pwm_table(100, max_input=100)
        self.assertEqual(curve_100[50], 18)

    def test_table_cache(self):
        curve_300_a = pwm_lightness.get_pwm_table(max_output=300)
        curve_300_50 = pwm_lightness.get_pwm_table(max_output=300, max_input=50)
        curve_50_300 = pwm_lightness.get_pwm_table(max_output=50, max_input=300)
        curve_50_50_a = pwm_lightness.get_pwm_table(max_output=50, max_input=50)
        curve_300_b = pwm_lightness.get_pwm_table(max_output=300)
        curve_50_50_b = pwm_lightness.get_pwm_table(max_output=50, max_input=50)
        self.assertNotEqual(curve_300_50, curve_50_300)
        self.assertNotEqual(curve_300_a, curve_300_50)
        self.assertNotEqual(curve_300_a, curve_50_300)
        self.assertIs(curve_300_a, curve_300_b)
        self.assertIs(curve_50_50_a, curve_50_50_b)
        pwm_lightness.clear_table_cache()
        curve_300_c = pwm_lightness.get_pwm_table(max_output=300)
        self.assertEqual(curve_300_a, curve_300_c)
        self.assertIsNot(curve_300_a, curve_300_c)

    @unittest.skipIf(not sys.executable, "sys.executable required")
    def test_cli_help(self):
        # pylint: disable=import-outside-toplevel,subprocess-run-check
        import subprocess

        proc = subprocess.run(
            [sys.executable, "-m", "pwm_lightness"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn(b"Usage: ", proc.stderr)

    @unittest.skipIf(not sys.executable, "sys.executable required")
    def test_command_line_interface(self):
        # pylint: disable=import-outside-toplevel,subprocess-run-check
        import subprocess

        # 0 is an invalid max_output value, error
        proc = subprocess.run(
            [sys.executable, "-m", "pwm_lightness", "0", "255"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn(b"Usage: ", proc.stderr)
        # success
        proc = subprocess.run(
            [sys.executable, "-m", "pwm_lightness", "42"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertNotIn(b"Usage:", proc.stderr)
        self.assertTrue(proc.stdout.startswith(b"0,"), proc.stdout)
        self.assertIn(b",42", proc.stdout)


if __name__ == "__main__":
    unittest.main()
