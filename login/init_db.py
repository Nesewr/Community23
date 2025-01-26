# init_db.py
import sqlite3

def init_db(db_path="my_database.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1) users 테이블 (회원가입/로그인)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );
    """)

    # 2) galleries 테이블
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS galleries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT
    );
    """)

    # 3) posts 테이블 (조회수, 좋아요 수)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gallery_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        author TEXT NOT NULL,
        created_at DATETIME,
        category TEXT,
        views INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        FOREIGN KEY (gallery_id) REFERENCES galleries(id)
    );
    """)

    # 4) comments 테이블
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        author TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at DATETIME,
        FOREIGN KEY (post_id) REFERENCES posts(id)
    );
    """)

    # 5) post_views 테이블 (조회수: 사용자 1회 제한)
    #    (post_id, username) 중복삽입을 막기 위해 UNIQUE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS post_views (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        created_at DATETIME,
        UNIQUE(post_id, username),
        FOREIGN KEY (post_id) REFERENCES posts(id)
    );
    """)

    # 6) post_likes 테이블 (좋아요: 사용자 1회 제한 + 토글)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS post_likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        created_at DATETIME,
        UNIQUE(post_id, username),
        FOREIGN KEY (post_id) REFERENCES posts(id)
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    init_db("my_database.db")
    print("DB 테이블 초기화 완료")
