import logging
from datetime import datetime
import time

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from bs4 import ResultSet



class Treewalker:
    def __init__(self):
        logging.debug('')
        self.browser = webdriver.Chrome()

    def open(self, url: str) -> None:
        logging.info(f'Open {url}')
        self.browser.get(url)
        timeout: int = 3  # seconds
        time.sleep(timeout)

        loaded: bool = False
        cookies_consented: bool = False
        for _ in range(10):
            if not cookies_consented:
                cookies_consented = self.consent_cookies()
            if not loaded:
                loaded = self.loaded()

        soup: BeautifulSoup = self.get_and_parse_html_source()
        self.find_links(soup)
        self.extract_pics(soup)

        time.sleep(timeout)
        self.browser.quit()

    def get_and_parse_html_source(self) -> BeautifulSoup:
        html_source_code = self.browser.execute_script('return document.body.innerHTML;')
        soup: BeautifulSoup = BeautifulSoup(html_source_code, 'html.parser')
        return soup

    @staticmethod
    def find_links(soup: BeautifulSoup) -> list[str]:
        a_elements: ResultSet = soup.find_all('a')
        number_a_elements: int = len(a_elements)
        index: int = 1
        links: list[str] = []
        for a_element in a_elements:
            href: str = a_element.get('href')
            links.append(href)
            logging.debug(f'link ({index}/{number_a_elements}) href = {href}')
        return links

    def extract_pics(self, soup: BeautifulSoup) -> None:
        pass

    def loaded(self) -> bool:
        timeout: int = 1
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

    def consent_cookies(self) -> bool:
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
                    logging.info(f'Button {inner_html} clicked!')
            return True
        except TimeoutException:
            logging.info("No cookie consent found!")
            return False
        finally:
            self.browser.switch_to.default_content()
