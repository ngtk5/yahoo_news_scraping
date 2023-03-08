import csv
import json
import sqlite3


class CsvWriter:
    def __init__(self, file_name: str):
        """
        CsvWriterのコンストラクタ

        Args:
            file_name: 出力するCSVファイルのファイル名
        """
        self.file_name = file_name + ".csv"
        self.data = [["category", "title", "url"]]

    def add_data(self, value: list) -> None:
        """
        self.dataにリスト型の値を挿入する

        Args:
            value: リスト型の値
        """
        self.data.append(value)

    def write(self) -> None:
        """ self.dataをcsvファイルに書き込む """
        with open(self.file_name, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(self.data)


class JsonWriter:
    def __init__(self, filename):
        """
        JsonWriterクラスのコンストラクタ。

        Args:
            filename: 作成するJSONファイルの名前。
        """
        self.filename = filename + ".json"
        self.data = {}

    def add_dict(self, key: str, value: dict) -> None:
        """
        self.dataに辞書型の値を挿入する
        指定されたキーが存在しない場合、リストを割り当ててキーを作成。

        Args:
            key: キー名
            value: 辞書型の値
        """
        if key not in self.data:
            self.data[key] = []
        self.data[key].append(value)

    def write(self) -> None:
        """ self.dataをJSONファイルに書き込む """
        with open(self.filename, 'w', encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)


class SQLiteDB:
    def __init__(self, dbname: str):
        """
        SQLiteDBクラスのコンストラクタ

        Args:
            dbname (str): データベースのファイル名
        """
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()

    def create_table(self, query: str) -> None:
        """
        テーブルを作成する

        Args:
            query (str): テーブルを作成するSQLクエリ
        """
        self.cursor.execute(query)
        self.conn.commit()

    def insert_data(self, query: str, data: tuple) -> None:
        """
        データを挿入する

        Args:
            query (str): データを挿入するSQLクエリ
            data (tuple): 挿入するデータのタプル
        """
        try:
            self.cursor.execute(query, data)
            self.conn.commit()
        # テーブル内に同じデータがあれば挿入せずに次の処理へ
        except sqlite3.IntegrityError:
            print("テーブル内に同じデータが存在します。")

    def fetch_data(self, query: str) -> list:
        """
        データを取得する

        Args:
            query (str): データを取得するSQLクエリ

        Returns:
            list: 取得したデータのリスト
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def close(self) -> None:
        """ データベースの接続を閉じる """
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    pass
