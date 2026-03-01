# quickdriver

## Overview - 概要
QuickDriver is a wrapper for Selenium. By controlling WebDriver through QuickDriver, you can easily implement processes such as browser automation and scraping.

quickdriverはSeleniumのラッパーです。QuickDriverを介してWebDriverを操作することで、ブラウザの自動操作、スクレイピングなどの処理を簡単に実装できます。


## Installation - インストール
You can install quickdriver and all required dependencies from PyPI:

quickdriverとその実行に必要なライブラリは以下でインストールできます。

### pip
`pip install quickdriver`

### uv (recommended)
`uv add quickdriver`


## Requirements - 必要条件
To run quickdriver, you need the following environment:

quickdriverの実行には、以下の環境が必要です。

* Python 3.8 or higher
* Libraries:
    * selenium (version 4.27.1 or higher)

## Usage Example - 使用例
```py
import os
import random
import time
import pandas as pd

from selenium import webdriver as wd
from quickdriver import QuickDriver

options = wd.ChromeOptions()
options.add_argument('--incognito') # secret mode
options.add_argument('--start-maximized') # maximize a window
options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2}) # Image loading disabled

CSV_PATH = 'classroom_info.csv'

with wd.Chrome(options=options) as driver:   
    d = QuickDriver(driver)
    
    d.go_to('https://www.foobarbaz1.jp')
    pref_urls =[d.attr('href', e) for e in d.ss('li.item > ul > li > a')]
    
    classroom_urls =[]
    total = len(pref_urls)
    for i, url in enumerate(pref_urls, 1):
        print(f'{i}/{total} pref_urls')
        if not d.go_to(url):
            continue
        time.sleep(random.uniform(1, 2))
        links = [d.attr('href', e) for e in d.ss('.school-area h4 a')]
        classroom_urls.extend(links)

    total = len(classroom_urls)
    for i, url in enumerate(classroom_urls, 1):
        print(f'{i}/{total} classroom_urls')
        if not d.go_to(url):
            continue
        time.sleep(random.uniform(1, 2))
        row = {
            'URL': driver.current_url,
            '教室名': d.attr('textContent', d.s('h1 .text01')),
            '住所': d.attr('innerText', d.s('.item .mapText')),
            '電話番号': d.attr('textContent', d.s('.item .phoneNumber')),
            'HP': d.attr('href', d.s('a', d.next(d.s_re('th', 'ホームページ')))),
        }
        pd.DataFrame([row]).to_csv(
            CSV_PATH, 
            mode='a', 
            index=False, 
            header=not os.path.exists(CSV_PATH),
            encoding='utf-8-sig'
        )
```

## Basic Usage - 基本的な使い方
### QuickDriver Class
The quickdriver module consists of a single class: QuickDriver. This class wraps a Selenium WebDriver instance, providing convenient methods for interacting with web pages.

quickdriverモジュールは、QuickDriverクラス1つによって構成されています。QuickDriverクラスは、WebDriverのインスタンスを受け取ってSeleniumの処理をラップします。
```py
d = QuickDriver(driver)
```

### Methods
The QuickDriver class provides the following instance methods:

QuickDriverクラスは、以下のインスタンスメソッドによって構成されています。

* Get element - 要素を取得
    * [ss](#ss)
    * [s](#s)
    * [ss_re](#ss_re)
    * [s_re](#s_re)
* Get attribute value - 属性値を取得
    * [attr](#attr)
* Get next sibling element - 弟要素を取得
    * [next](#next)
* Operate Browser - ブラウザを操作
    * [go_to](#go_to)
    * [click](#click)
    * [switch_to](#switch_to)
    * [scroll_to_view](#scroll_to_view)

<a id="ss"></a>
#### 1. ss
Get multiple web elements as a list using a CSS selector. Returns an empty list if no elements are found. If a WebElement is passed as the second argument, the search is performed within that element's DOM subtree.

セレクタで複数のWeb要素をリストで取得します。存在しない場合は空のリストを返します。第二引数にWeb要素を渡すと、その要素のDOMサブセットからの取得となります。
```py
elems = d.ss('li.item > ul > li > a')
```
<a id="s"></a>
#### 2. s
Get a single web element using a CSS selector. If more than one element satisfies the condition, only the first one is returned. Returns None if no element is found. If a WebElement is passed as the second argument, the search is performed within that element's DOM subtree.

セレクタでWeb要素を取得します。条件を満たす要素が複数ある場合、最初の一つだけが返されます。存在しない場合はNoneを返します。第二引数にWeb要素を渡すと、その要素のDOMサブセットからの取得となります。
```py
elem = d.s('h1 .text01')
```
<a id="ss_re"></a>
#### 3. ss_re
Get multiple web elements as a list using a CSS selector and a regular expression to match the element's textContent. Returns an empty list if no elements are found. If a WebElement is passed as the third argument, the search is performed within that element's DOM subtree.

セレクタと、textContentに対する正規表現マッチングで複数のWeb要素をリストで取得します。存在しない場合は空のリストを返します。第三引数にWeb要素を渡すと、その要素のDOMサブセットからの取得となります。
```py
elems = d.ss_re('li.item > ul > li > a', r'店\s*舗')
```
<a id="s_re"></a>
#### 4. s_re
Get a single web element using a CSS selector and a regular expression to match the element's textContent. If more than one element satisfies the condition, only the first one is returned. Returns None if no element is found. If a WebElement is passed as the third argument, the search is performed within that element's DOM subtree.

セレクタと、textContentに対する正規表現マッチングでWeb要素を取得します。条件を満たす要素が複数ある場合、最初の一つだけが返されます。存在しない場合はNoneを返します。第三引数にWeb要素を渡すと、その要素のDOMサブセットからの取得となります。
```py
elem = d.s_re('table tbody tr th', r'住\s*所')
```
<a id="attr"></a>
#### 5. attr
Get the value of an attribute from a web element.

Web要素から任意の属性値を取得します。
```py
text = d.attr('textContent', elem)
```
<a id="next"></a>
#### 6. next
Get the next sibling element of a web element.

渡されたWeb要素の弟要素を取得します。
```py
next_elem = d.next(elem)
```
<a id="go_to"></a>
#### 7. go_to
Navigate to the specified URL.

指定したURLに遷移します。
```py
d.go_to('https://foobarbaz1.com')
```
<a id="click"></a>
#### 8. click
After removing the target attribute of the specified web element, the click event is fired.

指定したWeb要素のtarget属性を削除した後、clickイベントを発生させます。
```py
d.click(elem)
```
<a id="switch_to"></a>
#### 9. switch_to
Switch the driver's focus to the specified iframe element.

指定したiframe要素内に制御を移します。
```py
d.switch_to(iframe_elem)
```
<a id="scroll_to_view"></a>
#### 10. scroll_to_view
Scroll the page to bring the specified web element into view.

指定したWeb要素をスクロールして表示します。
```py
d.scroll_to_view(elem)
```

## License - ライセンス
[MIT](./LICENSE)
