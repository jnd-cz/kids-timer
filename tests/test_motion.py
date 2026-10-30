import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'firmware'))
from motion import Pickup, tilt_degrees


class MotionTests(unittest.TestCase):
    def test_level_and_vertical(self):
        self.assertAlmostEqual(tilt_degrees((0, 0, 1)), 0)
        self.assertAlmostEqual(tilt_degrees((1, 0, 0)), 90)
        self.assertAlmostEqual(tilt_degrees((0, 0, -1)), 0)

    def test_pickup_requires_baseline_and_sustained_change(self):
        pickup = Pickup()
        self.assertFalse(pickup.moved((1, 0, 0)))
        pickup.observe((0, 0, 1))
        self.assertFalse(pickup.moved((0.05, 0, 1)))
        self.assertFalse(pickup.moved((0.5, 0, 0.866)))
        self.assertFalse(pickup.moved((0, 0, 1)))  # transient does not count
        self.assertFalse(pickup.moved((0.5, 0, 0.866)))
        self.assertFalse(pickup.moved((0.5, 0, 0.866)))
        self.assertTrue(pickup.moved((0.5, 0, 0.866)))
        pickup.clear()
        self.assertFalse(pickup.moved((1, 0, 0)))


if __name__ == '__main__':
    unittest.main()
