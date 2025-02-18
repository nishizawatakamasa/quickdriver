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

class QuickDriver:
    '''Wrapper for Selenium WebDriver。

    Attributes:
        self._driver: WebDriverのインスタンス。
        self._tables: 辞書。キーはテーブルデータの保存名。値はスクレイピング結果の辞書を格納したリスト。
    '''
    def __init__(self, driver: WebDriver) -> None:
        self._driver = driver
        self._tables: dict[str, list[dict[str, str]]] = {}

    def ss(self, selector: str, from_: Literal['driver'] | WebElement | None = 'driver') -> list[WebElement]:
        '''セレクタを使用し、DOM(全体かサブセット)からWeb要素をリストで取得。'''
        if from_ == 'driver':
            return self._driver.find_elements(By.CSS_SELECTOR, selector)
        return [] if from_ is None else from_.find_elements(By.CSS_SELECTOR, selector)

    def s(self, selector: str, from_: Literal['driver'] | WebElement | None = 'driver') -> WebElement | None:
        '''セレクタを使用し、DOM(全体かサブセット)からWeb要素を取得。'''
        return elems[0] if (elems := self.ss(selector, from_)) else None

    def ss_re(self, selector: str, pattern: str, from_: Literal['driver'] | WebElement | None = 'driver') -> list[WebElement]:
        '''セレクタと正規表現を使用し、DOM(全体かサブセット)からWeb要素をリストで取得。'''
        return [elem for elem in self.ss(selector, from_) if re.findall(pattern, ud.normalize('NFKC', self.attr('textContent', elem)))]

    def s_re(self, selector: str, pattern: str, from_: Literal['driver'] | WebElement | None = 'driver') -> WebElement | None:
        '''セレクタと正規表現を使用し、DOM(全体かサブセット)からWeb要素を取得。'''
        return elems[0] if (elems := self.ss_re(selector, pattern, from_)) else None

    def attr(self, attr_name: Literal['textContent', 'innerText', 'href', 'src'] | str, elem: WebElement | None) -> str | None:
        '''Web要素から任意の属性値を取得。'''
        if elem:
            return attr.strip() if (attr := elem.get_attribute(attr_name)) else attr
        return None

    def parent(self, elem: WebElement | None) -> WebElement | None:
        '''渡されたWeb要素の親要素を取得。'''
        return self._driver.execute_script('return arguments[0].parentElement;', elem) if elem else None

    def prev_sib(self, elem: WebElement | None) -> WebElement | None:
        '''渡されたWeb要素の兄要素を取得。'''
        return self._driver.execute_script('return arguments[0].previousElementSibling;', elem) if elem else None

    def next_sib(self, elem: WebElement | None) -> WebElement | None:
        '''渡されたWeb要素の弟要素を取得。'''
        return self._driver.execute_script('return arguments[0].nextElementSibling;', elem) if elem else None

    def add_class(self, elems: list[WebElement], class_name: str) -> None:
        '''Web要素に任意のクラスを追加する。'''
        for elem in elems:
            self._driver.execute_script(f'arguments[0].classList.add("{class_name}");', elem)

    def go_to(self, url: str) -> None:
        '''指定したURLに遷移。'''
        try:
            self._driver.get(url)
        except (InvalidArgumentException, TimeoutException) as e:
            print(f'{type(e).__name__}: {e}')
        else:
            time.sleep(1)

    def click(self, elem: WebElement, tab_switch: bool = True) -> None:
        '''Web要素をクリックする。新しいタブが開かれた場合はそのタブに遷移する(tab_switch=Falseで無効化)。'''
        if elem:
            self._driver.execute_script('arguments[0].click();', elem)
            time.sleep(1)
            if tab_switch and len(self._driver.window_handles) == 2:
                self._driver.close()
                self._driver.switch_to.window(self._driver.window_handles[-1])

    def switch_to(self, iframe_elem: WebElement) -> None:
        '''指定したiframeの中に制御を移す。'''
        self.scroll_to_view(iframe_elem)
        if iframe_elem:
            self._driver.switch_to.frame(iframe_elem)

    def scroll_to_view(self, elem: WebElement | None) -> None:
        '''スクロールして、指定Web要素を表示する。'''
        if elem:
            self._driver.execute_script('arguments[0].scrollIntoView({behavior: "instant", block: "end", inline: "nearest"});', elem)
            time.sleep(1)

    def save_row(self, name_path: str, row: dict[str, str]) -> None:
        '''指定した名前のテーブルデータ(無い場合は作成される)に行を追加。行は列名と値が要素の辞書。テーブルデータはparquetファイルとして保存される。'''
        if name_path not in self._tables.keys():
            self._tables[name_path] = []
        self._tables[name_path].append(row)
        pd.DataFrame(self._tables[name_path]).to_parquet(f'{name_path}.parquet')

    def use_tqdm(self, items: Iterable, target_func: Callable) -> tqdm:
        '''繰り返し処理を行う関数の進捗状況を表示する。'''
        return tqdm.tqdm(items, desc=f'{target_func.__name__}', bar_format='{desc}  {percentage:3.0f}%  {elapsed}  {remaining}')

    def crawl(self, proc_page: Callable[[], Iterable[str] | None]) -> Callable[[list[str]], list[str]]:
        '''page_urlsの各ページに対し、proc_pageが実行されるようになる。さらにproc_pageがhrefsを返す場合、それら全てを結合したリストを返すようになる。'''
        @functools.wraps(proc_page)
        def wrapper(page_urls: list[str]) -> list[str]:
            urls = []
            for page_url in self.use_tqdm(page_urls, proc_page):
                self.go_to(page_url)
                if isinstance(hrefs := proc_page(), Iterable):
                    urls.extend(hrefs)
            return urls
        return wrapper
