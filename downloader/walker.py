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
        document: Document = Downloader(self.browser).open(url)
        self.already_downloaded_documents.append(document.url)
        self.to_be_downloaded_documents.extend(document.links)
        for index in range(number_pages):  # type index: int
            logging.info(f'already downloaded urls({len(self.already_downloaded_documents)}): {self.already_downloaded_documents}')
            logging.info(f'to be downloaded urls({len(self.to_be_downloaded_documents)}): {self.to_be_downloaded_documents}')
            url: str = self.__get_next_url()
            document: Document = Downloader(self.browser).open(url)
            self.already_downloaded_documents.append(url)
            self.__append_links_to_to_be_downloaded(document.links)
            # self.to_be_downloaded_documents.extend(document.links)
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

    def __append_links_to_to_be_downloaded(self, new_links: [str]):
        for url in new_links:
            if (not self.blacklist.is_listed(url)) and (not self.__already_in_to_be_downloaded(url)):
                self.to_be_downloaded_documents.append(url)

    def __already_in_to_be_downloaded(self, url: str) -> bool:
        parsed: ParseResult = parse.urlparse(url)
        for to_be_downloaded_url in self.to_be_downloaded_documents:
            to_be_downloaded: ParseResult = parse.urlparse(to_be_downloaded_url)
            if (to_be_downloaded.netloc == parsed.netloc) and (to_be_downloaded.path == parsed.path):
                return True
        return False
