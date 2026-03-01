# README https://github.com/nishizawatakamasa/quickdriver/blob/main/README.md

import re
import unicodedata as ud
from typing import Literal

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import InvalidArgumentException, TimeoutException

class QuickDriver:
    '''Wrapper for Selenium WebDriver.'''
    def __init__(self, driver: WebDriver) -> None:
        self._driver = driver

    def ss(self, selector: str, from_: Literal['driver'] | WebElement | None = 'driver') -> list[WebElement]:
        '''Get web elements in the DOM matching a selector.'''
        if from_ == 'driver':
            return self._driver.find_elements(By.CSS_SELECTOR, selector)
        return [] if from_ is None else from_.find_elements(By.CSS_SELECTOR, selector)

    def s(self, selector: str, from_: Literal['driver'] | WebElement | None = 'driver') -> WebElement | None:
        '''Get the first web element in the DOM matching a selector.'''
        return elems[0] if (elems := self.ss(selector, from_)) else None

    def ss_re(self, selector: str, pattern: str, from_: Literal['driver'] | WebElement | None = 'driver') -> list[WebElement]:
        '''Get web elements in the DOM matching the selector and the regex pattern.'''
        return [elem for elem in self.ss(selector, from_) if (text := self.attr('textContent', elem)) is not None and re.findall(pattern, ud.normalize('NFKC', text))]

    def s_re(self, selector: str, pattern: str, from_: Literal['driver'] | WebElement | None = 'driver') -> WebElement | None:
        '''Get the first web element in the DOM matching the selector and the regex pattern.'''
        return elems[0] if (elems := self.ss_re(selector, pattern, from_)) else None

    def attr(self, attr_name: Literal['textContent', 'innerText', 'href', 'src'] | str, elem: WebElement | None) -> str | None:
        '''Get attribute value from web element (strips whitespace).'''
        if elem:
            return attr.strip() if (attr := elem.get_attribute(attr_name)) else attr
        return None

    def next(self, elem: WebElement | None) -> WebElement | None:
        '''Get next sibling element via JavaScript.'''
        return self._driver.execute_script('return arguments[0].nextElementSibling;', elem) if elem else None

    def go_to(self, url: str | None) -> bool:
        '''Navigate to the URL and return True if successful. (Skips None and catches exceptions)'''
        if not url:
            return False
        try:
            self._driver.get(url)
            return True
        except Exception as e:
            print(f'{type(e).__name__}: {e}')
            return False

    def click(self, elem: WebElement | None) -> None:
        '''Click on a web element after removing target attribute to stay in the same tab.'''
        if elem:
            self._driver.execute_script('arguments[0].removeAttribute("target")', elem)
            self._driver.execute_script('arguments[0].click();', elem)

    def switch_to(self, iframe_elem: WebElement | None) -> None:
        '''Scroll to view and switch to the specified iframe.'''
        self.scroll_to_view(iframe_elem)
        if iframe_elem:
            self._driver.switch_to.frame(iframe_elem)

    def scroll_to_view(self, elem: WebElement | None) -> None:
        '''Scroll the element into view using JavaScript.'''
        if elem:
            self._driver.execute_script('arguments[0].scrollIntoView({behavior: "instant", block: "end", inline: "nearest"});', elem)
