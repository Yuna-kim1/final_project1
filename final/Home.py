import streamlit as st
import importlib.util
import os

# 페이지 상단에 넣어주세요
st.markdown("""
    <style>
    /* 본문 버튼 (사이드바 제외) 스타일 고정 */
    div.stButton > button[kind="secondary"]:not([data-testid="baseButton-secondarySidebar"]) {
        background-color: black !important;
        color: white !important;
        border: 1px solid white !important;
        border-radius: 8px !important;
    }
    div.stButton > button[kind="secondary"]:hover:not([data-testid="baseButton-secondarySidebar"]) {
        background-color: #222 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# 사용자 정보 세팅
USER_CREDENTIALS = {
    "유나천재": "1234",
    "취업시켜조": "abcd"
}

# 세션 초기화
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "page" not in st.session_state:
    st.session_state.page = "Home"

# ✅ 로그인 화면
if not st.session_state.authenticated:
    # --- 다크모드 스타일 추가 ---
    st.markdown("""
        <style>
            .stApp {
                background-color: #121212;
                color: #FFFFFF;
            }
            .stTextInput > div > div > input {
                background-color: #1e1e1e !important;
                color: #FFFFFF !important;
            }
            .stTextInput label, .stPasswordInput label {
                color: #CCCCCC;
            }
            .stButton > button {
                background-color: #333333;
                color: white;
                border-radius: 6px;
            }
            .stButton > button:hover {
                background-color: #555555;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("🔐 로그인")

    # --- 텍스트 메시지 ---
    st.markdown("<strong>양산산화 도금공정</strong> 대시보드입니다.", unsafe_allow_html=True)

    st.markdown("""
        <div style='margin-top: 10px; margin-bottom: 20px; padding: 10px; background-color: #2a2a2a; color: #ddd; border-left: 6px solid #4a90e2; border-radius: 6px;'>
            로그인 후 상세 기능을 확인하실 수 있습니다.
        </div>
    """, unsafe_allow_html=True)

    # --- 로그인 입력창 ---
    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

# ✅ 로그인 성공 시 대시보드 메인 진입
else:
    # --- 🔧 사이드바 커스터마이징 ---
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                background-color: #1c1c1c;
            }
            [data-testid="stSidebar"]::before {
                content: "DASHBOARD";
                display: block;
                text-align: center;
                font-size: 40px;
                font-weight: bold;
                color: white;
                margin: 30px 0 20px 0;
            }
            div.stButton > button:first-child {
                background-color: transparent;
                color: white;
                border: none;
                padding: 10px 16px;
                font-size: 18px;
                width: 100%;
                text-align: left;
                border-radius: 8px;
            }
            div.stButton > button:first-child:hover {
                background-color: #333333;
            }
            div.stButton > button.custom-selected {
                background-color: #444444;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- ✅ 메뉴 구성 ---
    menu_items = {
        "Home": "🏠Home",
        "name2": "데이터 확인",
        "name3": "도금 두께 예측",
        "name4": "실시간 관리도"
    }

    for key, label in menu_items.items():
        button_clicked = st.sidebar.button(label, key=key)
        if button_clicked:
            st.session_state.page = key

    st.sidebar.markdown(f"""
        <script>
            const buttons = window.parent.document.querySelectorAll('div[data-testid="stSidebar"] button');
            buttons.forEach((btn) => {{
                if (btn.innerText.includes("{menu_items[st.session_state.page]}")) {{
                    btn.classList.add('custom-selected');
                }} else {{
                    btn.classList.remove('custom-selected');
                }}
            }});
        </script>
    """, unsafe_allow_html=True)

    # --- ✅ 페이지 로드 ---
    page = st.session_state.page

    if page == "Home":
        st.markdown("""
            <div style='
                background-color: #1c1c1c;
                padding: 16px 24px;
                border-radius: 12px;
                margin: 20px auto;
                text-align: center;
            '>
                <h2 style='color: white; margin: 0;'>도금 공정 대시보드 메인</h2>
            </div>
        """, unsafe_allow_html=True)

        st.subheader("대시보드 설명")
        st.write("아래에 버튼을 클릭하여 대시보드에 대한 정보를 확인할 수 있습니다.")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("데이터 확인", key="c0"):
                st.session_state.show_cluster = 0
        with col2:
            if st.button("도금 두께 예측", key="c1"):
                st.session_state.show_cluster = 1
        with col3:
            if st.button("실시간 관리도", key="c2"):
                st.session_state.show_cluster = 2

        if 'show_cluster' in st.session_state:
            cluster = st.session_state.show_cluster
            if cluster == 0:
                st.markdown("""
                <div style='border:2px solid #00aa00; padding:16px; border-radius:8px; background-color:#f0fff0;'>
                    <h4>데이터 확인</h4>
                    <ul>
                        <li>3D 데이터 값 시각화</li>
                        <li>데이터 기반 클러스터 예측</li>
                        <li>클러스터별 공정 특징 설명 확인</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            elif cluster == 1:
                st.markdown("""
                <div style='border:2px solid #ffaa00; padding:16px; border-radius:8px; background-color:#fff8e1;'>
                    <h4>도금 두께 예측</h4>
                    <ul>
                        <li>다양한 회귀 모델을 통한 도금 두께 예측</li>
                        <li>도금 두께 예측 결과 다운로드</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            elif cluster == 2:
                st.markdown("""
                <div style='border:2px solid #0066cc; padding:16px; border-radius:8px; background-color:#e8f4ff;'>
                    <h4>실시간 관리도</h4>
                    <ul>
                        <li>실시간 도금 두께 예측 및 관리도 생성</li>
                        <li>자동 그룹화 및 관리 한계 기준 분석</li>
                        <li>실시간 시각화 및 경고 표시</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
        # 하단 이미지 삽입 (중앙 정렬, 전체 너비)
        import os
        import importlib.util
        from PIL import Image

        st.markdown("<br>", unsafe_allow_html=True)
        from PIL import Image
        import os
        import importlib.util

        base_dir = os.path.dirname(__file__)
        img_path = os.path.join(base_dir, "image.png")
        image = Image.open(img_path)
        st.image(image, use_container_width=True)

    else:
        page_path = os.path.join(base_dir, "mypages", f"{page}.py")
        if os.path.exists(page_path):
            spec = importlib.util.spec_from_file_location("page_module", page_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.run()
        else:
            st.error(f"❌ '{page}.py' 파일을 찾을 수 없습니다.")



