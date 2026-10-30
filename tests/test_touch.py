import importlib
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'firmware'))


class FakePin:
    IN = 0
    def __init__(self, number, mode):
        self.number = number
    def init(self, mode):
        pass


class FakeSM:
    readings = [10, 10]
    def __init__(self, i, *args, **kwargs):
        self.i = i
    def active(self, value):
        pass
    def put(self, value):
        pass
    def get(self):
        return 1023 - self.readings[self.i]


class TouchTests(unittest.TestCase):
    def test_calibration_detection_and_recalibration(self):
        machine = types.ModuleType('machine')
        machine.Pin = FakePin
        rp2 = types.ModuleType('rp2')
        rp2.PIO = types.SimpleNamespace(OUT_LOW=0)
        rp2.asm_pio = lambda **kwargs: lambda f: f
        rp2.StateMachine = FakeSM
        saved = {k: sys.modules.get(k) for k in ('machine', 'rp2')}
        sys.modules.update(machine=machine, rp2=rp2)
        try:
            sys.modules.pop('touch', None)
            pads = importlib.import_module('touch').TouchPads()
            FakeSM.readings = [10, 10]
            for _ in range(16):
                self.assertIsNone(pads.read()[1])
            FakeSM.readings = [16, 10]
            self.assertEqual(pads.read()[1], [True, False])
            pads.reset()
            self.assertIsNone(pads.read()[1])
            pads.close()
        finally:
            sys.modules.pop('touch', None)
            for name, module in saved.items():
                if module is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = module


if __name__ == '__main__':
    unittest.main()
