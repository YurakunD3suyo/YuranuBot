import sqlite3
import logging
import sys

###データベース関連の処理###

##設定リストの管理
server_settings = [
    ("server_id", "INTEGER"),
    ("welcome_server", "INTEGER NOT NULL DEFAULT 0"),
    ("speak_channel", "INTEGER"),
    ("auto_connect", "INTEGER DEFAULT 0"),
    ("speak_speed", "REAL DEFAULT 1"),
    ("length_limit", "INTEGER DEFAULT 50"),
    ("vc_join_message", "TEXT DEFAULT がさんかしました！"),
    ("vc_exit_message", "TEXT DEFAULT がたいせきしました！"),
    ("vc_speaker", "INTEGER NOT NULL DEFAULT 3"),
    ("vc_user_announce", "INTEGER NOT NULL DEFAULT 1"),
    ("soundtext_mode", "INTEGER NOT NULL DEFAULT 2"),
    ("discord_url_load", "INTEGER NOT NULL DEFAULT 0")
]

user_settings = [
    ("user_id", "INTEGER"),
    ("vc_speaker", "INTEGER NOT NULL DEFAULT -1"),
    ("conn_msg", "TEXT NOT NULL DEFAULT nan"),
    ("disconn_msg", "TEXT NOT NULL DEFAULT nan"),
    ("speak_speed", "REAL NOT NULL DEFAULT 0")
]


# グローバル変数としてcursorとconnを定義
cursor: sqlite3.Cursor
conn: sqlite3.Connection

##データベースに接続
def db_load(file):
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

def db_init():
    """
    データベースを準備します(更新も含む)

    Returns:
        true: 正常  false:異常
    """
    try:
        ##初期処理しちゃいますね(テーブルがないときに作成する)
        cursor.execute('CREATE TABLE IF NOT EXISTS "server_settings" (server_id INTEGER)')
        cursor.execute('CREATE TABLE IF NOT EXISTS "user_settings" (user_id INTEGER)')

        ##追加した名前のオブジェクトがなかった場合に新しく作成(server_settings)
        ##server_settingの状態を取得
        cursor.execute("PRAGMA table_info(server_settings)")

        ##不足している設定の追加
        columns = [column[1] for column in cursor.fetchall()]
        for name, type in server_settings:
            if name not in columns:
                cursor.execute(f'ALTER TABLE server_settings ADD COLUMN {name} {type}')
    

        ##追加した名前のオブジェクトがなかった場合に新しく作成(user_settings)
        ##user_settingの状態を取得
        cursor.execute("PRAGMA table_info(user_settings)")

        ##不足している設定の追加
        columns = [column[1] for column in cursor.fetchall()]
        for name, type in user_settings:
            if name not in columns:
                cursor.execute(f'ALTER TABLE user_settings ADD COLUMN {name} {type}')
    
        conn.commit()
        return True
    
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_no = exception_traceback.tb_lineno
        logging.error(f"database -> ({line_no}行目) {e}")
        return False

##データベースから設定を読み出し、返すやつ
def get_server_setting(id, type):
    """
    データベースのサーバー設定を取得します

    Args:
        cursor: SQLite3で取得したカーソル
        server_id: discordのサーバーID
        type: 設定内容

    Returns:
        Result or None
    """

    list_type = "server_settings"
    id_type = "server_id"

    cursor.execute(f'SELECT {type} FROM {list_type} WHERE {id_type} = {id}')
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute(f'INSERT INTO {list_type} ({id_type}) VALUES (?)', (id,))

        cursor.execute(f'SELECT {type} FROM {list_type} WHERE {id_type} = {id}')
        result = cursor.fetchone()

        return result[0]

        
# サーバー設定をすべて取得し返す
def get_server_all_setting(id):
    """
    データベースのサーバー設定を取得します

    Args:
        cursor: SQLite3で取得したカーソル
        server_id: discordのサーバーID

    Returns:
        Result or None
    """

    list_type = "server_settings"
    id_type = "server_id"

    cursor.execute(f'SELECT * FROM {list_type} WHERE {id_type} = {id}')
    result = cursor.fetchone()
    if result:
        return result
    else:
        cursor.execute(f'INSERT INTO {list_type} ({id_type}) VALUES (?)', (id,))
        
        cursor.execute(f'SELECT * FROM {list_type} WHERE {id_type} = {id}')
        result = cursor.fetchone()

        return result



