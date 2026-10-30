# Kids timer — board bring-up and firmware notes

Rev 1 as ordered from JLCPCB (Economic PCBA, 2026-10-21). The production files are in
`production/`. The RM2 Wi-Fi module (U8) is **not fitted** on the first batch.

## Before the first flash: check the flash size

The RP2354A has **2 MB** of internal (stacked) flash; QSPI pins 55–59 are unconnected on purpose.
Stock MicroPython builds for the Pico 2 / Pico 2 W assume 4 MB and place the filesystem above
1 MB, so part of it would land past the end of the chip.

Check before trusting the filesystem. After flashing, `import rp2; rp2.Flash().ioctl(4, 0)` gives
the block count, and `os.statvfs('/')` the filesystem size. A filesystem bigger than about 1 MB
means the build assumes 4 MB. If it does, build a board variant with `PICO_FLASH_SIZE_BYTES`
set to 2 MB (`2 * 1024 * 1024`).

While U8 is missing, use a non-W (RPI_PICO2-style) build. Pin mapping is the same; see the Wi-Fi section.

## Power-up sequence

1. **Before any power:** measure resistance to GND on VSYS, +3V3, +1V1 (C21), 3V3_LED and +BATT.
   Nothing should read as a short.
2. **USB only, SW1 (POWER) off:**
   - VBUS ≈ 5 V and VSYS ≈ 4.4 V (BQ24073 OUT).
   - +3V3 should be 0 V, because SW1 drives the TPS63031's EN line.
   - The CHG LED (D1) may blink with no battery; that's normal for the BQ2407x.
3. **SW1 on:**
   - +3V3 ≈ 3.3 V (TPS63031, power-save mode).
   - +1V1 ≈ 1.1 V (RP2354 internal switcher via L2).
   - Idle current should be small; the LED rail is still off.
4. **Battery** (J2, JST PH; **pin 1 = +**; check the pack's wire colours, since JST packs are not standardised):
   - With USB connected, D1 lights while charging.
   - The MCU only runs with SW1 on, including over USB. Charging works with SW1 off.

## Programming and debug

- **BOOTSEL:** hold SW2 (BOOT), tap SW3 (REBOOT, the RUN pin), release BOOT. The board then appears as an RP2350 USB drive.
- **Test pads on the back**, y = 84 mm, 2.5 mm pitch (1.5 mm round pads), suitable for pogo pins or soldered wires.
  - Front-side x order: TP5 GND 95, TP3 SWCLK 97.5, TP4 SWDIO 100, TP6 UART_TX 102.5, TP7 UART_RX 105.
  - Looking at the back, the order is mirrored: RX, TX, SWDIO, SWCLK, GND.
- **UART0:** GP0 TX, GP1 RX.
- **Crystal:** Y1 is 12 MHz (X322512MSB4SI, CL 20 pF) with 33 pF load caps.
  - If the clock is slow to start (USB fails intermittently after a cold boot), raise `PICO_XOSC_STARTUP_DELAY_MULTIPLIER` (e.g. 64) in the firmware build.

## GPIO map (RP2354A, QFN-60)

| GPIO | Net | Notes |
|---|---|---|
| 0 / 1 | UART_TX / UART_RX | test pads TP6 / TP7 |
| 2 | CHG_HI | charge input limit: low = 500 mA USB (default, R7 pull-down), high = ~1.29 A (ILIM). Set high only on a >500 mA source |
| 3 | VBUS_DET | BQ24073 /PGOOD, open drain, 100 k pull-up: **low = USB power present** |
| 4 / 5 | I2C_SDA / I2C_SCL | I2C0, 4.7 k pull-ups. VEML6030 at **0x10** (ADDR = GND), STK8328-C at **0x1F** (SA0 high) |
| 6 / 7 | ACC_INT1 / ACC_INT2 | STK8328-C, no external pull-ups (configure push-pull in the chip). FIFO event modes need INT1. Map sources via INTMAP1/INTMAP2 (0x19/0x1A) |
| 8 | ALS_INT | VEML6030 /INT, 10 k pull-up, active low |
| 9–13 | BTN4, BTN1, BTN2, BTN3, BTN5 | to GND, **no external pull-ups**: use internal pull-ups, active low |
| 14 | AUDIO_PWM | PWM → RC low-pass (4.7 k / 4.7 nF) → PAM8302 differential input |
| 15 | AMP_EN | PAM8302 /SD, 100 k pull-down: high = amp on |
| 16 | LED_SDO | end of the driver chain (U19 SDO), for loop-back testing |
| 17 | — | free |
| 18 | LED_CLK | via 33 Ω, all ten drivers |
| 19 | LED_SDI | chain input (U10 SDI) |
| 20 | LED_OE | drivers' /OE, active low. Use PWM here for brightness |
| 21 | LED_LE | latch |
| 22 | LED_PWR_EN | high = 3V3_LED on (Q5 → Q4). 100 k pull-down, so it's off at boot |
| 23 | WL_ON | RM2 WL_ON + BT_ON, 100 k pull-down |
| 24 | WL_D | RM2 data (470 Ω to DOUT, 10 k to IRQ), the Pico 2 W layout |
| 25 | WL_CS | RM2 /CS |
| 26 / ADC0 | VBAT_SENSE | 220 k / 220 k divider: **V_bat = 2 × ADC voltage** |
| 27 / ADC1 | TOUCH1 | 12 mm pad (TP1), mask-covered, 1 M to GND |
| 28 / ADC2 | TOUCH2 | 12 mm pad (TP2), mask-covered, 1 M to GND |
| 29 | WL_CLK | via 33 Ω to RM2 SCLK |

The other buttons:
- SW2 BOOT pulls QSPI_SS low via 1 k.
- SW3 REBOOT pulls RUN low.
- SW1 POWER is the slide switch on the right edge.

## LED driver chain (10 × SM16206S, 16 outputs each)

GP19 → U10 → U11 → … → U19 → GP16. CLK, LE and /OE are shared by all ten. Each chip has 16
outputs, 160 bits in total. **Check the bit order at bring-up:**
- Light a single bit and see which LED responds.
- Use the GP16 loop-back: shift a known pattern in and read it back out after 160 clocks.

| Driver | OUT0 … OUT15 | Current set |
|---|---|---|
| U10 | D100 … D115 (minutes 0–15) | 3.3 k |
| U11 | D116 … D131 | 3.3 k |
| U12 | D132 … D147 | 3.3 k |
| U13 | D148 … D159, then OUT12–15 = D160 WIFI, D161 ALARM, D162 PAUSE, D163 BATT | 3.3 k |
| U14 | D200 … D215 (seconds 0–15) | 3.3 k |
| U15 | D216 … D231 | 3.3 k |
| U16 | D232 … D247 | 3.3 k |
| U17 | D248 … D259, OUT12–15 unused | 3.3 k |
| U18 | DS1 A–G (OUT0–6), DS2 A–G (OUT7–13), colon D300 (OUT14), D301 (OUT15) | 2 k |
| U19 | DS3 A–G (OUT0–6), DS4 A–G (OUT7–13), DP2 (OUT14), DP4 (OUT15) | 2 k |

- **Ring orientation:**
  - Outer red seconds ring: D200 at 12 o'clock, then **clockwise** (D215 at 3 o'clock).
  - Inner green minutes ring: D100 at 12 o'clock, then **counter-clockwise** (D115 at 9 o'clock). So minute *m* → LED index **(60 − m) % 60**.
