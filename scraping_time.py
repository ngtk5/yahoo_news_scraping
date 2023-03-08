import datetime


class ScrapingTime:
    def __init__(self):
        """　Timeのコンストラクタ　"""
        self.today = datetime.date.today()

    def get_today_yyyymmdd(self) -> str:
        """
        今日の日付をyyyymmdd形式で取得する

        Returns:
            str: 今日の日付を表す文字列 (yyyymmdd)
        """
        return self.today.strftime('%Y%m%d')


if __name__ == '__main__':
    pass
