##############################
# This is かんがえちう...
# どうやってやろう
##############################


import sqlite3
import logging
import sys

###データベース関連の処理###
soundtext_setting = [
    ("word", "TEXT NOT NULL"),
    ("dir", "TEXT"),
]

primary_key = "PRIMARY KEY (word)"

# グローバル変数としてcursorとconnを定義
cursor: sqlite3.Cursor
conn: sqlite3.Connection

#上書きエラーを返却
class OverwriteError(Exception):
    """上書きしようとした際に発生するエラー"""
    pass

def soundtext_load(file):
    """
    データベースに接続します

    Args:
        file: ファイル名

    Returns:
        true: 正常  false:異常
    """
    try:
        global cursor, conn

        conn = sqlite3.connect(file)
        cursor = conn.cursor()
        
        conn.autocommit = True

        return True
    
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_no = exception_traceback.tb_lineno
        logging.error(f"database -> ({line_no}行目) {e}")
        return False

def save_soundtext(id: int, word: str, dir: str):
    """
    サウンドテキストの保存
    
    Args:
        id: サーバーID
        word: 単語
        dir: 音声ファイルのディレクトリ

    Return:
        None: 正常, OverwriteError: 重複エラー
    """

    try:
        _create_table(id)

        cursor.execute(f"SELECT * FROM '{id}' WHERE 'word' = '{word}'")
        result = cursor.fetchmany()

        print(result)

        if result != []:
            raise OverwriteError("同じ単語を検出しました！")
        
        cursor.execute(f"INSERT INTO '{id}' (word, dir) VALUES ('{word}', '{dir}')")
        return None
    except sqlite3.IntegrityError as e:
        return e

def delete_soundtext(id: int, word: str):
    _create_table(id)

    cursor.execute(f"DELETE FROM '{id}' WHERE word = '{word}'")

# サウンドテキストを取得
def get_soundtext_list(id: int):
    _create_table(id)

    cursor.execute(f"SELECT * FROM '{id}'")
    result = cursor.fetchall()

    return result

def find_soundtext(id: int, word: str):
    _create_table(id)

    cursor.execute(f"SELECT * FROM '{id}' WHERE word = '{word}'")
    result = cursor.fetchone()

    return result

def _create_table(id):
    columns = ', '.join([f"{column_name} {data_type}" for column_name, data_type in soundtext_setting])
    create_table_query = f"CREATE TABLE IF NOT EXISTS '{id}' ({columns}, {primary_key});"
    
    # テーブルを作成
    cursor.execute(create_table_query)

    ##不足している設定の追加
    cursor.execute(f"PRAGMA table_info({id})")
    columns = [column[1] for column in cursor.fetchall()]
    for name, type in soundtext_setting:
        if name not in columns:
            cursor.execute(f"ALTER TABLE '{id}' ADD COLUMN '{name}' '{type}'")

