# Rev 1 LED power estimate

This is a rough nominal calculation, not a verified full-brightness rating.
The 120 ring LEDs and four indicators use 3.3 kΩ R-EXT; 28 digit segments,
two colon LEDs and two wired decimal points use 2 kΩ R-EXT. The LED anodes
connect to VSYS; SM16206 VDD connects to switched 3.3 V. Four driver outputs
are unused, and two digit decimal points are not connected.

The [SM16206 datasheet](https://datasheet.lcsc.com/lcsc/2107141521_Shenzhen-Sunmoon-Micro-SM16206S_C121618.pdf)
specifies typical 9.2 mA at 1.8 kΩ and 3.3 V with 1 V at the output. Assuming
an approximate inverse relationship gives 5.0 mA at 3.3 kΩ and 8.3 mA at 2 kΩ;
this is an interpolation, not a guaranteed specification. With all 156 wired
outputs on: 124 × 5.0 mA + 32 × 8.3 mA ≈ **0.89 A**. LED plus driver-output
power is VSYS × current: approximately 3.3 W at 3.7 V battery VSYS or 3.9 W at
4.4 V USB VSYS. Add the 3.3 V logic, MCU, sensor and amplifier consumption.

At 5% common /OE on-time the idealized average LED current is about 44 mA and
LED-path power is 0.16 W at 3.7 V or 0.20 W at 4.4 V; driver logic and other
loads remain. Instantaneous LED current can still approach 0.89 A for each
50 µs pulse. Capacitors, wiring, and regulator dynamics determine actual input
peaks. At low battery voltage white LEDs may lack sufficient current-sink
headroom; actual current may be lower and brightness uneven. The digits' white
LEDs are specified at 3.0 V typical, 3.8 V maximum at 10 mA.

USB500 mode is nominally 475 mA (450–500 mA) **total input** for system plus
charging, so full-on all LEDs alone exceed it. A battery may supplement the
load if present, but do not assume sustainable operation or charging. The
TPS63031's 3.3 V output rating is not the LED current limit because the LED
current comes from VSYS; it must supply logic, MCU and peripherals. The 1.29 A
input-limit mode, protection, battery, traces and thermal behavior need their
own checks. Full-brightness margin cannot be established from this estimate.

At VSYS 4.4 V and illustrative 2 V ring LED drop, a fully lit 16-output ring
driver dissipates roughly 16 × 5 mA × 2.4 V = 0.19 W, plus its own supply power;
actual LED forward voltages, PCB cooling and part temperatures matter. Do not
assume low average PWM current removes pulse or thermal concerns. Verify at
incremental brightness with a current-limited supply, oscilloscope on VSYS and
3.3 V, and temperature measurements, both with USB only and with battery.

Sources: [BQ24073](https://www.ti.com/lit/ds/symlink/bq24073.pdf),
[TPS63031](https://www.ti.com/product/TPS63031),
[GS8011 display](https://datasheet.lcsc.com/lcsc/2409302136_Guangcai-Display-GS8011AW-G_C22462707.pdf).
