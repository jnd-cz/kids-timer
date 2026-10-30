"""Bounded PIO discharge-time measurement for the two touch pads."""
import rp2
from machine import Pin


@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def discharge_counter():
    wrap_target()
    pull(block)
    mov(x, osr)
    set(pins, 1)
    set(pindirs, 1) [31]  # 32 us charge at 1 MHz
    set(pindirs, 0)
    label('measure')
    jmp(pin, 'high')
    jmp('done')
    label('high')
    jmp(x_dec, 'measure')
    label('done')
    mov(isr, x)
    push(block)
    wrap()


class TouchPads:
    def __init__(self):
        self.pins = (Pin(27, Pin.IN), Pin(28, Pin.IN))
        self.sms = []
        for i, pin in enumerate(self.pins):
            sm = rp2.StateMachine(i, discharge_counter, freq=1000000,
                                  set_base=pin, jmp_pin=pin)
            sm.active(1)
            self.sms.append(sm)
        self.reset()

    def reset(self):
        self.totals = [0, 0]
        self.baselines = None
        self.samples = 0

    def read(self):
        values = []
        for sm in self.sms:
            sm.put(1023)
            remaining = sm.get()
            values.append(1024 if remaining > 1023 else 1023 - remaining)
        if self.baselines is None:
            for i in range(2):
                self.totals[i] += values[i]
            self.samples += 1
            if self.samples >= 16:
                self.baselines = [total / self.samples for total in self.totals]
            return values, None
        touched = [values[i] < 1024 and self.baselines[i] < 1024 and
                   values[i] > self.baselines[i] + max(4, self.baselines[i] * 0.25)
                   for i in range(2)]
        return values, touched

    def close(self):
        for sm in self.sms:
            sm.active(0)
        for pin in self.pins:
            pin.init(Pin.IN)
