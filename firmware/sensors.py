"""Minimal Rev 1 sensor readers, with configuration reapplied on retry."""
from machine import I2C, Pin


class Sensors:
    def __init__(self):
        self.bus = I2C(0, sda=Pin(4), scl=Pin(5), freq=100000)
        self.light_ready = False
        self.accel_ready = False

    def light(self):
        try:
            if not self.light_ready:
                # Gain 1/8, integration 100 ms, PSM off, ALS on: 0.4608 lux/count.
                self.bus.writeto_mem(0x10, 0x03, b'\x00\x00')
                self.bus.writeto_mem(0x10, 0x00, b'\x00\x10')
                self.light_ready = True
                return None
            data = self.bus.readfrom_mem(0x10, 0x04, 2)
            return (data[0] | (data[1] << 8)) * 0.4608
        except OSError:
            self.light_ready = False
            raise

    def acceleration(self):
        try:
            if not self.accel_ready:
                if self.bus.readfrom_mem(0x1f, 0x00, 1)[0] != 0x25:
                    raise ValueError('unexpected accelerometer ID')
                self.bus.writeto_mem(0x1f, 0x11, b'\x80')
                self.bus.writeto_mem(0x1f, 0x0f, b'\x03')
                self.bus.writeto_mem(0x1f, 0x10, b'\x0b')
                self.bus.writeto_mem(0x1f, 0x11, b'\x00')
                self.accel_ready = True
                return None
            data = self.bus.readfrom_mem(0x1f, 0x02, 6)
            values = []
            for i in (0, 2, 4):
                value = data[i] | (data[i + 1] << 8)
                if value & 0x8000:
                    value -= 65536
                values.append(value / 16384)
            return tuple(values)
        except (OSError, ValueError):
            self.accel_ready = False
            raise
