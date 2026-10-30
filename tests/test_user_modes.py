import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'firmware'))
from brightness import brightness_target, smooth_brightness
from motion import level_frame


class UserModesTests(unittest.TestCase):
    def test_brightness_bounds_and_smoothing(self):
        self.assertAlmostEqual(brightness_target(0), 0.005)
        self.assertAlmostEqual(brightness_target(1000), 0.05)
        self.assertAlmostEqual(brightness_target(100000), 0.05)
        self.assertGreater(brightness_target(100), brightness_target(10))
        self.assertAlmostEqual(smooth_brightness(0.05, 0.005), 0.0455)

    def test_observed_direction_reflection(self):
        # Before correction D245, D230, D215 and D200 lit respectively.
        # After reflection and rotation they indicate D230, D245, D200, D215.
        import math
        for previous_step, expected_step in ((45, 30), (30, 45), (15, 0), (0, 15)):
            angle = previous_step * math.pi / 30
            x, y = math.sin(angle), -math.cos(angle)
            bits = level_frame((x, y, 1))
            self.assertEqual(bits[64 + expected_step], 1)
            self.assertEqual(sum(bits[64:124]), 1)

    def test_level_ring_and_axis_signs(self):
        flat = level_frame((0, 0, 1))
        self.assertEqual(sum(flat[:60]) + sum(flat[64:124]), 0)
        small = level_frame((0.09, 0, 1))
        self.assertEqual(small[0], 1)  # green ring runs counter-clockwise
        self.assertEqual(sum(small[64:124]), 0)
        large = level_frame((0, -0.5, 1))
        self.assertEqual(large[79], 1)  # red ring runs clockwise
        self.assertEqual(sum(large[:60]), 0)
        self.assertEqual(large[159], 1)  # negative Y marked by DP4


if __name__ == '__main__':
    unittest.main()

class TouchDisplayTests(unittest.TestCase):
    def test_both_pads_and_independent_timeout(self):
        from timer_core import touch_frame, text_frame
        self.assertEqual(touch_frame(None, None, None), text_frame('----'))
        bits = touch_frame([15, 20], [10, 10], [True, False])
        expected = text_frame('5099')
        expected[0] = 1
        self.assertEqual(bits, expected)
        self.assertEqual(touch_frame([1024, 10], [10, 10], [False, True])[64], 1)
        expected = text_frame('EE00')
        expected[64] = 1
        self.assertEqual(touch_frame([1024, 10], [10, 10], [False, True]), expected)
