'''
This script converts ducky script output from
'ducky_script_parser.DuckyScriptConverter'
and produces a valid c array containing all the HID_keys
'''
from abc import ABC, abstractmethod
from typing import List, Set
import string


class DuckyScriptConverter(object):
    '''
    Use this class to parse DuckyScript.
    It implements chain of responsibility pattern to match each type of line
    that can be found in the DuckyScript language
    '''
    def __init__(self):
        self.first_parser = WindowsConverter(set(['GUI']))

        # Create chain of responsibility
        # StringConverter MUST be last!
        self.first_parser.set_next(MenuConverter(set(['MENU', 'APP'])))\
                         .set_next(ShiftConverter(set(['SHIFT'])))\
                         .set_next(AltConverter(set(['ALT'])))\
                         .set_next(ControlConverter(set(['CONTROL', 'CTRL'])))\
                         .set_next(ArrorConverter(set(['DOWN', 'LEFT', 'RIGHT',
                                                       'UP'])))\
                         .set_next(ExtendedConverter(
                             set(ExtendedConverter.allowed)))\
                         .set_next(DelayConverter(set('DELAY')))\
                         .set_next(StringConverter(set(
                             [x for x in string.printable])))

    def convert(self, lines: List[str]) -> str:
        result = []
        for line in lines:
            if not line:
                continue
            parsed = self.first_parser.handle(line)
            result.append(parsed)
        # Generate c code here instead of printing
        return ', '.join(result)


class LineConverter(ABC):
    def __init__(self, line_start: Set[str]):
        self.line_startings = line_start
        self.next_parser = None

    def set_next(self, parser):
        self.next_parser = parser
        return self.next_parser

    def handle(self, line: str) -> str:
        if self.__should_parse(line):
            parsed = self._convert(line)
            return parsed
        else:
            if self.next_parser is not None:
                return self.next_parser.handle(line)
            raise Exception(f'No available converter found to convert: {line}')

    @abstractmethod
    def _convert(self, line) -> str:
        '''
        This method parses the line and returns a string which has to be send
        from the keyboard device and ready to be converted to HID values.
        '''
        pass

    def __should_parse(self, line: str) -> bool:
        return any(
         [line.startswith(start) for start in self.line_startings]
        )


class StringConverter(LineConverter):
    def _convert(self, line: str) -> str:
        '''
        This method creates parses plain strings
        For each character it converts it to its HID value
        '''
        result = []
        for char in line:
            if char.isdigit():
                result.append('HID_' + char)
            elif char.isalpha() and char.islower():
                result.append('HID_' + char.upper())
            elif char.isalpha() and char.isupper():
                result.append('HID_CAPS_LOCK, ' + 'HID_' + char
                              + ', HID_CAPS_LOCK')
            else:
                result.append(self.convert_special(char))
        return ', '.join(result)

    def convert_special(self, char: str) -> str:
        if len(char) != 1:
            raise ValueError(
                f'This method converts single chars only, got {char}')
        result = ''
        if char == '"':
            result = 'ESCAPE_KEY_START + 1, ' + 'HID_MODIFIER_LEFT_SHIFT, '\
                + 'HID_SINGLEQUOTE'
        elif char == "'":
            result = 'HID_SINGLEQUOTE'
        elif char == '(':
            result = 'ESCAPE_KEY_START + 1, ' + 'HID_MODIFIER_LEFT_SHIFT, ' \
                + 'HID_9'
        elif char == ')':
            result = 'ESCAPE_KEY_START + 1, ' + 'HID_MODIFIER_LEFT_SHIFT, ' \
                + 'HID_0'
        elif char == '*':
            result = 'HID_KEYPAD_MULTIPLY'
        elif char == '+':
            result = 'HID_KEYPAD_PLUS'
        elif char == '-':
            result = 'HID_KEYPAD_MINUS'
        elif char == '/':
            result = 'HID_KEYPAD_DIVIDE'
        elif char == ',':
            result = 'HID_COMMA'
        elif char == '.':
            result = 'HID_DOT'
        elif char == ';':
            result = 'HID_SEMICOLON'
        elif char == ':':
            result = 'ESCAPE_KEY_START + 1, ' + 'HID_MODIFIER_LEFT_SHIFT, ' \
                + 'HID_SEMICOLON'
        elif char == '<':
            result = 'ESCAPE_KEY_START + 1, ' + 'HID_MODIFIER_LEFT_SHIFT, ' \
                + 'HID_COMMA'
        elif char == '>':
            result = 'ESCAPE_KEY_START + 1, ' + 'HID_MODIFIER_LEFT_SHIFT, ' \
                + 'HID_DOT'
        elif char == '=':
            result = 'HID_KEYPAD_EQUAL'
        elif char == '?':
            result = 'ESCAPE_KEY_START + 1, ' + 'HID_MODIFIER_LEFT_SHIFT, ' \
                + 'HID_SLASH'
        elif char == '@':
            result = 'ESCAPE_KEY_START + 1, ' + 'HID_MODIFIER_LEFT_SHIFT, ' \
                + 'HID_2'
        elif char == '[':
            result = 'HID_LEFT_SQUARE_BRACKET'
        elif char == ']':
            result = 'HID_RIGHT_SQUARE_BRACKET'
        elif char == ' ':
            result = 'HID_SPACEBAR'
        # TODO: implemente all string.printable
        else:
            raise ValueError(f'Char not implemented as HID: {char}')
        return result


