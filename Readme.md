# Matrix Hexpansion App

A companion app for the [Matrix Hexpansion](https://5yk.de/matrix-hexpansion/). Select an animation pattern, display text, or flash your own code.

Supported boards:

* `v2 lite` + `lite-loop`

Currently the list of strings that can be displayed is hard-coded in the app source code; this will become editable from the badge in a future update.

![The 2024 Tildagon badge with my matrix hexpansion plugged into every slot. Each expansion circuit board is a slice of a donut shaped ring around the badge with 18 by 9 monochrome LEDs. There are four white and two orange segments, and they are programmed to display the text "You know the rules, and so..."](docs/you_know_the_rules.jpg)

## Display text from another app

```py
from system.eventbus import eventbus
from events.custom import CustomEvent

eventbus.emit(CustomEvent("matrix-hexpansion:display-text", { "text": "Hello World" }))
eventbus.emit(CustomEvent("matrix-hexpansion:clear-text", {}))
```

## Firmware upgrades (WIP)

The program running on the hexpansion processor can be upgraded from this app. The firmware maintains the matrix display and can run animations independently of the badge. If there is a new release or you want to upload custom firmware, follow these steps:

1. Bridge the `HSG - PD7/NRST` solder jumper on the back of the hexpansion base. (This is already done if you got a board from me at EMF 2026).
2. Connect the hexpansion(s).
3. Go to `Firmware upgrade` in the app in the Matrix Hexpansion app main menu.
4. Select the correct hexpansion port. _Make sure you select the correct port; the upgrade process will attempt to pull down the `HSG` (high speed pin 2) pin which may cause trouble with other types of hexpansion using it for something else._
5. The process should take a few seconds during which the app will be unresponsive and the port status LED will flash blue/white to indicate progress. A notification will confirm whether the upgrade succeeded and the port should light up in green.

### Hexpansion firmware details

The CH32V006 microcontroller on the hexpansion base board runs a compiled program that maintains the matrix display, generates frames for the selected pattern, and presents an I2C interface for configuration. It also emulates a read-only EEPROM with the hexpansion header, used by this app to detect which board is plugged into which hexpansion slot. No file system can be written to the emulated EEPROM, so the built-in hexpansion provisioning app cannot be used to upgrade the firmware.

This app supports flashing custom code to the CH32V006 processor on the hexpansion. By default the latest 'official' binary image will be loaded from the [Matrix Hexpansion firmware repository](https://github.com/kristianhentschel/tildagon-matrix-hexpansion). Upload custom image files to the badge file system (with a `.bin` extension the app's `assets/` folder) and they will be listed in the firmware upgrade menu.

```sh
cd firmware/lite_loop/
make build
mpremote cp main.bin :/apps/kristianhentschel_tildagon_matrix_hexpansion_app/assets/lite_loop_custom.bin
```

The firmware upgrade mode and bootloader simply writes a binary image to the start of the flash memory and boots into it. It is not capable of overriding the bootloader itself, for that a dedicated USB programmer using the SWIO debug pin is required.

To enable firmware upgrades, the solder jumper `HSG - PD7/NRST` on the back of the base board must be bridged. This enables the badge to enter the bootloader mode after briefly cutting power to the hexpansion. `PD7` by default is configured as an output to drive the matrix display (when not in bootloader mode), so bridging this jumper means that `HSG` (high speed pin 2) cannot be used as an output from the badge.


