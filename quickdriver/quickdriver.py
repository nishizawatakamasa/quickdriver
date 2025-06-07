# README https://github.com/nishizawatakamasa/quickdriver/blob/main/README.md

import functools
import re
import time
import unicodedata as ud
from collections.abc import Callable, Iterable
from typing import Literal

import pandas as pd
import tqdm
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import InvalidArgumentException, TimeoutException

type PageProcessor = Callable[[], Iterable[str] | None]
type Crawler = Callable[[list[str]], list[str]]

class QuickDriver:
    '''Wrapper for Selenium WebDriver.

    Attributes:
        self._driver: Instance of WebDriver.
        self._tables: A dictionary to store scraped data, with keys as saved names.
    '''
    def __init__(self, driver: WebDriver) -> None:
        self._driver = driver
        self._tables: dict[str, list[dict[str, str]]] = {}

    def ss(self, selector: str, from_: Literal['driver'] | WebElement | None = 'driver') -> list[WebElement]:
        '''Get web elements in the DOM matching a selector'''
        if from_ == 'driver':
            return self._driver.find_elements(By.CSS_SELECTOR, selector)
        return [] if from_ is None else from_.find_elements(By.CSS_SELECTOR, selector)

    def s(self, selector: str, from_: Literal['driver'] | WebElement | None = 'driver') -> WebElement | None:
        '''Get the first web element in the DOM matching a selector.'''
        return elems[0] if (elems := self.ss(selector, from_)) else None

    def ss_re(self, selector: str, pattern: str, from_: Literal['driver'] | WebElement | None = 'driver') -> list[WebElement]:
        '''Get web elements in the DOM matching the selector and the regex pattern.'''
        return [elem for elem in self.ss(selector, from_) if re.findall(pattern, ud.normalize('NFKC', self.attr('textContent', elem)))]

    def s_re(self, selector: str, pattern: str, from_: Literal['driver'] | WebElement | None = 'driver') -> WebElement | None:
        '''Get the first web element in the DOM matching the selector and the regex pattern.'''
        return elems[0] if (elems := self.ss_re(selector, pattern, from_)) else None

    def attr(self, attr_name: Literal['textContent', 'innerText', 'href', 'src'] | str, elem: WebElement | None) -> str | None:
        '''Get attribute value from web element.'''
        if elem:
            return attr.strip() if (attr := elem.get_attribute(attr_name)) else attr
        return None

    def next(self, elem: WebElement | None) -> WebElement | None:
        '''Get next sibling element.'''
        return self._driver.execute_script('return arguments[0].nextElementSibling;', elem) if elem else None

    def go_to(self, url: str) -> None:
        '''Go to the URL.'''
        try:
            self._driver.get(url)
        except (InvalidArgumentException, TimeoutException) as e:
            print(f'{type(e).__name__}: {e}')

    def click(self, elem: WebElement | None) -> None:
        '''Click on a web element.'''
        if elem:
            self._driver.execute_script('arguments[0].removeAttribute("target")', elem)
            self._driver.execute_script('arguments[0].click();', elem)

    def switch_to(self, iframe_elem: WebElement | None) -> None:
        '''Switch to iframe.'''
        self.scroll_to_view(iframe_elem)
        if iframe_elem:
            self._driver.switch_to.frame(iframe_elem)

    def scroll_to_view(self, elem: WebElement | None) -> None:
        '''Scroll to view the web element.'''
        if elem:
            self._driver.execute_script('arguments[0].scrollIntoView({behavior: "instant", block: "end", inline: "nearest"});', elem)

    def save_row(self, name_path: str, row: dict[str, str]) -> None:
        '''Save a row to a table with the specified name.'''
        self._tables.setdefault(name_path, []).append(row)
        pd.DataFrame(self._tables[name_path]).to_parquet(f'{name_path}.parquet')

    def progress(self, items: Iterable, target_func: Callable) -> tqdm:
        '''Displays a progress bar for a function performing iterations.'''
        return tqdm.tqdm(items, desc=f'{target_func.__name__}', bar_format='{desc}  {percentage:3.0f}%  {elapsed}  {remaining}')

    def crawl(self, *, delay: float | Callable[[], float]) -> Callable[[PageProcessor], Crawler]:
        '''Decorator to run a function on multiple pages with a mandatory delay between requests.'''
        def decorator(page_processor: PageProcessor) -> Crawler:
            @functools.wraps(page_processor)
            def crawler(page_urls: list[str]) -> list[str]:
                urls = []
                for page_url in self.progress(page_urls, page_processor):
                    self.go_to(page_url)
                    time.sleep(delay() if callable(delay) else delay)
                    if isinstance(hrefs := page_processor(), Iterable) and not isinstance(hrefs, (str, bytes)):
                        urls.extend(hrefs)
                return urls
            return crawler
        return decorator
