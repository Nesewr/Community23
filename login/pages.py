# pages.py
import streamlit as st
from auth import login, logout, register_user, is_admin
from gallery import (
    get_gallery, get_galleries, create_gallery, delete_gallery,
    get_posts_by_gallery, create_post, get_post, delete_post,
    get_comments_by_post, create_comment, delete_comment,
    has_user_viewed_post, add_post_view, increment_views,
    has_user_liked_post, add_post_like, remove_post_like,
    increment_likes, decrement_likes
)

#############################
#  로그인 페이지
#############################
def show_login_page():
    st.title("로그인 페이지")
    with st.form("login_form"):
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인")
        if submitted:
            login(username, password)

    if st.button("회원가입"):
        st.session_state["page_mode"] = "register"
        st.rerun()

#############################
#  회원가입 페이지
#############################
def show_register_page():
    st.title("회원가입 페이지")

    with st.form("register_form"):
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        confirm = st.text_input("비밀번호 확인", type="password")
        submitted = st.form_submit_button("회원가입 진행")
        if submitted:
            if password != confirm:
                st.error("비밀번호가 일치하지 않습니다.")
                return
            success = register_user(username, password)
            if success:
                st.success("회원가입 완료! 로그인 페이지로 이동합니다.")
                st.session_state["page_mode"] = "login"
                st.rerun()
            else:
                st.error("이미 존재하는 아이디입니다.")

    if st.button("로그인 페이지로 이동"):
        st.session_state["page_mode"] = "login"
        st.rerun()

#############################
#  메인 페이지
#############################
def show_main_page():
    st.title("커뮤니티 메인 페이지")

    username = st.session_state.get("username", "")
    st.write(f"로그인 유저: {username}")

    col1, col2 = st.columns([2, 1])
    with col2:
        search_keyword = st.text_input("갤러리 검색", value="", help="갤러리 이름을 검색해보세요.")

    with col1:
        st.subheader("갤러리 목록")
        galleries = get_galleries()
        if search_keyword:
            galleries = [g for g in galleries if search_keyword.lower() in g["name"].lower()]

        if len(galleries) == 0:
            st.write("해당 검색어에 해당하는 갤러리가 없습니다.")
        else:
            for g in galleries:
                if st.button(f"{g['id']}. {g['name']}", key=f"gallery_btn_{g['id']}"):
                    st.session_state["page_mode"] = "gallery_view"
                    st.session_state["current_gallery_id"] = g["id"]
                    st.session_state["post_page"] = 0
                    st.rerun()
                st.write("---")

    # 관리자 전용: 새 갤러리 생성
    if is_admin():
        with st.expander("관리자 메뉴 - 새 갤러리 생성"):
            new_gallery_name = st.text_input("새 갤러리 이름")
            new_gallery_desc = st.text_area("새 갤러리 설명")
            if st.button("갤러리 생성"):
                create_gallery(new_gallery_name, new_gallery_desc)
                st.success("새 갤러리가 생성되었습니다.")
                st.rerun()
    else:
        st.write("관리자가 아니므로 갤러리 생성 권한이 없습니다.")

