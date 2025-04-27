# quickdriver

## Overview - 概要
quickdriver is a wrapper for Selenium. It simplifies browser automation, web scraping, data saving, and other tasks by providing an easy-to-use interface to WebDriver.

quickdriverはSeleniumのラッパーです。QuickDriverを介してWebDriverを操作することで、ブラウザの自動操作、スクレイピング、データ保存などの処理を簡単に実装できます。


## Installation - インストール
You can install quickdriver and all the libraries needed to run it using pip: 

quickdriverとその実行に必要な全てのライブラリは以下のコマンドでインストールできます。  

`pip install quickdriver`


## Requirements - 必要条件
To run quickdriver, you need the following environment:

quickdriverの実行には、以下の環境が必要です。

* Python 3.8 or higher
* Libraries:
    * pandas (version 2.2.3 or higher)
    * selenium (version 4.27.1 or higher)
    * tqdm (version 4.67.1 or higher)
    * pyarrow (version 16.1.0 or higher)


## Usage Example - 使用例
```py
from selenium import webdriver as wd
from quickdriver import QuickDriver

options = wd.ChromeOptions()
options.add_argument('--incognito') # secret mode
# options.add_argument('--headless=new') # headless mode
options.add_argument('--start-maximized') # maximize a window
options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2}) # Image loading disabled
# options.add_argument(r'--user-data-dir=C:\Users\xxxx\AppData\Local\Google\Chrome\User Data') # User profile destination path
# options.add_argument('--profile-directory=Profile xx') # User profile directory name

with wd.Chrome(options=options) as driver:   
    d = QuickDriver(driver)
    
    @d.crawl
    def prefectures():
        return [d.attr('href', e) for e in d.ss('li.item > ul > li > a')]
        
    @d.crawl
    def each_classroom():
        return [d.attr('href', e) for e in d.ss('.school-area h4 a')]
    
    @d.crawl
    def scrape_classroom_info():
        d.save_row('./classroom_info', {
            'URL': driver.current_url,
            '教室名': d.attr('textContent', d.s('h1 .text01')),
            '住所': d.attr('innerText', d.s('.item .mapText')),
            '電話番号': d.attr('textContent', d.s('.item .phoneNumber')),
            'HP': d.attr('href', d.s('a', d.next_sib(d.s_re('th', 'ホームページ')))),
        })
    
    scrape_classroom_info(each_classroom(prefectures(['https://www.foobarbaz1.jp'])))
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
* Get parent/sibling element - 親、兄、弟要素を取得
    * [parent](#parent)
    * [prev_sib](#prev_sib)
    * [next_sib](#next_sib)
* Add class to element - 要素にクラスを追加
    * [add_class](#add_class)
* Operate Browser - ブラウザを操作
    * [go_to](#go_to)
    * [click](#click)
    * [switch_to](#switch_to)
    * [scroll_to_view](#scroll_to_view)
* Save Data - データを保存
    * [save_row](#save_row)
* Show progress - 進捗を表示
    * [progress](#progress)
* Create crawler - クローラーを作成
    * [crawl](#crawl)

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
<a id="parent"></a>
#### 6. parent
Get the parent element of a web element.

渡されたWeb要素の親要素を取得します。
```py
parent_elem = d.parent(elem)
```
<a id="prev_sib"></a>
#### 7. prev_sib
Get the previous sibling element of a web element.

渡されたWeb要素の兄要素を取得します。
```py
prev_elem = d.prev_sib(elem)
```
<a id="next_sib"></a>
#### 8. next_sib
Get the next sibling element of a web element.

渡されたWeb要素の弟要素を取得します。
```py
next_elem = d.next_sib(elem)
```
<a id="add_class"></a>
#### 9. add_class
Add a class to the specified web elements. This can be useful for targeting elements that are difficult to select using CSS selectors alone.

Web要素にクラスを追加して目印にします。これにより、Web要素のあらゆる取得条件をセレクタで表現できるようになります。
```py
d.add_class(elems, 'mark-001')
```
<a id="go_to"></a>
#### 10. go_to
Navigate to the specified URL.

指定したURLに遷移します。
```py
d.go_to('https://foobarbaz1.com')
```
<a id="click"></a>
#### 11. click
Trigger the click event on a web element. If a new tab is opened, switches to the new tab (disabled with tab_switch=False).

指定したWeb要素のclickイベントを発生させます。クリック時に新しいタブが開かれた場合は、そのタブに遷移します (tab_switch=False で無効化)。
```py
d.click(elem)
```
<a id="switch_to"></a>
#### 12. switch_to
Switch the driver's focus to the specified iframe element.

指定したiframe要素内に制御を移します。
```py
d.switch_to(iframe_elem)
```
<a id="scroll_to_view"></a>
#### 13. scroll_to_view
Scroll the page to bring the specified web element into view.

指定したWeb要素をスクロールして表示します。
```py
d.scroll_to_view(elem)
```
<a id="save_row"></a>
#### 14. save_row
Add a row to a table (creates the table if it doesn't exist) and save it as a Parquet file. The table name is determined by the provided path.

パス形式の名前で指定したテーブルデータ(無い場合は作成されます)に行を追加し、Parquetファイルとして保存します (拡張子の記述は不要)。
```py
d.save_row('./scrape/foo', {
    '列名1': text01,
    '列名2': text02,
    '列名3': text03,
})
```
<a id="progress"></a>
#### 15. progress
Display a progress bar for a function that iterates over a list of URLs.

urlリストの各ページに対して処理を行っていく関数の進捗状況を表示します。
```py
for page_url in d.progress(page_urls, func):
    d.go_to(page_url)
    func()
```
<a id="crawl"></a>
#### 16. crawl
Decorator. Modifies the decorated function to accept a list of URLs as input. The function will be executed for each URL, and if the function returns a list of URLs, those URLs will be added to the list of URLs to crawl.

デコレータ。付与された関数は、URL文字列のリストを引数として受け取るようになります。URLリストを渡すと、そのURLに順番にアクセスしていき、各ページに対して関数の処理を実行するようになります。関数の処理がURL文字列のリストを返す場合、最終的な戻り値はそれら全てを結合したリストとなります。
```py
@d.crawl
def foo():
    # 略
```

## License - ライセンス
[MIT](./LICENSE)
