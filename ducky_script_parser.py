from abc import ABC, abstractmethod
from typing import List, Set

last_typed = ''


class DuckyScriptParser(object):
    '''
    Use this class to parse DuckyScript.
    It implements chain of responsibility pattern to match each type of line
    that can be found in the DuckyScript language
    '''
    def __init__(self):
        self.first_parser = CommentParser(set(['REM']))

        # Create chain of responsibility
        self.first_parser.set_next(StringParser(set(['STRING'])))\
                         .set_next(WindowsParser(set(['WINDOWS', 'GUI'])))\
                         .set_next(MenuParser(set(['MENU', 'APP'])))\
                         .set_next(ShiftParser(set(['SHIFT'])))\
                         .set_next(AltParser(set(['ALT'])))\
                         .set_next(ControlParser(set(['CONTROL', 'CTRL'])))\
                         .set_next(ArrorParser(set(['DOWNARROW', 'DOWN',
                                                    'LEFTARROW', 'LEFT',
                                                    'RIGHTARROW', 'RIGHT',
                                                    'UPARROW', 'UP'])))\
                         .set_next(
                             ExtendedParser(set(ExtendedParser.allowed)))\
                         .set_next(RepeatParser(set('REPEAT')))\
                         .set_next(DelayParser(set('DELAY')))

    def parse(self, lines: List[str]) -> str:
        global last_typed
        result = ''
        for line in lines:
            parsed = self.first_parser.handle(line)
            result += parsed + '\n'
            last_typed = parsed
        # Generate c code here instead of printing
        print(result)

        return result


class LineParser(ABC):
    def __init__(self, line_start: Set[str]):
        self.line_startings = line_start
        self.next_parser = None

    def set_next(self, parser):
        self.next_parser = parser
        return self.next_parser

    def handle(self, line: str) -> str:
        if self.__should_parse(line):
            parsed = self._parse(line)
            return parsed
        else:
            if self.next_parser is not None:
                return self.next_parser.handle(line)
            raise Exception(f'No available parser found to parse: {line}')

    @abstractmethod
    def _parse(self, line) -> str:
        '''
        This method parses the line and returns a string which has to be send
        from the keyboard device and ready to be converted to HID values.
        '''
        pass

    def __should_parse(self, line: str) -> bool:
        return any(
         [line.startswith(start) for start in self.line_startings]
        )


class CommentParser(LineParser):
    def _parse(self, line):
        '''
        Comments are ignored so just move on
        '''
        return


class StringParser(LineParser):
    def _parse(self, line: str) -> str:
        '''
        This method creates parses the "STRING" directive
        '''
        result = line.split(' ', 1)[1]
        return result


class WindowsParser(LineParser):
    def _parse(self, line: str) -> str:
        '''
        This method parses "GUI" and "WINDOWS" directives.
        The DuckyScript specification allows only a single char to be send with
        it so this implementation follows it.
        '''
        splitted = line.split()
        if len(splitted) == 1:
            # just keyword
            result = 'GUI'
        elif len(splitted) == 2:
            # keyword and char
            result = 'GUI ' + splitted[1]
        else:
            # disallow GUI and multiple buttons
            raise Exception(
                f'DuckyScript allows GUI button and maximum 1 char: {line}')

        return result


class MenuParser(LineParser):
    def _parse(self, line: str) -> str:
        '''
        This method parses "APP" and "MENU" directives.
        Returns a "SHIFT-F10" key combo
        '''
        result = 'SHIFT F10'

        return result


class ShiftParser(LineParser):
    allowed = ['DELETE', 'HOME', 'INSERT', 'PAGEUP', 'PAGEDOWN',
               'WINDOWS', 'GUI', 'UPARROW', 'DOWNARROW', 'LEFTARROW',
               'RIGHTARROW', 'TAB']

    def _parse(self, line: str) -> str:
        '''
        This method parses "SHIFT" directive.
        Capital letters are not written using shift but with caps lock.
        Shift is used for special combos - shift arrow, shift delete, etc...
        '''
        splitted = line.split()
        if len(splitted) == 1:
            # only shift
            result = 'SHIFT'

            return result
        elif len(splitted) == 2:
            # shift + special key
            # check if key is in allowed
            if not (splitted[1] in self.allowed):
                raise Exception(
                    f'"SHIFT" is allowed only in combination with: \
                    {self.allowed}')

            result = 'SHIFT' + splitted[1]

            return result  # return checked line
        else:
            raise Exception(
                f'"SHIFT" can be used with at most 1 argument, got: {line}')


