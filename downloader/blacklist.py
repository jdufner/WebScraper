import os
from urllib import parse
from urllib.parse import ParseResult


class Blacklist:
    def __init__(self) -> None:
        if os.path.exists('blacklist.txt'):
            # with open('blacklist.txt') as file:
            #     self.lines = [line.rstrip() for line in file]
            self.blacks: list[ParseResult] = []
            with open('blacklist.txt') as file:
                for line in file:
                    parsed_line: ParseResult = parse.urlparse(line.rstrip())
                    self.blacks.append(parsed_line)

    def is_listed(self, url) -> bool:
        parsed_url = parse.urlparse(url)
        for black_url in self.blacks:
            if parsed_url.netloc == black_url.netloc and parsed_url.path.startswith(black_url.path):
                return True
        return False

