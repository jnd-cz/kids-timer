# MicroPython countdown prototype

This firmware targets the Rev 1 board. Complete the power and flash-size checks
in [BRINGUP.md](../BRINGUP.md) first. Confirm the installed build is configured
for the RP2354A's 2 MB flash before writing files. Copy `audio.py`, `display.py`,
`sensors.py`, `motion.py`, `touch.py`, `brightness.py`, `music.py`,
`timer_core.py`, and finally `main.py` to the device root; reset.

The LED mapping has been reported to work on the assembled board. Both D300 and
D301 are enabled in timer mode. LED brightness uses 1 kHz active-low /OE PWM.
Ambient-light control smoothly
varies on-time between 0.5% and 5%, with an approximately five-second response.
The 5% ceiling is provisional until power and thermal testing; an unavailable
light sensor smoothly returns it to 5%.

## Controls and modes

- START starts or pauses the timer, or dismisses its alarm. RESET clears it from
  any mode except audio test and songs. On the timer screen, + and − adjust by
  one minute while paused; reset the timer from any other mode.
- MODE cycles timer → battery → light → accelerometer → level → touch → audio
  test → songs → timer. The timer keeps running in other modes; its alarm sounds
  there too. START dismisses the alarm.
- Timer: MM:SS, with remaining whole minutes and seconds on the rings. The
  minutes ring saturates at 60. Maximum time is 99:59.
- Battery: ` 4.12` means 4.12 V; the BATT indicator is on. ADC scaling assumes
  exactly 3.3 V and a 2:1 divider, so compare and calibrate against a meter.
  With no battery installed the reading is not meaningful.
- Light: whole lux, capped at 9999, with one inner-ring LED on. This is an
  approximate uncalibrated reading; bright light may saturate the sensor.
- Accelerometer: signed acceleration in g, e.g. `-1.00`. Use + and − to select
  X, Y, Z; one, two, or three inner-ring LEDs identify the axis. Tilting the
  stationary board should move roughly 1 g between axes. `----` means waiting
  for the first sample and ` Err` means a sensor communication or ID error.
- Level: the left two digits show the magnitude of X tilt in whole degrees and
  the right two show Y tilt; a decimal point indicates a negative value. The
  rings are off within 2° of level. From 2° to 10°, one green LED shows the
  downward direction; above 10°, one red LED does. The mapping corrects the
  observed reflection and should be checked on the board after updating. It is
  uncalibrated, assumes the board is face up, and is unreliable while moving.
- Touch test: leave both pads untouched for the first 16 samples (~1.6 s).
  The left and right digit pairs show pads 1 and 2 respectively: each is the
  percentage increase in discharge count over its untouched baseline, clamped
  to 00–99. A green ring LED indicates touch on pad 1, a red LED indicates
  pad 2. START recalibrates while no alarm is active. `----` means calibrating;
  `EE` in either pair means that pad timed out. This experimental threshold
  needs physical calibration; RP2350 input leakage and the 1 MΩ pull-down may
  prevent this technique from working reliably.

- Audio test: the left pair shows a note and octave, from C3 to B8. A lit
  upper colon dot means sharp: `C3` plus that dot means C♯3. Lowercase `d`
  and `b` stand for D and B. The right pair shows test level 00–99. START
  selects the note, RESET selects level, and +/− adjusts it and plays a short
  tone. The WIFI indicator lights when level is selected. Level changes the
  duty of the audio-frequency PWM; it is not calibrated loudness. Begin quietly.
- Songs: +/− selects a song number; START plays or stops it, and RESET stops
  it. Songs use the level set in audio test. Changing mode or song stops playback;
  a timer alarm interrupts it. Reset the timer from another mode. These are
  short monophonic arrangements:

  01 Skákal pes; 02 Prší, prší; 03 Twinkle, Twinkle; 04 Frère Jacques;
  05 Mary Had a Little Lamb; 06 London Bridge; 07 Old MacDonald;
  08 Row, Row, Row Your Boat; 09 Ode to Joy; 10 Happy Birthday;
  11 Bingo; 12 Jingle Bells.

Button presses beep outside the audio and song tests. The timer also beeps at
each minute boundary and each
of the last ten seconds, then repeats an alarm once per second until dismissed
or reset. While the alarm is sounding, lifting and tilting the board far enough
to change acceleration by 0.35 g for three 100 ms samples also dismisses it.
The pre-alarm orientation is the reference. A perfectly vertical lift with
little acceleration may not register; vibration or a knock may trigger it.
If the accelerometer fails, use START or RESET. Audio uses the buzzer through
the amp; check volume. BZ1 and J4 are wired in parallel: use one output at a time.

On battery, five consecutive once-per-second ADC readings below 3.4 V turn the
LED rail and audio off and pause the timer until USB is attached or power is
cycled. This provisional safeguard needs voltage calibration; USB presence is
the active-low /PGOOD signal, not a measurement of battery charge.

The touch test has not yet been tested on hardware. The
sensor settings follow the [VEML6030 datasheet](https://www.vishay.com/docs/84366/veml6030.pdf)
and [STK8328-C datasheet](https://www.datasheet4u.com/pdf-down/S/T/K/STK8328-C-Sensortek.pdf).
`diagnostic.py` remains available for LED single-output and loopback tests.

The Czech melodies follow archived folk transcriptions of
[Skákal pes](https://badatelska.pisnovna.cz/pisen/An.EOR3-0003/anonym-skakal-pes-pres-oves)
and [Prší, prší](https://badatelska.pisnovna.cz/pisen/Hol.R_VII-0034/holas-cenek-prsi-prsi-jen-se-lije).
Song playback has not yet been tested on hardware.
