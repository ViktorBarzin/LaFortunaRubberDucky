'''
This script does the following:
    1. Reads a file containing a valid DuckyScript text
        (https://github.com/hak5darren/USB-Rubber-Ducky/wiki/Duckyscript)
    2. Parses the DuckyScript and adjusts keyboard_task.c to
        send the appropriate keys
    3. Make-s the demo code with the updated keyboard task
    4. Produces a .hex file ready to be flashed on the LaFortuna board
'''

import utilities
import ducky_script_parser as dsp
import ducky_to_hid as dth
import os

DUCKY_SCRIPT_PATH = os.path.join(os.getcwd(), 'duckyScript.txt')
KEYBOARD_TASK_PATH = os.path.join(os.getcwd(), 'USB Keyboard',
                                  'USBKEY_STK525-series6-hidkbd-2_0_3-doc',
                                  'at90usb128', 'demo',
                                  'USBKEY_STK525-series6-hidkbd',
                                  'keyboard_task.c')
MAKEFILE_PATH = os.path.join(os.getcwd(), 'USB Keyboard',
                                          'USBKEY_STK525-series6-hidkbd-2_0_3-doc',
                                          'at90usb128', 'demo',
                                          'USBKEY_STK525-series6-hidkbd',
                                          'gcc')


def main():
    ducky_script_lines = utilities.get_lines(DUCKY_SCRIPT_PATH)
    # print(ducky_script_lines)
    parser = dsp.DuckyScriptParser()
    parsed = parser.parse(ducky_script_lines)

    converter = dth.DuckyScriptConverter()
    converted = converter.convert(parsed.split('\n'))

    array_str = utilities.create_array_string('const U8 code', 'usb_keys',
                                              converted)

    keyboard_task_lines = utilities.get_lines(KEYBOARD_TASK_PATH)
    changed_lines = utilities.replace_line(keyboard_task_lines,
                                           'const U8 code usb_keys',
                                           array_str)
    new_keyboard_task_file = '\n'.join(changed_lines)

    # overwrite file
    utilities.write_file(KEYBOARD_TASK_PATH, new_keyboard_task_file)
    # run make
    utilities.make(MAKEFILE_PATH)


if __name__ == "__main__":
    main()
