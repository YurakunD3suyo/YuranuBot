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
    ("sound_file", "TEXT"),
]

# グローバル変数としてcursorとconnを定義
cursor: sqlite3.Cursor
conn: sqlite3.Connection

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

# サウンドテキストを取得
def get_soundtext_list(id: int):
    cursor.execute(f'CREATE TABLE IF NOT EXIST "{id}"')

    ##不足している設定の追加
    cursor.execute(f"PRAGMA table_info({id})")
    columns = [column[1] for column in cursor.fetchall()]
    for name, type in soundtext_setting:
        if name not in columns:
            cursor.execute(f'ALTER TABLE "{id}" ADD COLUMN {name} {type}')
    
        cursor.execute(f'SELECT * FROM {id}')
        result = cursor.fetchone()

        return result

def _create_table(id):


