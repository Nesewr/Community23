# auth.py
import streamlit as st
from db import get_connection

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def user_exists(username: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return (row[0] > 0) if row else False

def register_user(username: str, password: str) -> bool:
    # 이미 사용자 존재 여부 확인
    if user_exists(username):
        return False
    
    conn = get_connection()
    cursor = conn.cursor()
    query = "INSERT INTO users (username, password) VALUES (?, ?)"
    cursor.execute(query, (username, password))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def check_credentials(username, password):
    # 1) 하드코딩 Admin 계정 먼저 확인
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return "admin"

    # 2) DB에서 user 검색
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return None

    if user["password"] == password:
        return "user"
    return None

def login(username, password):
    role = check_credentials(username, password)
    if role is not None:
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["role"] = role  # "admin" or "user"
        st.success("로그인 성공!")
        st.rerun()
    else:
        st.error("아이디 혹은 비밀번호가 잘못되었습니다.")

def logout():
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = ""
    st.info("로그아웃되었습니다.")
    st.rerun()

def is_admin() -> bool:
    """세션에 저장된 role이 'admin'인지 확인"""
    return (st.session_state.get("role") == "admin")