class WindowsConverter(LineConverter):
    def _convert(self, line: str) -> str:
        '''
        This method converts the "GUI" key press to HID_VALUE
        If another key is pressed with it, the GUI button is passed as modifier
        '''
        splitted = line.split()
        if len(splitted) == 1:
            # just keyword
            result = 'HID_MODIFIER_LEFT_GUI'
        elif len(splitted) == 2:
            # keyword and char
            if len(splitted[1]) != 1:
                raise Exception(f'GUI button can be pressed with a single char,\
got {line}')
            # splitted[1].upper() may not be the best, but should work for now
            result = 'ESCAPE_KEY_START + 1, HID_MODIFIER_LEFT_GUI, '\
                + 'HID_' + splitted[1].upper()
        else:
            # disallow GUI and multiple buttons
            raise Exception(
                f'DuckyScript allows GUI button and maximum 1 char: {line}')

        return result


class MenuConverter(LineConverter):
    def _convert(self, line: str) -> str:
        '''
        This method parses "APP" and "MENU" directives.
        Returns a "SHIFT-F10" key combo
        '''
        result = 'ESCAPE_KEY_START + 1, HID_MODIFIER_LEFT_SHIFT, HID_F10'

        return result


class ShiftConverter(LineConverter):
    allowed = ['DELETE', 'HOME', 'INSERT', 'PAGEUP', 'PAGEDOWN',
               'WINDOWS', 'GUI', 'UP', 'DOWN', 'LEFT',
               'RIGHT', 'TAB']

    def _convert(self, line: str) -> str:
        '''
        This method parses "SHIFT" directive.
        Capital letters are not written using shift but with caps lock.
        Shift is used for special combos - shift arrow, shift delete, etc...
        '''
        splitted = line.split()
        if len(splitted) == 1:
            # only shift
            result = 'HID_MODIFIER_LEFT_SHIFT'
            return result
        elif len(splitted) == 2:
            # shift + special key
            # check if key is in allowed
            if not (splitted[1] in self.allowed):
                raise Exception(
                    f'"SHIFT" is allowed only in combination with: \
                    {self.allowed}')

            result = 'ESCAPE_KEY_START + 1, HID_MODIFIER_LEFT_SHIFT, '\
                + 'HID_' + splitted[1]

            return result  # return checked line
        else:
            raise Exception(
                f'"SHIFT" can be used with at most 1 argument, got: {line}')


