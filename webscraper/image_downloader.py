import argparse
from argparse import Namespace
import cv2
from datetime import datetime
import json
import logging
import os
import re
import requests
from urllib import parse
from urllib.parse import ParseResult
from webscraper.url_list import UrlList
from webscraper.repository import PostgresqlRepository
from webscraper.repository import SqliteRepository
from webscraper.repository import Repository


class ImageDownloader:
    def __init__(self, config: dict):
        self.config = config
        self.blacklist = UrlList(config["blacklist"])
        self.whitelist = UrlList(config["whitelist"])
        if config["database"]["type"].lower() == 'postgres':
            self.repository: Repository = PostgresqlRepository(self.config)
        else:
            self.repository: Repository = SqliteRepository(self.config)
        self.session = requests.Session()

    def run(self):
        for i in range(config['number-images']):
            self.__download_next_image()

    def __download_next_image(self):
        id_url: tuple[int, str] = self.repository.get_next_image_url()
        self.url: str = id_url[1]
        self.parsed_url = parse.urlparse(self.url)
        self.__remove_parameter()
        self.__replace_part_of_path()
        if (not self.whitelist.is_listed(self.url) or self.blacklist.is_listed(self.url) or
                not self.__is_allowed_file_type()):
            logging.debug(f'Skip URL: {self.url}')
            self.repository.set_image_skip(id_url[0])
        else:
            logging.info(f'Download URL: {self.url}')
            filename = self.__download_image((id_url[0]))
            self.__analyze_image(id_url[0], filename)

    def __replace_part_of_path(self) -> None:
        match = re.match('(https?://\\w+.\\w+.\\w+/)(\\d+)(/[a-zA-Z0-9/_]+.jpg)', self.url)
        if match is not None:
            self.url = match[1] + '1280' + match[3]

    def __download_image(self, id_url: int) -> str:
        parsed_url: ParseResult = parse.urlparse(self.url)
        head_tail = os.path.split(parsed_url.path)
        logging.debug(f'Domain = {parsed_url.netloc}, Path = {head_tail[0]}, File = {head_tail[1]}')
        path: str = config["download"]["data-dir"] + '/' + parsed_url.netloc + head_tail[0]
        if not os.path.exists(path):
            os.makedirs(path)
        filename: str = path + '/' + head_tail[1]
        with open(filename, "wb") as f:
            f.write(self.session.get(self.url, stream=True).content)
        f.close()
        self.repository.set_image_downloaded(int(id_url))
        return filename

    def __analyze_image(self, image_id: int, filename: str) -> None:
        size: int = os.path.getsize(filename)
        image = cv2.imread(filename)
        image_height: int = image.shape[0]
        image_width: int = image.shape[1]
        logging.info(f'file {filename} has size = {size} and dimensions height = {image_height} and '
                     f'width = {image_width}')
        self.repository.update_image(image_id, filename, size, image_width, image_height)

    def __remove_parameter(self) -> None:
        self.url = parse.urlunsplit((self.parsed_url.scheme, self.parsed_url.netloc, self.parsed_url.path, None, None))

    def __is_allowed_file_type(self) -> bool:
        return any(self.url.endswith(ext) for ext in self.config['download']['file-types'])


def __parse_arguments() -> Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='A file containing all necessary config.')
    return parser.parse_args()


def __load_config() -> dict:
    args: Namespace = __parse_arguments()
    file = open(args.file)
    conf: dict = json.load(file)
    file.close()
    return conf


if __name__ == '__main__':
    config: dict = __load_config()
    now: datetime = datetime.now()
    if not os.path.exists(config["logging"]["path"]):
        os.makedirs(config["logging"]["path"])
    logging.basicConfig(filename=f'{config["logging"]["path"]}/{now: %Y-%m-%d_%Hh%Mm%Ss}_image_downloader.log',
                        encoding='utf-8',
                        format='%(asctime)s,%(msecs)-3d - %(levelname)-8s - %(filename)s:%(lineno)d - '
                               '%(module)s - %(funcName)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.getLevelNamesMapping()[config["logging"]["level"].upper()])
    ImageDownloader(config).run()
