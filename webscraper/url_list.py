import os
from urllib import parse
from urllib.parse import ParseResult


class UrlList:
    def __init__(self, urls: list[str]) -> None:
        self.blacks: list[ParseResult] = []
        for url in urls:
            parsed_line: ParseResult = parse.urlparse(url)
            self.blacks.append(parsed_line)

    def is_listed(self, url) -> bool:
        parsed_url = parse.urlparse(url)
        for black_url in self.blacks:
            if parsed_url.netloc == black_url.netloc and (parsed_url.path == '' or
                                                          parsed_url.path.startswith(black_url.path)):
                return True
        return False
