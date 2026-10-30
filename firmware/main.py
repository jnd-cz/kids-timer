"""Button-operated countdown and hardware diagnostic modes for Rev 1."""
from machine import ADC, Pin
from time import sleep_ms, ticks_ms, ticks_diff, ticks_add
from audio import Audio
from music import Player, SONGS, frequency, note_label
from display import Display
from sensors import Sensors
from motion import Pickup, level_frame
from brightness import brightness_target, smooth_brightness, MAX_BRIGHTNESS
from touch import TouchPads
from timer_core import Timer, frame, fixed_frame, text_frame, touch_frame

BUTTONS = ((10, 'start'), (11, 'minus'), (12, 'mode'), (9, 'plus'), (13, 'reset'))
DEBOUNCE_MS = 35
LOW_BATTERY_V = 3.4


def main():
    Pin(2, Pin.OUT, value=0)  # Default USB input limit.
    Pin(23, Pin.OUT, value=0)  # Unfitted radio off.
    usb = Pin(3, Pin.IN)
    battery = ADC(26)
    buttons = [(Pin(pin, Pin.IN, Pin.PULL_UP), action) for pin, action in BUTTONS]
    state = [[1, 1, ticks_ms()] for _ in buttons]
    timer = Timer()
    display = Display()
    audio = Audio()
    player = Player(audio, ticks_add, ticks_diff)
    sensors = Sensors()
    display.on()
    mode = 0  # timer, battery, light, accelerometer, level, touch, notes, songs
    test_note = 72  # C5 (MIDI 48 = C3, 119 = B8)
    selected_song = 0
    test_volume = 20
    audio_field = 0
    light = None
    last_light = ticks_ms()
    touch = None
    touch_values = None
    touch_flags = None
    last_touch = ticks_ms()
    pickup = Pickup()
    accel = None
    last_accel = ticks_ms()
    axis = 0
    reading = None
    previous_frame = None
    last_sensor = ticks_ms()
    last_battery_check = ticks_ms()
    last_alarm = ticks_ms()
    low_count = 0
    try:
        while True:
            now = ticks_ms()
            old_seconds = timer.seconds
            old_running = timer.running
            timer.update(now, ticks_diff)
            if timer.alarm and player.playing:
                player.stop()
            if old_running and timer.seconds != old_seconds:
                if timer.alarm or (timer.seconds <= 10 or timer.seconds % 60 == 0):
                    audio.beep(now, 2400 if timer.alarm else 1500, 180 if timer.alarm else 45)
                    last_alarm = now
            if timer.alarm and ticks_diff(now, last_alarm) >= 1000:
                audio.beep(now, 2400, 180)
                last_alarm = now
            audio.update(now)
            if not timer.alarm:
                player.update(now)
            for i, (pin, action) in enumerate(buttons):
                raw = pin.value()
                if raw != state[i][0]:
                    state[i][0], state[i][2] = raw, now
                if raw != state[i][1] and ticks_diff(now, state[i][2]) >= DEBOUNCE_MS:
                    state[i][1] = raw
                    if raw == 0:
                        if mode not in (6, 7) or action == 'mode':
                            if not player.playing:
                                audio.beep(now)
                        if action == 'mode':
                            player.stop()
                            mode = (mode + 1) % 8
                            if touch is not None:
                                touch.close()
                                touch = None
                            if mode == 5:
                                touch = TouchPads()
                                touch_values = None
                                touch_flags = None
                            reading = None
                            last_sensor = ticks_ms() - 1000
                        elif mode == 6:
                            if timer.alarm:
                                if action in ('start', 'reset'):
                                    timer.reset() if action == 'reset' else timer.toggle()
                                    audio.stop()
                            else:
                                if action == 'start':
                                    audio_field = 0
                                elif action == 'reset':
                                    audio_field = 1
                                elif action in ('plus', 'minus'):
                                    delta = 1 if action == 'plus' else -1
                                    if audio_field == 0:
                                        test_note = min(119, max(48, test_note + delta))
                                    else:
                                        test_volume = min(99, max(0, test_volume + delta * 5))
                                audio.beep(now, frequency(test_note), 400, test_volume)
                        elif mode == 7:
                            if timer.alarm:
                                if action in ('start', 'reset'):
                                    timer.reset() if action == 'reset' else timer.toggle()
                                    audio.stop()
                            elif action in ('plus', 'minus'):
                                player.stop()
                                selected_song = (selected_song + (1 if action == 'plus' else -1)) % len(SONGS)
                            elif action == 'start':
                                if player.playing:
                                    player.stop()
                                else:
                                    player.start(selected_song, now, test_volume)
                            elif action == 'reset':
                                player.stop()
                        elif mode == 5 and action == 'start' and not timer.alarm:
                            touch.reset()
                            touch_flags = None
                        elif action == 'reset':
                            timer.reset()
                        elif mode == 0:
                            if action == 'start':
                                timer.toggle()
                            elif action == 'plus':
                                timer.add(60)
                            elif action == 'minus':
                                timer.add(-60)
                        elif mode == 3 and action in ('plus', 'minus'):
                            axis = (axis + (1 if action == 'plus' else -1)) % 3
                            reading = None
                            last_sensor = ticks_ms() - 1000
                        elif action == 'start' and timer.alarm:
                            timer.toggle()
            if ticks_diff(now, last_battery_check) >= 1000:
                last_battery_check = now
                voltage = battery.read_u16() * 3.3 * 2 / 65535
                low_count = low_count + 1 if usb.value() and voltage < LOW_BATTERY_V else 0
                if low_count >= 5:
                    timer.running = False
                    pickup.clear()
                    if touch is not None:
                        touch.reset()
                        touch_flags = None
                    accel = None
                    player.stop()
                    audio.stop()
                    display.off()
                    while usb.value():
                        sleep_ms(500)
                    low_count = 0
                    timer.last_ms = ticks_ms()
                    display.on()
                    previous_frame = None
            if ticks_diff(now, last_accel) >= 100:
                last_accel = now
                try:
                    accel = sensors.acceleration()
                    if accel is not None:
                        if timer.alarm:
                            if pickup.moved(accel):
                                timer.toggle()
                                audio.stop()
                        else:
                            pickup.observe(accel)
                except (OSError, ValueError):
                    accel = 'error'
                    pickup.clear()
            if touch is not None and ticks_diff(now, last_touch) >= 100:
                last_touch = now
                touch_values, touch_flags = touch.read()
            if ticks_diff(now, last_light) >= 500:
                last_light = now
                try:
                    light = sensors.light()
                    target = brightness_target(light) if light is not None else MAX_BRIGHTNESS
                except OSError:
                    light = 'error'
                    target = MAX_BRIGHTNESS
                display.set_brightness(smooth_brightness(display.brightness, target))
            if mode and mode not in (5, 6, 7) and ticks_diff(now, last_sensor) >= 250:
                last_sensor = now
                try:
                    if mode == 1:
                        reading = battery.read_u16() * 3.3 * 2 / 65535
                    elif mode == 2:
                        reading = light
                    else:
                        reading = accel
                except (OSError, ValueError):
                    reading = 'error'
            if mode == 6:
                label, sharp = note_label(test_note)
                bits = text_frame(label + '%02d' % test_volume)
                bits[142] = int(sharp)
                bits[143] = 1
                bits[60] = audio_field  # WIFI marks volume selected
            elif mode == 7:
                bits = text_frame('  %02d' % (selected_song + 1))
                bits[62] = int(not player.playing)
            elif mode == 5:
                bits = touch_frame(touch_values, touch.baselines, touch_flags)
            elif mode == 0:
                bits = frame(timer.seconds, timer.running, timer.alarm)
            elif reading == 'error':
                bits = text_frame(' Err')
            elif reading is None:
                bits = text_frame('----')
            elif mode == 1:
                bits = fixed_frame(reading)
            elif mode == 3:
                bits = fixed_frame(reading[axis])
            elif mode == 4:
                bits = level_frame(reading)
            else:
                bits = text_frame('%4d' % min(9999, int(reading + 0.5)))
            if mode == 1:
                bits[63] = 1
            elif mode == 2:
                bits[0] = 1
            elif mode == 3:
                for i in range(axis + 1):
                    bits[i] = 1
            if mode and timer.alarm:
                bits[61] = 1
            if bits != previous_frame:
                display.write(bits)
                previous_frame = bits
            sleep_ms(20)
    finally:
        player.stop()
        if touch is not None:
            touch.close()
        audio.close()
        display.off()


main()
