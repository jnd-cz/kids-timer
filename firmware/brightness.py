"""Bounded ambient-light brightness policy."""
import math

MIN_BRIGHTNESS = 0.005
MAX_BRIGHTNESS = 0.05


def brightness_target(lux):
    # Log response maps 0..1000 lux to 0.5..5% on-time.
    fraction = math.log(1 + max(0, lux)) / math.log(1001)
    return MIN_BRIGHTNESS + (MAX_BRIGHTNESS - MIN_BRIGHTNESS) * min(1, fraction)


def smooth_brightness(current, target):
    # Called every 500 ms: approximately 5 s time constant.
    return current + 0.1 * (target - current)
