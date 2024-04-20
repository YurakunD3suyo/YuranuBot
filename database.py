import sqlite3
import logging
###データベース関連の処理###

##設定リストの管理
settings_list = [
    ("server_id", "INTEGER"),
    ("speak_channel", "INTEGER"),
    ("auto_connect", "INTEGER"),
    ("speak_speed", "REAL"),
    ("file_limit" , "INTEGER DEFAULT '3'"),
    ("length_limit", "INTEGER"),
    ("vc_join_message", "TEXT DEFAULT 'がさんかしたのだ！'"),
    ("vc_exit_message", "TEXT DEFAULT 'がたいせきしたのだ！'"),
    ("vc_connect_message", "TEXT DEFAULT 'せつぞくしたのだ！'")
]

##データベースに接続
def db_load(file):
    """
    データベースのカーソルを取得します

    Args:
        file: ファイル名

    Returns:
        List[cursor, conn]
    """
    conn = sqlite3.connect(file)
    cursor = conn.cursor()

    ##ついでに初期処理もしちゃいますねー
    cursor.execute('CREATE TABLE IF NOT EXISTS "server_settings" (server_id INTEGER)')

    ##カラムも追加しますねー
    cursor.execute("PRAGMA table_info(server_settings)")
    columns = [column[1] for column in cursor.fetchall()]

    for name, type in settings_list:
        if name not in columns:
            cursor.execute(f'ALTER TABLE server_settings ADD COLUMN {name} {type}')

    conn.commit()

    result = [cursor, conn]
    return result

##データベースから設定を読み出し、返すやつ
def get_db_setting(cursor, server_id, type):
    """
    データベースの設定を取得します

    Args:
        cursor: SQLite3で取得したカーソル
        server_id: discordのサーバーID
        type: 設定内容

    Returns:
        Result or None
    """
    cursor.execute(f'SELECT {type} FROM server_settings WHERE server_id = {server_id}')
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None
    
##設定を上書きするやつ
def set_db_setting(cursor, conn, server_id, type, new_value):
    """
    データベースの設定を更新します

    Args:
        cursor: SQLite3で取得したカーソル
        conn: SQLite3で接続した際の接続されたやつ
        server_id: discordのサーバーID
        type: 設定内容
        new_value: 変更する設定の値

    Returns:
        正常に完了: None, 異常: Exception
    """
    try:
        result = cursor.execute(f'SELECT "{type}" FROM server_settings WHERE server_id = {server_id}').fetchone()
        if result is None:
            cursor.execute(f'INSERT INTO server_settings (server_id, "{type}") VALUES ({server_id}, {new_value})')
            return
    
        cursor.execute(f'UPDATE server_settings SET "{type}" = "{new_value}" WHERE server_id = {server_id}')
        conn.commit()
        logging.debug(f"Setting '{server_id}' was updated ({type}: {new_value})")
    except Exception as e:
        return e
