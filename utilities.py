from typing import List


def get_lines(path: str) -> List[str]:
    with open(path, 'r') as f:
        return [x[:-1] for x in f.readlines()]  # remove the '\n' at the end
