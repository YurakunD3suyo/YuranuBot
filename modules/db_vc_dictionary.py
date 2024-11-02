import sqlite3
import logging
###データベース関連の処理###

# グローバル変数としてcursorとconnを定義
cursor: sqlite3.Cursor
conn: sqlite3.Connection

def dictionary_load(file):
    """
    サーバー辞書に接続します

    Args:
        file: ファイル名

    Returns:
        true: 正常  false:異常
    """
    try:
        global cursor, conn

        conn = sqlite3.connect(file, isolation_level=None)
        cursor = conn.cursor()

        return True
    except:
        return False

def get_dictionary(server_id):
    """
    サーバー辞書を取得します

    Args:
        server_id: discordのサーバーID

    Returns:
        Result(List) or None
    """
    cursor.execute(f'CREATE TABLE IF NOT EXISTS "{server_id}" (text TEXT NOT NULL UNIQUE, reading TEXT NOT NULL, user INTEGER)')

    cursor.execute(f'SELECT * FROM "{server_id}"')
    result = cursor.fetchall()

    if result:
        return result
    else:
        return None
    
##設定を上書きするやつ
def save_dictionary(server_id: int, text, reading, user: int):
    """
    サーバー辞書を更新します

    Args:
        server_id: discordのサーバーID
        text: 読み上げ対象の内容
        reading: 読み上げ対象の仮名 
        user: 作ったユーザー

    Returns:
        正常に完了: None, 異常: Exception
    """
    try:
        cursor.execute(f'CREATE TABLE IF NOT EXISTS "{server_id}" (text TEXT NOT NULL UNIQUE, reading TEXT NOT NULL, user INTEGER)')
        cursor.execute(f'INSERT OR REPLACE INTO "{server_id}" (text, reading, user) VALUES(?, ?, ?)', (text, reading, user))
        conn.commit()

        logging.debug(f"Server '{server_id}' Dictionary was updated ({text}: {reading})")
        return
    
    except Exception as e:
        return e

def delete_dictionary(server_id: int, text):
    """
    サーバー辞書を更新します

    Args:
        server_id: discordのサーバーID
        text: 削除する読み上げ対象の単語

    Returns:
        正常に完了: None, 異常: Exception
    """
    try:
        cursor.execute(f'CREATE TABLE IF NOT EXISTS "{server_id}" (text TEXT NOT NULL UNIQUE, reading TEXT NOT NULL, user INTEGER)')
        cursor.execute(f'DELETE FROM "{server_id}" WHERE text = ?', (text,))
        conn.commit()

        logging.debug(f"Server '{server_id}' Dictionary was updated (deleted: {text})")
        return
    
    except Exception as e:
        return e

