"""Tilt and movement helpers; acceleration inputs are in g."""
import math

# Board test: reflect the direction, then rotate 15 positions clockwise.
LEVEL_ROTATION_STEPS = 15
LEVEL_REVERSE = True


def tilt_degrees(xyz):
    x, y, z = xyz
    return math.degrees(math.atan2(math.sqrt(x * x + y * y), abs(z)))


def level_frame(xyz):
    from timer_core import text_frame
    x, y, z = xyz
    ax = math.degrees(math.atan2(x, abs(z)))
    ay = math.degrees(math.atan2(y, abs(z)))
    bits = text_frame('%02d%02d' % (min(90, int(abs(ax) + 0.5)),
                                    min(90, int(abs(ay) + 0.5))))
    bits[158], bits[159] = int(ax < -0.5), int(ay < -0.5)
    angle = tilt_degrees(xyz)
    if angle > 2:
        # Red ring is clockwise from 12; green ring is counter-clockwise.
        step = int((math.atan2(x, -y) * 30 / math.pi) + 60.5) % 60
        if LEVEL_REVERSE:
            step = -step
        step = (step + LEVEL_ROTATION_STEPS) % 60
        if angle <= 10:
            bits[(-step) % 60] = 1
        else:
            bits[64 + step] = 1
    return bits


class Pickup:
    """Compare consecutive alarm-time samples to a pre-alarm gravity baseline."""
    def __init__(self):
        self.baseline = None
        self.count = 0

    def observe(self, xyz):
        if self.baseline is None:
            self.baseline = xyz
        else:
            self.baseline = tuple(old * 0.8 + new * 0.2
                                  for old, new in zip(self.baseline, xyz))
        self.count = 0

    def moved(self, xyz):
        if self.baseline is None:
            return False
        distance2 = sum((a - b) ** 2 for a, b in zip(xyz, self.baseline))
        self.count = self.count + 1 if distance2 >= 0.35 ** 2 else 0
        return self.count >= 3

    def clear(self):
        self.baseline = None
        self.count = 0
