"""Pure countdown and display mapping logic for the Rev 1 board."""

SEGMENTS = (0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6d, 0x7d, 0x07, 0x7f, 0x6f)
GLYPHS = {' ': 0, '-': 0x40, 'E': 0x79, 'r': 0x50, 'C': 0x39, 'd': 0x5e, 'F': 0x71, 'G': 0x3d, 'A': 0x77, 'b': 0x7c}
MAX_SECONDS = 99 * 60 + 59


class Timer:
    def __init__(self):
        self.seconds = 0
        self.running = False
        self.alarm = False
        self.last_ms = None
        self.remainder_ms = 0

    def update(self, now, ticks_diff):
        if self.last_ms is None:
            self.last_ms = now
            return
        elapsed = max(0, ticks_diff(now, self.last_ms))
        self.last_ms = now
        if self.running:
            self.remainder_ms += elapsed
            whole = self.remainder_ms // 1000
            self.remainder_ms %= 1000
            if whole >= self.seconds:
                self.seconds = 0
                self.running = False
                self.alarm = True
                self.remainder_ms = 0
            else:
                self.seconds -= whole

    def add(self, seconds):
        if not self.running:
            self.seconds = min(MAX_SECONDS, max(0, self.seconds + seconds))
            self.alarm = False
            self.remainder_ms = 0

    def toggle(self):
        if self.alarm:
            self.alarm = False
        elif self.seconds:
            self.running = not self.running

    def reset(self):
        self.seconds = 0
        self.running = False
        self.alarm = False
        self.remainder_ms = 0


def text_frame(text, decimal=False):
    bits = [0] * 160
    for digit, char in enumerate(text):
        pattern = SEGMENTS[int(char)] if '0' <= char <= '9' else GLYPHS[char]
        base = 128 + (digit // 2) * 16 + (digit % 2) * 7
        for segment in range(7):
            bits[base + segment] = (pattern >> segment) & 1
    bits[158] = int(decimal)  # DP2, after the second digit
    return bits


def fixed_frame(value):
    """Signed value in hundredths, shown as ' 1.23' or '-1.23'."""
    hundredths = min(999, int(abs(value) * 100 + 0.5))
    return text_frame(('-' if value < 0 else ' ') + '%03d' % hundredths, True)


def frame(seconds, running=False, alarm=False, low_battery=False):
    minutes, sec = divmod(seconds, 60)
    bits = text_frame('%02d%02d' % (minutes, sec))
    for i in range(min(minutes, 60)):
        bits[(60 - i) % 60] = 1
    for i in range(sec):
        bits[64 + i] = 1
    bits[142] = bits[143] = 1  # D300 and D301
    bits[61] = int(alarm)
    bits[62] = int(not running and seconds > 0)
    bits[63] = int(low_battery)
    return bits


def touch_frame(values, baselines, touched):
    """Show each pad's increase over baseline as 00..99 percent, EE on timeout."""
    if values is None or touched is None:
        return text_frame('----')
    parts = []
    for value, baseline in zip(values, baselines):
        if value >= 1024 or baseline >= 1024:
            parts.append('EE')
        else:
            increase = max(0, int((value - baseline) * 100 / max(1, baseline)))
            parts.append('%02d' % min(99, increase))
    bits = text_frame(''.join(parts))
    bits[0] = int(touched[0])
    bits[64] = int(touched[1])
    return bits
