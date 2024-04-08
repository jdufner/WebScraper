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


class Treewalker:
    def __init__(self):
        logging.debug('')
        self.browser = webdriver.Chrome()

    def open(self):
        url: str = 'http://www.heise.de/'
        logging.info(f'Load {url}')
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

        self.find_links()

        time.sleep(timeout)
        self.browser.quit()

    def find_links(self) -> None:
        html_source_code = self.browser.execute_script("return document.body.innerHTML;")
        soup: BeautifulSoup = BeautifulSoup(html_source_code, 'html.parser')
        links = soup.find_all('a')
        links_len: int = len(links)
        index: int = 1
        for link in links:
            href: str = link.get('href')
            logging.debug(f'link ({index}/{links_len}) href = {href}')

        # links = self.browser.find_elements(By.XPATH, '//a[@href]')
        # links_len: int = len(links)
        # logging.debug(f'links number = {links_len}')
        # index: int = 1
        # for link in links:
        #     try:
        #         logging.debug(f'link ({index}/{links_len}), innerHTML = {link.get_attribute('innerHTML')}, '
        #                       f'href = {link.get_attribute('href')}')
        #     except StaleElementReferenceException:
        #         logging.error(f'Element {link.id} not found!')
        #     except TimeoutException:
        #         logging.error(f'Element {link.id} not found!')
        #     finally:
        #         index += 1

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
