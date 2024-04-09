import logging

from downloader.blacklist import Blacklist
from downloader.document import Document
from downloader.downloader import Downloader
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from urllib import parse
from urllib.parse import ParseResult


class Walker:
    def __init__(self) -> None:
        self.browser: WebDriver = webdriver.Chrome()
        self.blacklist: Blacklist = Blacklist()
        self.already_downloaded_documents = []
        self.to_be_downloaded_documents = []

    def walk(self, url: str, number_pages: int) -> None:
        downloader = Downloader(self.browser)
        document: Document = downloader.open(url)
        self.already_downloaded_documents.append(document.url)
        self.to_be_downloaded_documents.extend(document.links)
        for index in range(number_pages):  # type index: int
            logging.info(self.already_downloaded_documents)
            logging.info(self.to_be_downloaded_documents)
            url: str = self.__get_next_url()
            document: Document = downloader.open(url)
            self.already_downloaded_documents.append(url)
            self.to_be_downloaded_documents.extend(document.links)
        self.__terminate()

    def __terminate(self) -> None:
        self.browser.quit()

    def __get_next_url(self) -> str:
        while True:
            if len(self.to_be_downloaded_documents) <= 0:
                return ''
            url: str = self.to_be_downloaded_documents.pop(0)
            if (not self.blacklist.is_listed(url)) and (not self.__already_downloaded(url)):
                return url

    def __already_downloaded(self, url: str) -> bool:
        parsed: ParseResult = parse.urlparse(url)
        for already_downloaded_url in self.already_downloaded_documents:
            already_downloaded: ParseResult = parse.urlparse(already_downloaded_url)
            if (already_downloaded.netloc == parsed.netloc) and (already_downloaded.path == parsed.path):
                return True
        return False
