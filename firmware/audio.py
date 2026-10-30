"""Non-blocking test tones using the amplifier input PWM."""
from machine import Pin, PWM
from time import ticks_add, ticks_diff


class Audio:
    def __init__(self):
        self.amp = Pin(15, Pin.OUT, value=0)
        self.pwm = PWM(Pin(14))
        self.pwm.duty_u16(0)
        self.until = None

    def beep(self, now, frequency=2000, duration=45, volume=99):
        if volume <= 0:
            self.stop()
            return
        self.pwm.freq(frequency)
        self.pwm.duty_u16(int(32768 * min(99, volume) / 99))
        self.amp.value(1)
        self.until = ticks_add(now, duration)

    def update(self, now):
        if self.until is not None and ticks_diff(now, self.until) >= 0:
            self.stop()

    def stop(self):
        self.amp.value(0)
        self.pwm.duty_u16(0)
        self.until = None

    def close(self):
        self.stop()
        self.pwm.deinit()
