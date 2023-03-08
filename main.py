from scraping_time import ScrapingTime
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from create_file import CsvWriter, JsonWriter, SQLiteDB
from selenium.common.exceptions import SessionNotCreatedException


class WebScraping:
    def __init__(self, url: str):
        # ニュース情報を保持するリスト
        self.news_list = []
        # カテゴリーリスト
        self.category = [
            "domestic",
            "world",
            "business",
            "entertainment",
            "sports",
            "it",
            "science",
            "local"
        ]
        # カテゴリごとのページにアクセスするためのURL
        self.category_url = None
        # アクセスしたいURL
        self.url = url
        # Timeインスタンスの生成
        self.time = ScrapingTime()
        # 今日の日付
        self.today_str = self.time.get_today_yyyymmdd()
        # ChromeDriverのパスを指定してServiceオブジェクトを作成
        service = Service("driver/chromedriver.exe")
        # AddOptionsインスタンスの生成
        add_options = AddOptions()
        # オプション設定を格納
        options = add_options.set_browser_options()
        try:
            # Serviceオブジェクトを使用してWebDriverオブジェクトを作成
            self.driver = webdriver.Chrome(service=service, options=options)
        # driverがブラウザのバージョンに対応していないときの例外処理
        except SessionNotCreatedException as e:
            print("WebDriverのバージョンがブラウザのバージョンに対応していません。最新のWebDriverをダウンロードしてください。")
            print(e)
            # 例外を再度発生させ、プログラムを終了する
            raise

    def get_news_list(self) -> list:
        """
        ニュースリストを返す

        Returns:
            list: ニュースリスト
        """
        return self.news_list

    def add_news_list(self, category: str, title: str, url: str) -> None:
        """
        ニュースのリストに新しいニュースを追加する

        Args:
            category (str): ニュースのカテゴリー
            title (str): ニュースのタイトル
            url (str): ニュースのURL
        """
        self.news_list.append([category, title, url])

    def get_today_str(self) -> str:
        """
        今日の日付を表す文字列を取得する

        Returns:
            str: 今日の日付を表す文字列 (yyyymmdd)
        """
        return self.today_str

    def get_category_url(self) -> str:
        """
        カテゴリごとのページにアクセスするためのURLを表す文字列を取得する

        Returns:
             str: カテゴリごとのページにアクセスするためのURLを表す文字列
        """
        return self.category_url

    def set_category_url(self, name: str) -> None:
        """
        アクセスするURLを生成し、self.category_urlに格納する

        Args:
            name (str): カテゴリー名
        """
        self.category_url = self.get_url() + name + "?date=" + self.get_today_str()

    def get_url(self) -> str:
        """
        urlを取得する

        Returns:
             str: urlを表す文字列
        """
        return self.url

    def run(self) -> None:
        """ スクレイピングを開始する """
        for category_name in self.category:
            self.set_category_url(category_name)
            self.get_category_news(category_name)
        # 各種データ形式で保存
        self.create_csv()
        self.create_json()
        self.create_db()
        # WebDriverを終了する
        self.driver.quit()

    def create_csv(self) -> None:
        """ ニュース情報を元に、CSVファイルを作成する """
        # CsvWriterインスタンスの生成
        csv_writer = CsvWriter("csv/Yahoo_News_" + self.get_today_str())
        for news in self.get_news_list():
            csv_writer.add_data(news)
        csv_writer.write()

    def create_json(self) -> None:
        """ ニュース情報を元に、JSONファイルを作成する """
        # JsonWriterインスタンスの生成
        json_writer = JsonWriter('json/Yahoo_News_' + self.get_today_str())

        for news in self.get_news_list():
            # 記事情報の辞書型データを作成
            article_dict = {"title": news[1], "url": news[2]}
            # JsonWriterに記事情報を追加
            json_writer.add_dict(news[0], article_dict)

        # Jsonファイルの書き込み
        json_writer.write()

    def create_db(self) -> None:
        """ ニュース情報を元にDBファイルを作成する """
        # SQLiteDBインスタンスの生成
        db = SQLiteDB(f"db/Yahoo_News_{self.get_today_str()}.db")
        # テーブルの作成
        db.create_table("""
        CREATE TABLE IF NOT EXISTS news (
            category TEXT,
            title TEXT,
            url TEXT,
            UNIQUE(category, title, url)
        );
        """)
        # ニュース情報をテーブルに挿入
        for news in self.get_news_list():
            db.insert_data(
                f'INSERT INTO news( category, title, url ) VALUES ( ?, ?, ? )',
                (news[0], news[1], news[2])
            )
        # newsテーブルの情報をリストとして表示する
        print(db.fetch_data("SELECT * FROM news"))
        # データベースを閉じる
        db.close()

    def get_category_news(self, category_name: str) -> None:
        """
        Yahoo!ニュースの指定されたカテゴリーから記事を取得し、news_listに追加する

        Args:
            category_name (str): 取得するカテゴリー名
        """
        # Yahoo!ニュースのページにアクセス
        self.driver.get(self.get_category_url())

        # ニュース情報を持つ各divタグを取得する
        news_elements = self.driver.find_elements(By.CLASS_NAME, "newsFeed_item")

        # ニュースがなければ何もしない
        if not news_elements:
            return

        for news in news_elements:
            # 要素内の指定したクラスを持ったdivタグを取得する
            div_tag = None
            while div_tag is None:
                try:
                    div_tag = news.find_element(By.CLASS_NAME, "newsFeed_item_title")
                except NoSuchElementException:
                    pass

            # 要素内のaタグを取得する
            a_tag = None
            while a_tag is None:
                try:
                    a_tag = news.find_element(By.XPATH, ".//a")
                except NoSuchElementException:
                    pass

            # title(Key):記事タイトル(Value),url(Key):記事URL(Value)を
            # self.newsリストに挿入
            self.add_news_list(category_name, div_tag.text, a_tag.get_attribute('href'))


class AddOptions:
    def __init__(self):
        """　AddOptionsのコンストラクタ　"""
        # ChromeDriverに渡すオプションを作成
        self.options = Options()

    def set_browser_options(self) -> Options:
        """
        Seleniumのオプションを設定する

        Returns:
            Options: 設定されたオプション
        """
        self.options.add_argument("--headless")  # ヘッドレスモードを有効化
        self.options.add_argument("--disable-extensions")  # 拡張機能を無効化
        return self.options


if __name__ == '__main__':
    web_scraping = WebScraping("https://news.yahoo.co.jp/topics/")
    web_scraping.run()
