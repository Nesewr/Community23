# db.py
import sqlite3

def get_connection():
    """
    SQLite 연결을 반환합니다.
    """
    db_path = "my_database.db"

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # select 결과를 딕셔너리처럼 접근
    return conn
