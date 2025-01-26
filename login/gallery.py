# gallery.py
from datetime import datetime
from db import get_connection

#############################
#  갤러리 관련
#############################
def get_gallery(gallery_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM galleries WHERE id = ?", (gallery_id,))
    gallery = cursor.fetchone()
    cursor.close()
    conn.close()
    return gallery

def get_galleries():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM galleries")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def create_gallery(name, description):
    conn = get_connection()
    cursor = conn.cursor()
    query = "INSERT INTO galleries (name, description) VALUES (?, ?)"
    cursor.execute(query, (name, description))
    conn.commit()
    cursor.close()
    conn.close()

def delete_gallery(gallery_id: int):
    """
    갤러리를 삭제할 때, 해당 갤러리에 포함된 posts, comments를 먼저 삭제
    """
    conn = get_connection()
    cur = conn.cursor()
    # 1) comments
    cur.execute("""
        DELETE FROM comments 
        WHERE post_id IN (SELECT id FROM posts WHERE gallery_id=?)
    """, (gallery_id,))
    # 2) post_likes, post_views도 삭제 (해당 갤러리의 posts)
    cur.execute("""
        DELETE FROM post_likes 
        WHERE post_id IN (SELECT id FROM posts WHERE gallery_id=?)
    """, (gallery_id,))
    cur.execute("""
        DELETE FROM post_views 
        WHERE post_id IN (SELECT id FROM posts WHERE gallery_id=?)
    """, (gallery_id,))
    # 3) posts
    cur.execute("DELETE FROM posts WHERE gallery_id=?", (gallery_id,))
    # 4) gallery
    cur.execute("DELETE FROM galleries WHERE id=?", (gallery_id,))
    conn.commit()
    cur.close()
    conn.close()

#############################
#  post_views (조회수) 관련
#############################
def has_user_viewed_post(username: str, post_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM post_views WHERE post_id=? AND username=?", (post_id, username))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row["cnt"] > 0

def add_post_view(username: str, post_id: int):
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.now()
    cur.execute("""
        INSERT OR IGNORE INTO post_views (post_id, username, created_at)
        VALUES (?, ?, ?)
    """, (post_id, username, now))
    conn.commit()
    cur.close()
    conn.close()

def increment_views(post_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE posts SET views = views + 1 WHERE id=?", (post_id,))
    conn.commit()
    cur.close()
    conn.close()

#############################
#  post_likes (좋아요) 관련
#############################
def has_user_liked_post(username: str, post_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM post_likes WHERE post_id=? AND username=?", (post_id, username))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row["cnt"] > 0

def add_post_like(username: str, post_id: int):
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.now()
    cur.execute("""
        INSERT OR IGNORE INTO post_likes (post_id, username, created_at)
        VALUES (?, ?, ?)
    """, (post_id, username, now))
    conn.commit()
    cur.close()
    conn.close()

def remove_post_like(username: str, post_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM post_likes WHERE post_id=? AND username=?", (post_id, username))
    conn.commit()
    cur.close()
    conn.close()

def increment_likes(post_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE posts SET likes = likes + 1 WHERE id=?", (post_id,))
    conn.commit()
    cur.close()
    conn.close()

def decrement_likes(post_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE posts SET likes = likes - 1 WHERE id=?", (post_id,))
    conn.commit()
    cur.close()
    conn.close()

#############################
#  게시글 관련
#############################
def get_posts_by_gallery(gallery_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM posts WHERE gallery_id = ? ORDER BY id DESC"
    cursor.execute(query, (gallery_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def create_post(gallery_id: int, title: str, content: str, author: str, category: str):
    """
    category(말머리), views=0, likes=0로 초기화
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO posts (gallery_id, title, content, author, created_at, category, views, likes)
        VALUES (?, ?, ?, ?, ?, ?, 0, 0)
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(query, (gallery_id, title, content, author, now, category))
    conn.commit()
    cursor.close()
    conn.close()

def get_post(post_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM posts WHERE id = ?"
    cursor.execute(query, (post_id,))
    post = cursor.fetchone()
    cursor.close()
    conn.close()
    return post

def delete_post(post_id: int):
    """
    해당 post와 그 댓글, post_likes, post_views를 모두 삭제
    """
    conn = get_connection()
    cur = conn.cursor()
    # 댓글 삭제
    cur.execute("DELETE FROM comments WHERE post_id=?", (post_id,))
    # 좋아요 / 조회수 기록 삭제
    cur.execute("DELETE FROM post_likes WHERE post_id=?", (post_id,))
    cur.execute("DELETE FROM post_views WHERE post_id=?", (post_id,))
    # 게시글 삭제
    cur.execute("DELETE FROM posts WHERE id=?", (post_id,))
    conn.commit()
    cur.close()
    conn.close()

#############################
#  댓글 관련
#############################
def get_comments_by_post(post_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM comments WHERE post_id = ? ORDER BY id ASC"
    cursor.execute(query, (post_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def create_comment(post_id: int, author: str, content: str):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO comments (post_id, author, content, created_at)
        VALUES (?, ?, ?, ?)
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(query, (post_id, author, content, now))
    conn.commit()
    cursor.close()
    conn.close()

def delete_comment(comment_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM comments WHERE id=?", (comment_id,))
    conn.commit()
    cur.close()
    conn.close()