class AltConverter(LineConverter):
    allowed = ['END', 'ESCAPE', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6',
               'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'SPACE', 'TAB']

    def _convert(self, line: str) -> str:
        '''
        This method parses "ALT" directive.
        A single optional parameter is allowed
        '''
        splitted = line.split()
        if len(splitted) == 1:
            # only alt
            result = 'HID_MODIFIER_LEFT_ALT'

            return result
        elif len(splitted) == 2:
            # alt + special key or single char
            # if key is not in allowed, and (is not a letter, or has len > 1
            if splitted[1] not in self.allowed and\
                 (len(splitted[1]) != 1 or not splitted[1].isalpha()):
                raise Exception(
                    f'"ALT" is allowed only in combination with: \
                    {self.allowed} and any single chars')

            # quick fix space
            if splitted[1] == 'SPACE':
                splitted[1] = 'SPACEBAR'

            result = 'ESCAPE_KEY_START + 1, HID_MODIFIER_LEFT_ALT, '\
                + 'HID_' + splitted[1]

            return result  # return checked line
        else:
            raise Exception(
                f'"ALT" can be used with at most 1 argument, got: {line}')


class ControlConverter(LineConverter):
    allowed = ['ENTER', 'BREAK', 'ESC', 'ESCAPE', 'F1', 'F2', 'F3', 'F4',
               'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'PAUSE']
    allowed_modifiers = ['ALT', 'SHIFT']

    def _convert(self, line: str) -> str:
        '''
        This method parses "Control" directive.
        A single optional parameter is allowed
        '''
        raise Exception(f'Not implemented yet: {line}')
        splitted = line.split()
        if len(splitted) == 2:
            # control + special key or single char
            # if key is not in allowed, and (is not a letter, or has len > 1)
            if splitted[1] not in self.allowed and\
                 (len(splitted[1]) != 1 or not splitted[1].isalpha()):
                raise Exception(
                    f'"CONTROL" is allowed only in combination with: \
{self.allowed} and any single chars, got: {line}')

            # result = 'CONTROL ' + splitted[1]
        else:
            raise Exception(
                f'"CONTROL" can be used with at most 1 argument, got: {line}')

        # check for 'CONTROL-MODIFIER' combo
        control_combo = splitted[0].split('-')
        if len(control_combo) > 1:
            # check if second key is allowed
            if control_combo[1] not in self.allowed_modifiers:
                raise Exception(f'You can use control with another modifier\
from the list: {self.allowed_modifiers},\
got: {line}')
        return line  # return checked line


class ArrorConverter(LineConverter):
    def _convert(self, line: str) -> str:
        '''
        This method parses arrow directives.
        Trims the "ARROR" suffix
        '''
        splitted = line.split('ARROW')
        if len(splitted) != 2 and\
                (splitted[0] not in {'LEFT', 'RIGHT', 'UP', 'DOWN'}):
            raise Exception(f'Invalid input: {line}. Allowed arrow inputs\
 are (UP|DOWN|LEFT|RIGHT)[ARROW]')
        result = 'HID_' + splitted[0]

        return result


class ExtendedConverter(LineConverter):
    allowed = ['SPACE', 'INSERT', 'ENTER', 'CAPSLOCK',
               'DELETE', 'END', 'HOME', 'INSERT', 'ESCAPE']

    def _convert(self, line: str) -> str:
        '''
        This method handles some additional special keys that are not typeable.
        '''
        if line in self.allowed:  # if line is only 1 keyword
            # quickfix space
            if line is 'SPACE':
                line = 'SPACEBAR'
            return 'HID_' + line
        else:
            raise Exception(f'One keyword per statement, got: "{line}"')


class DelayConverter(LineConverter):
    def _convert(self, line: str) -> str:
        '''
        This method parses the "DELAY" directive.
        Sleeping is done in C code so just check everything is okay here.

        Directive format is: DELAY <int>
        '''
        splitted = line.split()
        if len(splitted) != 2 or not self.try_parse(splitted[1], int)\
                or int(splitted[1]) < 0:
            raise ValueError('DELAY format is: DELAY <positive int>')

        # C code support delays multiple of 100(ms) and up to 8bit multiples
        # This means max delay supported currently is 100 * (2**8)
        delay = int(splitted[1])
        delay //= 100  # 100 is the current single delay
        if delay > 2**8:
            delay = 2**8 - 1  # max sleep is 2**8 - 1
        result = f'SLEEP_KEY, {delay}'
        return result

    def try_parse(self, val: str, t: type) -> bool:
        try:
            t(val)
            return True
        except ValueError:
            return False