##設定を上書きするやつ
def save_server_setting(id, type, new_value):
    """
    データベースのサーバー設定を更新します

    Args:
        server_id: discordのユーザーID
        type: 設定内容
        new_value: 変更する設定の値

    Returns:
        正常に完了: None, 異常: Exception
    """
    list_type = "server_settings"
    id_type = "server_id"

    try:
        result = cursor.execute(f'SELECT "{type}" FROM {list_type} WHERE {id_type} = {id}').fetchone()
        if result is None:
            if type in server_settings:
                cursor.execute(f'INSERT INTO {list_type} ({id_type}, "{type}") VALUES ({id}, {new_value})')
                conn.commit()
                
                logging.info(f"{list_type} '{id}' was created ({type}: {new_value})")
                return
            else:
                return 1
    
        cursor.execute(f'UPDATE {list_type} SET "{type}" = "{new_value}" WHERE {id_type} = {id}')
        conn.commit()

        logging.info(f"{list_type} '{id}' was updated ({type}: {new_value})")
        return
    
    
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_no = exception_traceback.tb_lineno
        logging.error(f"database -> ({line_no}行目) {e}")

##データベースから設定を読み出し、返すやつ
def get_user_setting(id, type):
    """
    データベースのサーバー設定を取得します

    Args:
        cursor: SQLite3で取得したカーソル
        server_id: discordのユーザーID
        type: 設定内容

    Returns:
        Result or None
    """
    try:
        list_type = "user_settings"
        id_type = "user_id"

        cursor.execute(f'SELECT {type} FROM {list_type} WHERE {id_type} = {id}')
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            cursor.execute(f'INSERT INTO {list_type} ({id_type}) VALUES (?)', (id,))
            conn.commit()

            cursor.execute(f'SELECT {type} FROM {list_type} WHERE {id_type} = {id}')

            result = cursor.fetchone()
            return result[0]
        
    except Exception as e:
        logging.error(f"database -> {e}")
    
##データベースから設定を読み出し、返すやつ
def get_user_all_settings(id):
    """
    データベースのサーバー設定を取得します

    Args:
        cursor: SQLite3で取得したカーソル
        server_id: discordのユーザーID
        type: 設定内容

    Returns:
        Result or None
    """
    try:
        list_type = "user_settings"
        id_type = "user_id"

        cursor.execute(f'SELECT * FROM {list_type} WHERE {id_type} = {id}')
        result = cursor.fetchone()
        if result:
            return result
        else:
            cursor.execute(f'INSERT INTO {list_type} ({id_type}) VALUES (?)', (id,))
            conn.commit()

            cursor.execute(f'SELECT * FROM {list_type} WHERE {id_type} = {id}')

            result = cursor.fetchone()
            return result
        
    except Exception as e:
        logging.error(f"database -> {e}")
    
##設定を上書きするやつ
def save_user_setting(id, type, new_value):
    """
    データベースのサーバー設定を更新します

    Args:
        server_id: discordのユーザーID
        type: 設定内容
        new_value: 変更する設定の値

    Returns:
        正常に完了: None, 異常: エラー
    """
    list_type = "user_settings"
    id_type = "user_id"

    try:
        result = cursor.execute(f'SELECT "{type}" FROM {list_type} WHERE {id_type} = {id}').fetchone()
        if result is None:
            if type in server_settings:
                cursor.execute(f'INSERT INTO {list_type} ({id_type}, "{type}") VALUES ({id}, {new_value})')
                conn.commit()
                
                logging.debug(f"{list_type} '{id}' was created ({type}: {new_value})")
                return
            else:
                return 1
    
        cursor.execute(f'UPDATE {list_type} SET "{type}" = "{new_value}" WHERE {id_type} = {id}')
        conn.commit()

        logging.debug(f"{list_type} '{id}' was updated ({type}: {new_value})")
        return
    
    
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_no = exception_traceback.tb_lineno
        logging.error(f"database -> ({line_no}行目) {e}")
