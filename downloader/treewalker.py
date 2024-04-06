import logging
import time

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


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
        html_source_code = self.browser.execute_script("return document.body.innerHTML;")
        time.sleep(timeout)
        html_source_code = self.browser.execute_script("return document.body.innerHTML;")

        links = self.browser.find_elements(By.CSS_SELECTOR, 'button.message-button')  # type: list[WebElement]
        for link in links:
            logging.debug(f'link innerHTML = {link.get_attribute("innerHTML")}')

        try:
            logging.debug(f'Try to get an <button class="message-button" title="Zustimmen"> element')
            web_element = WebDriverWait(self.browser, 3.0).until(EC.presence_of_element_located(
                # (By.CSS_SELECTOR, 'button.message-button')))
                (By.XPATH, '//button[@title="Zustimmen"]')))
            logging.debug(f'element {web_element.get_attribute("innerHTML")}')
        except TimeoutException:
            logging.debug('Timeout of EC.presence_of_element_located')
        # finally:

        # try:
        #     logging.debug(f'Try to get an <a> element')
        #     web_element = WebDriverWait(self.browser, 10.0).until(EC.presence_of_element_located(
        #         (By.TAG_NAME, 'a')))
        #     logging.debug(f'element {web_element}')
        # except TimeoutException:
        #     logging.debug('Timeout of EC.presence_of_element_located')
        # finally:

        # try:
        #     logging.debug(f'Try to get an <a>nach oben</a> element')
        #     web_element = WebDriverWait(self.browser, 10.0).until(EC.text_to_be_present_in_element(
        #         (By.TAG_NAME, 'a'), 'nach oben'))
        #     logging.debug(f'element {web_element}')
        # except TimeoutException:
        #     logging.debug('Timeout of EC.text_to_be_present_in_element')
        # finally:

        # try:
        #     logging.debug(f'Try to get an <a href="#top"> element')
        #     web_element = WebDriverWait(self.browser, 10.0).until(EC.text_to_be_present_in_element_attribute(
        #         (By.TAG_NAME, 'a'), 'href', '#top'))
        #     logging.debug(f'element {web_element}')
        # except TimeoutException:
        #     logging.debug('Timeout of EC.text_to_be_present_in_element_attribute')
        # finally:

        loaded: bool = False
        cookies_consented: bool = False
        for _ in range(10):
            # html_soup: BeautifulSoup = BeautifulSoup(html_source_code, 'html.parser')
            if not cookies_consented:
                cookies_consented = self.consent_cookies()
            if not loaded:
                loaded = self.loaded()

        self.browser.quit()

    def loaded(self) -> bool:
        timeout: int = 1
        try:
            element_present = EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'html body div.container div footer.text-center a'))
            web_element: WebElement = WebDriverWait(self.browser, timeout).until(element_present)
            logging.info(f'Page is ready! web_element {web_element.get_attribute("innerHTML")} found!')
            return True
        except TimeoutException:
            logging.info("Loading took too much time!")
            return False

    def consent_cookies(self) -> bool:
        timeout: int = 1
        try:
            element_visible = EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 'button[title="Zustimmen"]'))
            web_element: WebElement = WebDriverWait(self.browser, timeout).until(element_visible)
            # web_element.click()
            logging.info(f'Consented cookies! web_element {web_element.get_attribute("innerHTML")} found!')
            return True
        except TimeoutException:
            logging.info("No cookie consent found!")
            return False
