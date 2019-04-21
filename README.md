# What is this

This repository contains contains my final project for **COMP2215** module for **University of Southmapton**.

TL;DR: Creates a rubber ducky using a Atmel microcontroller, parses a DuckyScript file and creates a hex file to flash on the microcontroller.

That is a hacky implementation of the [DuckyScript](https://github.com/hak5darren/USB-Rubber-Ducky/wiki/Duckyscript) that works for the [Atmel AT90USB1286 microcontroller](https://www.microchip.com/wwwproducts/en/AT90USB1286).
You can find the schematics of the LaFortuna board [here](https://github.com/ViktorBarzin/LaFortunaRubberDucky/blob/master/lafortuna-schem.pdf) and the datasheet for the microcontroller [here](https://github.com/ViktorBarzin/LaFortunaRubberDucky/blob/master/at90usb1286_doc7593.pdf) or on Atmel's website.

The LaFortuna board has a USB controller which is used in Device Controller mode (aka client mode), simulates a USB keyboard (p. 246 in the datasheet) and simulates key presses that are hard coded based on the ducky script code.

The C code is based on the keyboard demo provided on [Atmel's website](https://www.microchip.com/wwwAppNotes/AppNotes.aspx?appnote=en591888). I highly recommend understanding the code before trying to tweak it.

The main change is in *keyboard_task.c*. The keys that are going to be pressed are stored in an array called `usb_keys`.
The HID values of each key can be found in `usb_commun_hid.h`.
I've also tweaked the latter to add some new keys and fix old ones.

# Demo

The script:
```
DELAY 3000
WINDOWS r
DELAY 500
STRING notepad
DELAY 500
ENTER
DELAY 2750
STRING Hello World!
ENTER
```
produces the expected hello world example once the board is plugged in:

![](lafortuna-rubber-ducky-demo.gif)

# Requirements

1. [Python 3.7+](https://www.python.org/downloads/release/python-370/) to parse DuckyScript and adjust the C file
2. [Gnu make](https://www.gnu.org/software/make/) to make the project
3. [dfu-programmer](https://dfu-programmer.github.io/) to flash the *.hex* file on the microcontroller

# How to run your own DuckyScript program

1. Run ```python rubber_ducky_to_hex.py```
This will read the contents of ```duckyScript.txt```, parse it and make the *hex* file that you should afterwards flash to your microcontroller.
2. Run ```sudo dfu-programmer at90usb1286 erase && sudo dfu-programmer at90usb1286 flash payload.hex``` to erase and reflash it.

# Know issues
