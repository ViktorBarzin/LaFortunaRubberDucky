from typing import List
import os


def get_lines(path: str) -> List[str]:
    with open(path, 'r') as f:
        return [x.replace('\n', '') for x in f.readlines()]  # remove \n at end


def replace_line(lines: List[str], to_replace: str,
                 replacement: str) -> List[str]:
    result = []
    for l in lines:
        if l.startswith(to_replace):
            result.append(replacement)
        else:
            result.append(l)
    return result


def create_array_string(type_of_arr: str, name: str, value: str) -> str:
    result = type_of_arr + ' ' + name + '[] = {' + value + '};'
    return result


def write_file(file_path: str, new_content: str) -> str:
    with open(file_path, 'w') as f:
        f.write(new_content)
    return new_content


def make(path: str) -> None:
    '''
    Go to `path` and run gnu make utility
    '''
    os.chdir(path)
    os.system('make')
