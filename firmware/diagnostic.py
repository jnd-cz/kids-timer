"""REPL diagnostics. Import explicitly; never installed as main.py."""
from machine import Pin
from time import sleep_ms
from display import Display


def single(driver, output):
    """Light one assumed output; call off() when finished."""
    global display
    if not (10 <= driver <= 19 and 0 <= output < 16):
        raise ValueError('driver must be 10..19, output 0..15')
    try:
        display.off()
    except NameError:
        pass
    display = Display()
    display.on()
    bits = [0] * 160
    bits[(driver - 10) * 16 + output] = 1
    display.write(bits)


def off():
    display.off()


def loopback():
    """Compare a non-periodic 160-bit pattern after a full chain delay."""
    display = Display()
    sdo = Pin(16, Pin.IN)
    pattern = [int((i * 37 % 101) < 47) for i in range(160)]
    try:
        display.on()
        for bit in pattern:
            display.clock.value(0)
            display.data.value(bit)
            display.clock.value(1)
        received = []
        for _ in pattern:
            display.clock.value(0)
            sleep_ms(1)
            received.append(sdo.value())
            display.data.value(0)
            display.clock.value(1)
        display.clock.value(0)
        return received == pattern
    finally:
        display.off()
