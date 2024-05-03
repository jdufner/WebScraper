from bs4 import BeautifulSoup
from bs4 import ResultSet
from datetime import datetime
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
from webscraper.page_downloader.document import Document


class Downloader:
    def __init__(self, config: dict, browser: WebDriver):
        self.config = config
        self.browser: WebDriver = browser
        self.url = None
        self.html_source_code = None
        self.soup = None
        self.downloaded_at = datetime.now()
        self.title = ''
        self.created_at = []
        self.creators = []
        self.links = []
        self.image_urls = []

    def open(self, url: str) -> Document:
        logging.info(f'Open {url}')
        self.url: str = url
        self.browser.get(url)
        timeout: float = 1.0  # seconds
        time.sleep(timeout)
        self.__wait_until_cookies_consented_and_page_loaded()
        self.__get_and_parse_html_source()
        self.__find_first_title()
        self.__find_created_at()
        self.__find_creators()
        self.__find_links()
        self.__extract_images()
        return self.__build_document()

    def __get_and_parse_html_source(self) -> None:
        self.html_source_code = self.browser.execute_script('return document.documentElement.outerHTML;')
        self.soup: BeautifulSoup = BeautifulSoup(self.html_source_code, 'html.parser')

    def __find_first_title(self) -> None:
        title_elements: ResultSet = self.soup.css.select('head title')
        for title_element in title_elements:
            logging.debug(f'title of page {title_element.getText()}')
            title: str = title_element.getText().strip().replace('\n', ' ').replace('\r', '')
            self.title = ' '.join(title.split())
            break

    def __find_created_at(self) -> None:
        if self.url.endswith('.html'):
            time_elements: ResultSet = self.soup.css.select('div.a-publish-info time[datetime]')
            for time_element in time_elements:
                logging.debug(f'created at {time_element.get("datetime")}')
                self.created_at.append(time_element.get("datetime"))

    def __find_creators(self) -> None:
        if self.url.endswith('.html'):
            creator_elements: ResultSet = self.soup.css.select('div.creator ul li')
            for creator_element in creator_elements:
                logging.debug(f'created by {creator_element.getText()}')
                self.creators.append(creator_element.getText())

    def __find_links(self) -> None:
        a_elements: ResultSet = self.soup.find_all('a')
        number_a_elements: int = len(a_elements)
        index: int = 1
        for a_element in a_elements:
            href: str = a_element.get('href')
            href = self.__build_url(self.url, href)
            if href is not None and self.__filter_url(href) != '':
                if self.config["download"]["remove-parameter-query-fragment-from-url"].lower() == "true":
                    href = self.__remove_parameter_and_query_and_fragment(href)
                if len(href) > 1000:
                    logging.warning(f'URL is bigger than 1000 chars {href}')
                    break
                self.links.append(href)
                logging.debug(f'link ({index}/{number_a_elements}) href = {href}')
                if self.config["print-links"].lower() == 'true':
                    print(href)
                index += 1

    def __extract_images(self) -> None:
        img_elements: ResultSet = self.soup.find_all('img')
        number_img_elements: int = len(img_elements)
        index: int = 1
        # self.image_urls: list[str] = []
        for img_element in img_elements:
            src: str = img_element.get('src')
            src = self.__build_url(self.url, src)
            if src is not None and self.__filter_url(src) != '':
                if len(src) > 1000:
                    logging.warning(f'URL is bigger than 1000 chars {src}')
                    break
                self.image_urls.append(src)
                logging.debug(f'img ({index}/{number_img_elements}) src = {src}')
                if self.config["print-images"].lower() == 'true':
                    print(src)
                index += 1

    def __wait_until_cookies_consented_and_page_loaded(self):
        loaded: bool = False
        cookies_consented: bool = False
        for _ in range(1):
            if not cookies_consented:
                cookies_consented = self.__consent_cookies()
            if not loaded:
                loaded = self.__check_page_fully_loaded()

    def __check_page_fully_loaded(self) -> bool:
        timeout: float = 3.0
        try:
            self.browser.switch_to.default_content()
            self.__scroll_down_page_by_page()
            element_present = EC.presence_of_element_located((By.CSS_SELECTOR, self.config["download"]["footer"]))
            web_element: WebElement = WebDriverWait(self.browser, timeout).until(element_present)
            logging.info(f'Web_element {web_element} present!')
            return True
        except TimeoutException:
            logging.info("Loading took too much time!")
            return False

    def __scroll_down_page_by_page(self):
        timeout: float = 0.3  # seconds
        window_height: int = int(self.browser.execute_script("return window.innerHeight"))
        scroll_position: int = 0
        scroll_height: int = int(self.browser.execute_script("return document.body.scrollHeight"))
        index: int = 1
        logging.debug(f'index = {index}, '
                      f'windows_height / window.innerHeight = {window_height}, '
                      f'scroll_position = {scroll_position}, '
                      f'scroll_height / document.body.scrollHeight = {scroll_height}')
        while scroll_position < 0.99 * (scroll_height - window_height) and index <= 100:
            self.browser.execute_script(f'window.scrollTo(0, {index * window_height});')
            time.sleep(timeout)
            scroll_position = int(self.browser.execute_script("return window.pageYOffset + window.innerHeight"))
            new_scroll_height = int(self.browser.execute_script("return document.body.scrollHeight"))
            if new_scroll_height > scroll_height:
                index = -1
                scroll_height = new_scroll_height
            index += 1
            logging.debug(f'index = {index}, '
                          f'scroll_position / windowYOffset + window.innerHeight = {scroll_position}, '
                          f'scroll_height / document.body.scrollHeight = {scroll_height}')
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def __consent_cookies(self) -> bool:
        try:
            self.browser.switch_to.frame(self.browser.switch_to.active_element)
            logging.debug(f'browser title = {self.browser.title}')
            # self.browser.get_screenshot_as_file(f'./logs/pics/screenshot_{datetime.now(): %Y-%m-%d_%Hh%Mm%Ss}.png')
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
                    logging.info(f'Button clicked!')
            return True
        except NoSuchFrameException:
            logging.warning("No cookie consent found!")
            return True
        except TimeoutException:
            logging.warning("Cookie consent expected, but not found!")
            return False
        finally:
            self.browser.switch_to.default_content()

    def __build_document(self) -> Document:
        return Document(self.url, self.html_source_code if self.config["download"]["save-html"].lower() == 'true'
                        else '', self.title, self.downloaded_at, self.created_at, self.creators, self.links,
                        self.image_urls)

    @staticmethod
    def __build_url(base_url, url_or_path: str) -> str:
        parsed_url: ParseResult = parse.urlparse(url_or_path)
        # TODO: check base_url and throw exception if not valid
        if parsed_url.scheme == '' and parsed_url.netloc == '':
            url: str = parse.urljoin(base_url, url_or_path)
            return url
        return url_or_path

    @staticmethod
    def __remove_parameter_and_query_and_fragment(url: str) -> str:
        parsed_url: ParseResult = parse.urlparse(url)
        if parsed_url.params != '' or parsed_url.query != '' or parsed_url.fragment != '':
            new_url: str = parse.urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
            logging.warning(f'Remove parameter, query, and fragment from url {url} to {new_url}')
            return new_url
        return url

    @staticmethod
    def __filter_url(url) -> str:
        parsed_url: ParseResult = parse.urlparse(url)
        if parsed_url.scheme != '' and parsed_url.netloc != '':
            return url
        return ''
