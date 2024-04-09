from bs4 import BeautifulSoup
from bs4 import ResultSet
from datetime import datetime
from downloader.document import Document
import logging
from selenium.common.exceptions import NoSuchFrameException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from urllib import parse
from urllib.parse import ParseResult


class Downloader:
    def __init__(self, browser: WebDriver):
        # logging.debug('')
        self.browser: WebDriver = browser
        self.url = None
        self.html_source_code = None
        self.soup = None
        self.links = []
        self.image_urls = []

    def open(self, url: str) -> Document:
        logging.info(f'Open {url}')
        self.url: str = url
        self.browser.get(url)
        timeout: int = 1  # seconds
        time.sleep(timeout)
        self.__wait_until_cookies_consented_and_page_loaded()
        self.__get_and_parse_html_source()
        self.__find_published_at()
        self.__find_links()
        self.__extract_images()
        return self.__build_document()

    def __wait_until_cookies_consented_and_page_loaded(self):
        loaded: bool = False
        cookies_consented: bool = False
        for _ in range(5):
            if not cookies_consented:
                cookies_consented = self.__consent_cookies()
            if not loaded:
                loaded = self.__check_page_fully_loaded()

    def __get_and_parse_html_source(self) -> None:
        self.html_source_code = self.browser.execute_script('return document.body.innerHTML;')
        self.soup: BeautifulSoup = BeautifulSoup(self.html_source_code, 'html.parser')

    def __find_published_at(self):
        time_elements: ResultSet = self.soup.css.select('div.a-publish-info time')
        for time_element in time_elements:
            logging.debug(time_element.get('datetime'))
            # self.published_at = time_element.get('datetime')
            break

    def __find_links(self) -> None:
        a_elements: ResultSet = self.soup.find_all('a')
        number_a_elements: int = len(a_elements)
        index: int = 1
        # self.links: list[str] = []
        for a_element in a_elements:
            href: str = a_element.get('href')
            href = self.__build_url(self.url, href)
            if self.__filter_url(href) != '':
                self.links.append(href)
                logging.debug(f'link ({index}/{number_a_elements}) href = {href}')
                index += 1

    def __extract_images(self) -> None:
        img_elements: ResultSet = self.soup.find_all('img')
        number_img_elements: int = len(img_elements)
        index: int = 1
        # self.image_urls: list[str] = []
        for img_element in img_elements:
            src: str = img_element.get('src')
            src = self.__build_url(self.url, src)
            if self.__filter_url(src) != '':
                self.image_urls.append(src)
                logging.debug(f'img ({index}/{number_img_elements}) src = {src}')
                index += 1

    def __check_page_fully_loaded(self) -> bool:
        timeout: float = 1.0
        try:
            self.browser.switch_to.default_content()
            scroll_position: int = int(self.browser.execute_script("return window.pageYOffset + window.innerHeight"))
            logging.debug(f'scroll position before scrolling = {scroll_position}')
            scroll_height: int = self.browser.execute_script("return document.body.scrollHeight")
            logging.debug(f'scroll height = {scroll_height}')
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            scroll_position: int = int(self.browser.execute_script("return window.pageYOffset + window.innerHeight"))
            logging.debug(f'scroll position after scrolling = {scroll_position}')
            element_present = EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'html body div.container div footer.text-center a'))
            web_element: WebElement = WebDriverWait(self.browser, timeout).until(element_present)
            logging.info(f'Web_element {web_element.get_attribute("innerHTML")} present!')
            return True
        except TimeoutException:
            logging.info("Loading took too much time!")
            return False

    def __consent_cookies(self) -> bool:
        try:
            self.browser.switch_to.frame(self.browser.switch_to.active_element)
            logging.debug(f'browser title = {self.browser.title}')
            self.browser.get_screenshot_as_file(f'./logs/pics/screenshot_{datetime.now(): %Y-%m-%d_%Hh%Mm%Ss}.png')
            buttons = self.browser.find_elements(By.CSS_SELECTOR, 'button[title="Zustimmen"]')  # type: list[WebElement]
            for button in buttons:
                inner_html: str = button.get_attribute("innerHTML")
                title: str = button.get_attribute('title')
                logging.debug(f'button id = {button.id}, '
                              f'innerHTML = {inner_html}, '
                              f'title = {title}, displayed = {button.is_displayed()}, '
                              f'enabled = {button.is_enabled()}')
                if button.is_displayed():
                    button.click()
                    logging.info(f'Button {inner_html} clicked!')
            return True
        except NoSuchFrameException:
            logging.info("No cookie consent found!")
            return True
        except TimeoutException:
            logging.info("No cookie consent found!")
            return False
        finally:
            self.browser.switch_to.default_content()

    def __build_document(self) -> Document:
        return Document(self.url, self.html_source_code, datetime.now(), self.links, self.image_urls)

    @staticmethod
    def __build_url(base_url, url_or_path: str) -> str:
        parsed_url: ParseResult = parse.urlparse(url_or_path)
        # TODO: check base_url and throw exception if not valid
        if parsed_url.scheme == '' and parsed_url.netloc == '':
            url: str = parse.urljoin(base_url, url_or_path)
            return url
        return url_or_path

    @staticmethod
    def __filter_url(url) -> str:
        parsed_url: ParseResult = parse.urlparse(url)
        if parsed_url.scheme != '' and parsed_url.netloc != '':
            return url
        return ''
