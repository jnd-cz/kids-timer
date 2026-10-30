import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'firmware'))
from timer_core import Timer, frame


class TimerTests(unittest.TestCase):
    def test_countdown_pause_and_alarm(self):
        t = Timer()
        t.add(61)
        t.update(0, lambda a, b: a - b)
        t.toggle()
        t.update(1500, lambda a, b: a - b)
        self.assertEqual(t.seconds, 60)
        t.toggle()
        t.update(5000, lambda a, b: a - b)
        t.toggle()
        t.update(64500, lambda a, b: a - b)
        self.assertEqual(t.seconds, 0)
        self.assertTrue(t.alarm)
        self.assertFalse(t.running)
        t.toggle()
        self.assertFalse(t.alarm)

    def test_clamping_and_mapping(self):
        t = Timer()
        t.add(100000)
        self.assertEqual(t.seconds, 5999)
        t.reset()
        t.add(-60)
        self.assertEqual(t.seconds, 0)
        bits = frame(61, running=True)
        self.assertEqual(bits[0], 1)
        self.assertEqual(bits[64], 1)
        self.assertEqual(sum(bits[:60]), 1)
        self.assertEqual(sum(bits[64:124]), 1)
        self.assertEqual(bits[142], 1)
        self.assertEqual(bits[62], 0)


if __name__ == '__main__':
    unittest.main()
