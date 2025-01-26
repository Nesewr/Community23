# app.py
import streamlit as st
from init_db import init_db
from db import get_connection
from pages import (
    show_login_page,
    show_register_page,
    show_main_page,
    show_gallery_page,
    show_post_detail_page
)

def main():
    # DB 초기화 (테이블 없으면 생성)
    init_db()

    st.set_page_config(
        page_title="My Community",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 세션 초기화
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = ""
    if "page_mode" not in st.session_state:
        st.session_state["page_mode"] = "login"
    if "client_ip" not in st.session_state:
        # IP기반 관리자 여부 판단 -> 여기서는 127.0.0.1만 admin
        st.session_state["client_ip"] = "127.0.0.1"

    # 사이드바
    render_sidebar()

    page_mode = st.session_state["page_mode"]

    # 페이지 라우팅
    if not st.session_state["logged_in"]:
        if page_mode == "login":
            show_login_page()
        elif page_mode == "register":
            show_register_page()
        else:
            st.session_state["page_mode"] = "login"
            st.rerun()
    else:
        # 로그인 상태
        if page_mode == "main":
            show_main_page()
        elif page_mode == "gallery_view":
            show_gallery_page()
        elif page_mode == "post_detail":
            show_post_detail_page()
        else:
            st.session_state["page_mode"] = "main"
            st.rerun()

def render_sidebar():
    with st.sidebar:
        st.header("사이드바 메뉴")

        if st.session_state["logged_in"]:
            st.write(f"**{st.session_state['username']}** 님 안녕하세요!")
            # 메인 페이지 이동
            if st.button("메인 페이지로 이동"):
                st.session_state["page_mode"] = "main"
                st.rerun()

            # 로그아웃
            if st.button("로그아웃"):
                from auth import logout
                logout()
        else:
            # 비로그인 상태
            # 이미 page_mode가 'login' or 'register'면 radio로 덮어쓰지 않음
            if st.session_state["page_mode"] in ["login", "register"]:
                if st.session_state["page_mode"] == "login":
                    st.write("현재: 로그인 모드")
                else:
                    st.write("현재: 회원가입 모드")
            else:
                # page_mode가 다른 값일 때만 radio 표시
                user_action = st.radio("계정 작업", ["로그인", "회원가입"])
                if user_action == "로그인":
                    st.session_state["page_mode"] = "login"
                else:
                    st.session_state["page_mode"] = "register"

if __name__ == "__main__":
    main()
