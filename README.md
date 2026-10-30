# Kids timer

Rev 1 PCB design and a MicroPython countdown timer for the RP2354A. The firmware
supports a seven-segment countdown, minute and second LED rings, ambient-light
brightness, audio and songs, battery and sensor readouts, a level, and a touch
pad test.

- [Firmware installation, features and controls](firmware/README.md)
- [Board bring-up and GPIO map](BRINGUP.md)
- [Display power estimate and measurement plan](firmware/POWER.md)
- [Production files for Rev 1](production/)

The firmware is an evolving hardware prototype. See the firmware guide for
features that still need board verification and the 2 MB flash check before
copying files to the device. Run host-side logic checks with
`python -m unittest discover -s tests -v`.
