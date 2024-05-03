import logging
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from webscraper.page_downloader.url_list import UrlList
from webscraper.page_downloader.document import Document
from webscraper.page_downloader.downloader import Downloader
from webscraper.page_downloader.repository import PostgresqlRepository
from webscraper.page_downloader.repository import SqliteRepository
from webscraper.page_downloader.repository import Repository


class Walker:
    def __init__(self, config: dict) -> None:
        self.config: dict = config
        self.browser: WebDriver = webdriver.Chrome()
        self.blacklist: UrlList = UrlList(config["blacklist"])
        self.whitelist: UrlList = UrlList(config["whitelist"])
        if config["database"]["type"].lower() == 'postgres':
            self.repository: Repository = PostgresqlRepository(self.config)
        else:
            self.repository: Repository = SqliteRepository(self.config)

    def walk(self, url: str, number_pages: int) -> None:
        document: Document = Downloader(self.config, self.browser).open(url)
        self.repository.save_document(document)
        self.repository.set_link_downloaded(document.url)
        for index in range(number_pages):  # type index: int
            url: str = self.__get_next_url()
            document: Document = Downloader(self.config, self.browser).open(url)
            self.repository.save_document(document)
            self.repository.set_link_downloaded(url)
        self.__terminate()

    def __terminate(self) -> None:
        self.browser.quit()

    def __get_next_url(self) -> str:
        while True:
            id_url: tuple[id, str] = self.repository.get_next_link()
            logging.info(f'Got next url from database {id_url}')
            if (not self.whitelist.is_listed(id_url[1])) or self.blacklist.is_listed(id_url[1]):
                logging.info(f'Skip url because of not whitelisted or blacklisted {id_url[1]}')
                self.repository.set_link_skip(id_url[0])
            else:
                logging.debug(f'Next url {id_url[1]}')
                return id_url[1]
