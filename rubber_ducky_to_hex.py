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

DUCKY_SCRIPT_PATH = os.path.join(os.getcwd(), "duckyScript.txt")


def main():
    ducky_script_lines = utilities.get_lines(DUCKY_SCRIPT_PATH)
    # print(ducky_script_lines)
    parser = dsp.DuckyScriptParser()
    parsed = parser.parse(ducky_script_lines)

    converter = dth.DuckyScriptConverter()
    converted = converter.convert(parsed.split('\n'))
    print(converted)


if __name__ == "__main__":
    main()
