import importlib
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'firmware'))
from timer_core import fixed_frame, frame, text_frame


class FakeI2C:
    def __init__(self, *args, **kwargs):
        self.writes = []
        self.fail = False

    def writeto_mem(self, addr, reg, data):
        if self.fail:
            raise OSError('i2c')
        self.writes.append((addr, reg, data))

    def readfrom_mem(self, addr, reg, count):
        if self.fail:
            raise OSError('i2c')
        if addr == 0x1f and reg == 0:
            return b'\x25'
        if addr == 0x1f:
            return b'\x00\xc0\x00\x00\x00\x40'  # -1 g, 0 g, +1 g
        return b'\xe8\x03'  # 1000 counts


class FeatureTests(unittest.TestCase):
    def test_colon_and_fixed_point(self):
        bits = frame(0)
        self.assertEqual(bits[142:144], [1, 1])
        self.assertEqual(fixed_frame(-1.0), text_frame('-100', True))
        self.assertEqual(fixed_frame(4.12), text_frame(' 412', True))

    def test_sensor_setup_conversion_and_retry(self):
        machine = types.ModuleType('machine')
        machine.I2C = FakeI2C
        machine.Pin = lambda pin: pin
        previous = sys.modules.get('machine')
        sys.modules['machine'] = machine
        try:
            sys.modules.pop('sensors', None)
            sensors = importlib.import_module('sensors').Sensors()
            self.assertIsNone(sensors.light())
            self.assertAlmostEqual(sensors.light(), 460.8)
            self.assertIsNone(sensors.acceleration())
            self.assertEqual(sensors.acceleration(), (-1.0, 0.0, 1.0))
            sensors.bus.fail = True
            with self.assertRaises(OSError):
                sensors.light()
            self.assertFalse(sensors.light_ready)
            sensors.bus.fail = False
            self.assertIsNone(sensors.light())
        finally:
            sys.modules.pop('sensors', None)
            if previous is None:
                sys.modules.pop('machine', None)
            else:
                sys.modules['machine'] = previous


if __name__ == '__main__':
    unittest.main()