- **Digits:** DS1 … DS4 run left to right, all common anode on VSYS. Segment order on each driver is A, B, C, D, E, F, G.
- **LED rail:** anodes are on VSYS (≈ 4.4 V on USB, battery voltage otherwise); the drivers' VDD is 3V3_LED.
  - Before turning 3V3_LED off (GP22 low), drive LED_SDI, LED_CLK, LED_LE and LED_OE low. Otherwise the drivers get back-powered through their inputs.
  - Turn-on order: GP22 high, short delay, shift data, latch, then enable /OE.
- **Brightness:** check the SM16206S current formula against R-EXT in the datasheet. Start with a low /OE PWM duty; 120 LEDs at full current is a large load on the battery and the USB limit.

## Battery and protection

- **Charger:** BQ24073, ISET 1 k → ≈ 890 mA charge (0.45 C on 2000 mAh), limited by the input limit set by CHG_HI.
  - Pre-charge ≈ 89 mA below 3 V; termination ≈ 89 mA at 4.2 V.
  - TS has a fixed 10 k, so there's no temperature monitoring. TMR is open, so the default safety timers apply.
- **Protection:** DW01A + 8205A.
  - Cuts off at ≈ 4.3 V on charge and ≈ 2.4 V on discharge; overcurrent trips at ≈ 3 A.
  - Q1 (AO3401A) protects against a reversed battery.
- **Firmware:** shut down (LEDs off, deep sleep or a "please charge" state) at about **3.3–3.4 V**, measured on ADC0 ×2. The buck-boost keeps running down to about 1.8 V, so otherwise only the DW01A at 2.4 V stops the discharge, and that is hard on the cell.
- **Switched off:** with SW1 off, VSYS stays live. Only the regulator is off; the amp is held in shutdown by its pull-down. Expect a small standby drain, mostly from the BQ24073 and the DW01A.

## Touch pads

- Each pad is a single capacitive pad: the GPIO with 1 M to GND (CircuitPython `touchio` style).
- To measure: drive the pin high briefly, switch to input, and time how long it takes to fall low. A finger makes it slower.
- MicroPython has no `touchio`, so use a tight timing loop or a small PIO program, and calibrate a baseline at boot.
- The pads are under soldermask, and the GND pours are kept 1 mm away on top and removed from the back of the pads.

## Audio

PAM8302 (mono class-D) runs from VSYS. **BZ1 (MLT-8530 magnetic buzzer) and J4 (speaker connector) are wired in parallel** on the amp outputs:
- Use one or the other; a speaker on J4 together with BZ1 loads the amp with both.
- The BZ1 land pattern was approximated from the drawing, so check its fit.

## Wi-Fi (RM2, U8 — not fitted yet)

- Wired like the Pico 2 W, so stock `RPI_PICO2_W` MicroPython works once U8 is fitted:
  - WL_ON = GP23
  - data = GP24
  - /CS = GP25
  - CLK = GP29
- Until then, keep WL_ON low (it has a pull-down) and use a non-W build.
- The antenna keep-out is the top edge area y 25–30 mm.

## Known board quirks

- U17 OUT12–15 and GP17 are spare.
- H1 is an 8.4 mm wire pass-through for the battery leads. H2–H5 are M3 holes for a cover; use nylon hardware on H5, which is close to the 3V3_EN trace on the back.
- JLC placement offsets are kept in hidden `FT Rotation Offset` footprint fields (Fabrication Toolkit).
- TP1–TP7 and H1–H5 are excluded from BOM/CPL on the board only. Mark the TP symbols the same way in the schematic before running Update PCB (F8) again.