class AltParser(LineParser):
    allowed = ['END', 'ESC', 'ESCAPE', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6',
               'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'SPACE', 'TAB']

    def _parse(self, line: str) -> str:
        '''
        This method parses "ALT" directive.
        A single optional parameter is allowed
        '''
        splitted = line.split()
        if len(splitted) == 1:
            # only alt
            result = 'ALT'

            return result
        elif len(splitted) == 2:
            # alt + special key or single char
            # if key is not in allowed, and (is not a letter, or has len > 1
            if splitted[1] not in self.allowed and\
                 (len(splitted[1]) != 1 or not splitted[1].isalpha()):
                raise Exception(
                    f'"ALT" is allowed only in combination with: \
                    {self.allowed} and any single chars')

            # quick fix escape
            if splitted[1] == 'ESC':
                splitted[1] = 'ESCAPE'
            result = 'ALT' + splitted[1]

            return result  # return checked line
        else:
            raise Exception(
                f'"ALT" can be used with at most 1 argument, got: {line}')


class ControlParser(LineParser):
    allowed = ['ENTER', 'BREAK', 'ESC', 'ESCAPE', 'F1', 'F2', 'F3', 'F4',
               'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'PAUSE']
    allowed_modifiers = ['ALT', 'SHIFT']

    def _parse(self, line: str) -> str:
        '''
        This method parses "Control" directive.
        A single optional parameter is allowed
        '''
        splitted = line.split()
        if len(splitted) == 2:
            # alt + special key or single char
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


class ArrorParser(LineParser):
    def _parse(self, line: str) -> str:
        '''
        This method parses arrow directives.
        Trims the "ARROR" suffix
        '''
        splitted = line.split('ARROW')
        if len(splitted) != 2 and\
                (splitted[0] not in {'LEFT', 'RIGHT', 'UP', 'DOWN'}):
            raise Exception(f'Invalid input: {line}. Allowed arrow inputs\
 are (UP|DOWN|LEFT|RIGHT)[ARROW]')
        result = splitted[0]

        return result


class ExtendedParser(LineParser):
    allowed = ['SPACE', 'INSERT', 'ENTER', 'CAPSLOCK',
               'DELETE', 'END', 'HOME', 'INSERT', 'ESCAPE']

    def _parse(self, line: str) -> str:
        '''
        This method handles some additional special keys that are not typeable.
        '''
        # For now just return the pressed key and deal with it elsewhere
        if line.replace('\n', '') in self.allowed:  # if line is only 1 keyword
            return line
        else:
            breakpoint()
            raise Exception(f'One keyword per statement, got: "{line}"')


class RepeatParser(LineParser):
    def _parse(self, line: str) -> str:
        '''
        This method parses the "REPEAT" directive.
        It repeats the last_typed n times.
        Does so by parsing is again and again n times
        '''
        global last_typed
        splitted = line.split()
        if len(splitted) != 2:
            breakpoint()
            raise Exception(
                f'"REPEAT" directive takes 1 int argument, got: {line}')
        # try parse argument as int
        times = int(splitted[1])

        # re-parse last command `times` times
        result = (last_typed + '\n') * times
        return result


class DelayParser(LineParser):
    def _parse(self, line: str) -> str:
        '''
        This method parses the "DELAY" directive.
        Sleeping is done in C code so just check everything is okay here.

        Directive format is: DELAY <int>
        '''
        splitted = line.split()
        if len(splitted) != 2 or not self.try_parse(splitted[1], int):
            raise ValueError('DELAY format is: DELAY <int>')
        return line

    def try_parse(self, val: str, t: type) -> bool:
        try:
            t(val)
            return True
        except ValueError:
            return False
