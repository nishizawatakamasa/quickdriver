# quickdriver

## 概要
quickdriverは、Seleniumを簡単に使うためのPythonモジュールです。  
ブラウザの自動操作、スクレイピング、データの保存などを簡単に行えます。

## インストール方法
quickdriverと、quickdriverの実行に必要な全てのPythonライブラリは、以下のコマンドでインストールできます。  
`pip install git+https://github.com/nishizawatakamasa/quickdriver`

## 必要な環境
quickdriverの実行には、以下の環境が必要です。
* Python3.8以上
* ライブラリ
    * pandas(バージョン2.2.3以上)
    * selenium(バージョン4.27.1以上)
    * tqdm(バージョン4.67.1以上)
    * pyarrow(バージョン16.1.0以上)

## 使用例
```py
from selenium import webdriver as wd
from quickdriver import QuickDriver

options = wd.ChromeOptions()
options.add_argument('--incognito') # シークレットモード
# options.add_argument('--headless=new') # ヘッドレスモード
options.add_argument('--start-maximized') # ウィンドウ最大化
options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2}) # 画像読み込み無効
# options.add_argument(r'--user-data-dir=C:\Users\xxxx\AppData\Local\Google\Chrome\User Data') # 使用するユーザープロファイルの保存先パス
# options.add_argument('--profile-directory=Profile xx') # 使用するユーザープロファイルのディレクトリ名

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
            'HP': d.attr('href', d.s('a', d.next_sib(d.s_re(th, 'ホームページ')))),
        })
    
    scrape_classroom_info(each_classroom(prefectures(['https://www.foobarbaz1.jp'])))
```

## 基本的な使い方
### QuickDriverクラス
quickdriverモジュールは、QuickDriverクラス1つによって構成されています。  
QuickDriverクラスは、WebDriverのインスタンスを受け取ってSeleniumの処理をラップします。
```py
d = QuickDriver(driver)
```

### QuickDriverクラスのメソッド
QuickDriverクラスは、以下のインスタンスメソッド16個によって構成されています。

#### 1. ss
セレクタで複数のWeb要素をリストで取得。存在しない場合は空のリスト。  
第二引数にWeb要素を渡すと、そのDOMサブセットからの取得となる。
```py
elems = d.ss('li.item > ul > li > a')
```
#### 2. s
セレクタでWeb要素を取得。存在しない場合はNone。  
第二引数にWeb要素を渡すと、そのDOMサブセットからの取得となる。
```py
elem = d.s('h1 .text01')
```
#### 3. ss_re
セレクタと正規表現で複数のWeb要素をリストで取得。存在しない場合は空のリスト。  
正規表現によるWeb要素のフィルタリングにはre_filterが使われる。  
第三引数にWeb要素を渡すと、そのDOMサブセットからの取得となる。
```py
elems = d.ss_re('li.item > ul > li > a', r'店\s*舗')
```
#### 4. s_re
セレクタと正規表現でWeb要素を取得。存在しない場合はNone。  
正規表現によるWeb要素のフィルタリングにはre_filterが使われる。  
第三引数にWeb要素を渡すと、そのDOMサブセットからの取得となる。
```py
elem = d.s_re('table tbody tr th', r'住\s*所')
```
#### 5. attr
Web要素から任意の属性値を取得。
```py
text = d.attr('textContent', elem)
```
#### 6. parent
渡されたWeb要素の親要素を取得。
```py
parent_elem = d.parent(elem)
```
#### 7. prev_sib
渡されたWeb要素の兄要素を取得。
```py
prev_elem = d.prev_sib(elem)
```
#### 8. next_sib
渡されたWeb要素の弟要素を取得。
```py
next_elem = d.next_sib(elem)
```
#### 9. add_class
Web要素に任意のクラスを追加して目印にする。  
これにより、Web要素のあらゆる取得条件をセレクタで表現できるようになる。
```py
d.add_class(elems, 'mark-001')
```
#### 10. go_to
指定したURLに遷移する。
```py
d.go_to('https://foobarbaz1.com')
```
#### 11. click
指定したWeb要素のclickイベントを発生させる。  
クリック時に新しいタブが開かれた場合は、そのタブに遷移(tab_switch=Falseで無効化)。
```py
d.click(elem)
```
#### 12. switch_to
指定したiframe要素内に制御を移す。
```py
d.switch_to(iframe_elem)
```
#### 13. scroll_to_view
指定したWeb要素をスクロールして表示する。
```py
d.scroll_to_view(elem)
```
#### 14. save_row
パス指定したテーブルデータ(無い場合は作成される)に行を追加し、parquetファイルとして保存(拡張子の記述は不要)。
```py
d.save_row('./scrape/foo', {
    '列名1': text01,
    '列名2': text02,
    '列名3': text03,
})
```
#### 15. progress
urlリストの各ページに対して処理を行っていく関数の進捗状況を表示する。
```py
for page_url in d.progress(page_urls, func):
    d.go_to(page_url)
    func()
```
#### 16. crawl
デコレータ。  
付与された関数は、URL文字列のリストを引数として受け取るようになる。  
URLリストを渡すと、そのURLに順番にアクセスしていき、各ページに対して関数の処理を実行するようになる。  
関数の処理がURL文字列のリストを返す場合、それら全てを結合したリストが最終的な戻り値となる。
```py
@d.crawl
def foo():
    # 略
```