#############################
#  갤러리 페이지
#############################
def show_gallery_page():
    # CSS 오버라이드 적용
    st.markdown("""
    <style>
    /* 컬럼 컨테이너의 wrap 방지 및 가로 스크롤 허용 */
    .css-1l269bu > div {
        flex-wrap: nowrap !important;
        overflow-x: auto;
    }
    /* 컬럼 간 마진 조정 (원하는 대로 수정 가능) */
    .css-1l269bu .css-1kyxreq {
        margin-right: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    gallery_id = st.session_state.get("current_gallery_id", None)
    if not gallery_id:
        st.error("갤러리 ID가 없습니다.")
        st.session_state["page_mode"] = "main"
        st.rerun()
        return

    gallery = get_gallery(gallery_id)
    if not gallery:
        st.error("해당 갤러리가 존재하지 않습니다.")
        st.session_state["page_mode"] = "main"
        st.rerun()
        return

    st.title(gallery["name"])
    if gallery["description"]:
        st.write(gallery["description"])

    # 갤러리 삭제(관리자만)
    if is_admin():
        if st.button("이 갤러리 삭제 (관리자)"):
            delete_gallery(gallery_id)
            st.success("갤러리를 삭제했습니다.")
            st.session_state["page_mode"] = "main"
            st.rerun()

    if st.button("메인으로"):
        st.session_state["page_mode"] = "main"
        st.rerun()

    # 게시글 목록 (페이지네이션)
    posts = get_posts_by_gallery(gallery_id)
    if "post_page" not in st.session_state:
        st.session_state["post_page"] = 0

    page_size = 5
    start_idx = st.session_state["post_page"] * page_size
    end_idx = start_idx + page_size
    visible_posts = posts[start_idx:end_idx]

    st.subheader("게시글 목록")

    # 표 헤더 (번호, 말머리, 제목, 글쓴이, 작성일, 조회, 추천)
    header_cols = st.columns([1, 1, 3, 1, 2, 1, 1])
    with header_cols[0]:
        st.write("**번호**")
    with header_cols[1]:
        st.write("**말머리**")
    with header_cols[2]:
        st.write("**제목**")
    with header_cols[3]:
        st.write("**글쓴이**")
    with header_cols[4]:
        st.write("**작성일**")
    with header_cols[5]:
        st.write("**조회**")
    with header_cols[6]:
        st.write("**추천**")

    if visible_posts:
        for p in visible_posts:
            row_cols = st.columns([1, 1, 3, 1, 2, 1, 1])

            # (1) 번호
            with row_cols[0]:
                st.write(p["id"])

            # (2) 말머리
            with row_cols[1]:
                st.write(p["category"] if p["category"] else "-")

            # (3) 제목 (버튼으로 상세 페이지 이동)
            with row_cols[2]:
                if st.button(p["title"], key=f"title_btn_{p['id']}"):
                    st.session_state["page_mode"] = "post_detail"
                    st.session_state["current_post_id"] = p["id"]
                    st.rerun()

            # (4) 글쓴이
            with row_cols[3]:
                st.write(p["author"])

            # (5) 작성일
            with row_cols[4]:
                st.write(str(p["created_at"]))

            # (6) 조회
            with row_cols[5]:
                st.write(p["views"])

            # (7) 추천
            with row_cols[6]:
                st.write(p["likes"])
    else:
        st.write("아직 게시글이 없습니다.")

    # 페이지네이션
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.session_state["post_page"] > 0:
            if st.button("이전 페이지"):
                st.session_state["post_page"] -= 1
                st.rerun()
    with col3:
        if end_idx < len(posts):
            if st.button("다음 페이지"):
                st.session_state["post_page"] += 1
                st.rerun()

    # 새 글 작성
    st.subheader("새 글 작성")
    with st.form("new_post_form"):
        new_title = st.text_input("제목", key="new_post_title")
        category_options = ["자유", "공지", "질문", "정보", "기타"]
        new_category = st.selectbox("말머리", category_options)
        new_content = st.text_area("내용", key="new_post_content")
        submitted = st.form_submit_button("글 등록")
        if submitted:
            author = st.session_state.get("username", "비회원")
            create_post(gallery_id, new_title, new_content, author, new_category)
            st.success("게시글이 등록되었습니다.")
            st.rerun()

#############################
#  게시글 상세 페이지
#############################
def show_post_detail_page():
    # CSS 오버라이드 적용
    st.markdown("""
    <style>
    /* 컬럼 wrap 방지 및 가로 스크롤 허용 */
    .css-1l269bu > div {
        flex-wrap: nowrap !important;
        overflow-x: auto;
    }
    .css-1l269bu .css-1kyxreq {
        margin-right: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    post_id = st.session_state.get("current_post_id", None)
    if not post_id:
        st.error("게시글 ID가 없습니다.")
        st.session_state["page_mode"] = "main"
        st.rerun()
        return

    post = get_post(post_id)
    if not post:
        st.error("존재하지 않는 게시글입니다.")
        st.session_state["page_mode"] = "main"
        st.rerun()
        return

    # 조회수: 사용자당 1회
    username = st.session_state.get("username", "")
    logged_in = st.session_state.get("logged_in", False)
    if logged_in:
        if not has_user_viewed_post(username, post_id):
            increment_views(post_id)
            add_post_view(username, post_id)
            post = get_post(post_id)  # 업데이트된 조회수 반영

    # 상세 페이지 표시
    st.title(f"[{post['category']}] {post['title']}")
    st.write(f"작성자: {post['author']}")
    st.write(f"작성일: {post['created_at']}")
    st.write(f"조회수: {post['views']}")
    st.write(f"추천수: {post['likes']}")
    st.write("---")
    st.write(post["content"])

    # 권한
    is_author = (username == post["author"])
    is_admin_ = is_admin()

    # 좋아요(토글)
    if logged_in:
        user_liked = has_user_liked_post(username, post_id)
        like_label = "좋아요 취소" if user_liked else "좋아요"
        if st.button(like_label):
            if user_liked:
                remove_post_like(username, post_id)
                decrement_likes(post_id)
                st.success("좋아요를 취소했습니다.")
            else:
                add_post_like(username, post_id)
                increment_likes(post_id)
                st.success("좋아요를 눌렀습니다.")
            st.rerun()
    else:
        st.write("로그인 후 좋아요를 누를 수 있습니다.")

    # 게시글 삭제
    if is_admin_ or is_author:
        if st.button("게시글 삭제"):
            delete_post(post_id)
            st.success("게시글을 삭제했습니다.")
            st.session_state["page_mode"] = "gallery_view"
            st.rerun()

    if st.button("갤러리로 돌아가기"):
        st.session_state["page_mode"] = "gallery_view"
        st.rerun()

    # 댓글 목록
    st.subheader("댓글")
    comments = get_comments_by_post(post_id)
    if comments:
        for c in comments:
            st.markdown(f"""
            <div style="border:1px solid #ccc; padding:10px; border-radius:5px; margin-bottom:10px;">
                <strong>{c['author']}</strong> | {c['created_at']}<br/>
                {c["content"]}
            </div>
            """, unsafe_allow_html=True)

            comment_is_author = (username == c["author"])
            if is_admin_ or comment_is_author:
                if st.button(f"댓글 삭제 (ID:{c['id']})", key=f"del_comment_{c['id']}"):
                    delete_comment(c["id"])
                    st.success("댓글을 삭제했습니다.")
                    st.rerun()
    else:
        st.write("댓글이 없습니다.")

    # 댓글 작성
    st.subheader("댓글 작성")
    with st.form("comment_form"):
        comment_content = st.text_area("댓글 내용")
        submitted = st.form_submit_button("댓글 등록")
        if submitted:
            author = username if username else "비회원"
            create_comment(post_id, author, comment_content)
            st.success("댓글이 등록되었습니다.")
            st.rerun()
