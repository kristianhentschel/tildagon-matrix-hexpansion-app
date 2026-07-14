# Matrix Hexpansion App

A companion app for the [Matrix Hexpansion](https://5yk.de/matrix-hexpansion/). Select an animation pattern, display text, or flash your own code.

Supported boards:

* `v2 lite` + `lite-loop`

Currently the list of strings that can be displayed is hard-coded in the app source code; this will become editable from the badge in a future update.

![The 2024 Tildagon badge with my matrix hexpansion plugged into every slot. Each expansion circuit board is a slice of a donut shaped ring around the badge with 18 by 9 monochrome LEDs. There are four white and two orange segments, and they are programmed to display the text "You know the rules, and so..."](docs/you_know_the_rules.jpg)

## Firmware upgrades (WIP)

_NB this functionality is not complete in the hexpansion firmware yet and has been disabled in the app until confirmed working. Currently, attempting to flash a new firmware will only erase the current program (this then needs a WCH-LinkE or similar programmer to recover)_

The program running on the hexpansion processor can be upgraded from this app. The firmware maintains the matrix display and can run animations independently of the badge. If there is a new release or you want to upload custom firmware, follow these steps:

1. Bridge the `HSG - PD7/NRST` solder jumper on the back of the hexpansion base. _Make sure you select the correct hexpansion slot; the upgrade process will attempt to pull down the `HSG` (high speed pin 2) pin which may cause trouble with hexpansions using it for something else._
2. Connect the hexpansion
3. Go to `Firmware upgrade` in the app
4. Select the hexpansion slot and firmware image matching your hardware in the menu
5. Select `Flash now`
6. Wait for a confirmation message to appear in the app.

### Background

The CH32V006 microcontroller on the hexpansion base board runs a compiled program that maintains the matrix display, generates frames for the selected pattern, and presents an I2C interface for configuration. It also emulates a read-only EEPROM with the hexpansion header, used by this app to detect which board is plugged into which hexpansion slot.

The app will support flashing custom code to the CH32V003 or CH32V006 processor on the hexpansion. By default the latest 'official' binary image will be loaded from the [Matrix Hexpansion firmware repository](https://github.com/kristianhentschel/tildagon-matrix-hexpansion-firmware). Upload custom image files to the badge file system and they will be listed in the firmware upgrade menu.

The firmware upgrade mode and bootloader simply writes a binary image to the start of the flash memory and boots into it; no verification of its contents takes place.

To enable firmware upgrades, the solder jumper `HSG - PD7/NRST` on the back of the base board must be bridged. This enables the badge to enter the bootloader mode after briefly cutting power to the hexpansion. `PD7` by default is configured as an output to drive the matrix display (when not in bootloader mode), so bridging this jumper means that `HSG` (high speed pin 2) cannot be used as an output from the badge.


