"""Rev 1 display driver. Bit order must be checked using diagnostic.py."""
from machine import Pin, PWM
from time import sleep_ms


class Display:
    def __init__(self, brightness=0.05):
        self.power = Pin(22, Pin.OUT, value=0)
        self.data = Pin(19, Pin.OUT, value=0)
        self.clock = Pin(18, Pin.OUT, value=0)
        self.latch = Pin(21, Pin.OUT, value=0)
        self.oe = Pin(20, Pin.OUT, value=0)
        self.pwm = None
        self.brightness = brightness

    def on(self):
        self.power.value(1)
        self.oe.value(1)  # Blank outputs while the chain is initialized.
        sleep_ms(10)
        self.write([0] * 160)
        # /OE is active low: a high PWM duty means fewer LEDs on.
        self.pwm = PWM(self.oe)
        self.pwm.freq(1000)
        self.pwm.duty_u16(int(65535 * (1 - self.brightness)))

    def set_brightness(self, brightness):
        self.brightness = min(0.05, max(0.005, brightness))
        if self.pwm is not None:
            self.pwm.duty_u16(int(65535 * (1 - self.brightness)))

    def write(self, bits):
        if len(bits) != 160:
            raise ValueError('expected 160 LED bits')
        # U19 is furthest from SDI; assume OUT15 shifts in first per chip.
        for bit in reversed(bits):
            self.clock.value(0)
            self.data.value(bit)
            self.clock.value(1)
        self.clock.value(0)
        self.latch.value(1)
        self.latch.value(0)

    def off(self):
        if self.pwm is not None:
            self.pwm.deinit()
            self.pwm = None
        # The LED rail must not be back-powered by any of these pins.
        self.oe.init(Pin.OUT, value=0)
        self.data.value(0)
        self.clock.value(0)
        self.latch.value(0)
        self.power.value(0)
