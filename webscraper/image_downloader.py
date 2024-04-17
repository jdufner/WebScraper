import argparse
from argparse import Namespace
from datetime import datetime
import json
import logging
import os
import requests
from urllib import parse
from urllib.parse import ParseResult
from webscraper.blacklist import Blacklist
from webscraper.repository import PostgresqlRepository
from webscraper.repository import SqliteRepository
from webscraper.repository import Repository


class ImageDownloader:
    def __init__(self, config: dict):
        self.config = config
        self.blacklist = Blacklist(config["blacklist"])
        if config["database"]["type"].lower() == 'postgres':
            self.repository: Repository = PostgresqlRepository(self.config)
        else:
            self.repository: Repository = SqliteRepository(self.config)

    def run(self):
        id_url: tuple[int, str] = self.repository.get_next_image_url()
        if self.blacklist.is_listed(id_url[1]):
            logging.debug(f'Skip URL: {id_url[1]}')
            self.repository.set_image_skip(id_url[0])
        else:
            logging.info(f'Download URL: {id_url[1]}')
            parsed_url: ParseResult = parse.urlparse(id_url[1])
            head_tail = os.path.split(parsed_url.path)
            logging.debug(f'Domain = {parsed_url.netloc}, Path = {head_tail[0]}, File = {head_tail[1]}')
            path: str = config["download"]["data-dir"] + '/' + parsed_url.netloc + head_tail[0]
            os.makedirs(path)
            with open(path + '/' + head_tail[1], "wb") as f:
                f.write(requests.get(id_url[1]).content)
            f.close()
            self.repository.set_image_downloaded(int(id_url[0]))


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
