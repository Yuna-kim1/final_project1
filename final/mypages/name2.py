import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.cluster import KMeans
from catboost import CatBoostRegressor

# 스타일 먼저 정의
st.markdown("""
    <style>
    /* 본문 버튼 (사이드바 제외) 스타일 고정 */
    div.stButton > button[kind="secondary"]:not([data-testid="baseButton-secondarySidebar"]):not([aria-expanded]) {
        background-color: black !important;
        color: white !important;
        border: 1px solid white !important;
        border-radius: 8px !important;
    }
    div.stButton > button[kind="secondary"]:hover:not([data-testid="baseButton-secondarySidebar"]):not([aria-expanded]) {
        background-color: #222 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

def run():
    # 제목
    st.markdown("""
        <div style='background-color: #1c1c1c; padding: 16px 24px; border-radius: 12px; margin: 20px auto; text-align: center;'>
            <h2 style='color: white; margin: 0;'> 데이터 확인</h2>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("공정 데이터 입력 및 업로드")
    st.write("입력 또는 CSV 파일 업로드를 통해 공정 데이터를 시각화할 수 있습니다.")

    if 'custom_points' not in st.session_state:
        st.session_state.custom_points = []
    if 'user_df' not in st.session_state:
        st.session_state.user_df = None

    with st.form("input_form"):
        col1, col2, col3 = st.columns(3)
        temperature = col1.number_input("Temperature (℃)", value=0.0, format="%.2f", step=1.0)
        power = col2.number_input("Power (W)", value=0.0, format="%.2f", step=200.0)
        time = col3.number_input("Time (s)", value=0.0, format="%.2f", step=100.0)

        col1, col2, col3 = st.columns([6, 2, 2])
        submitted = col2.form_submit_button("입력 추가")
        reset = col3.form_submit_button("입력 초기화")

    if submitted:
        if len(st.session_state.custom_points) < 5:
            st.session_state.custom_points.append((temperature, power, time))
        else:
            st.warning("⚠️ 5개까지만 업로드할 수 있습니다.")

    if reset:
        st.session_state.custom_points = []

    uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])
    if uploaded_file:
        try:
            df_uploaded = pd.read_csv(uploaded_file)
            required_cols = ['temperature', 'power', 'time']
            if not all(col in df_uploaded.columns for col in required_cols):
                st.error(f"CSV 파일에는 다음 컬럼이 있어야 합니다: {required_cols}")
            else:
                st.session_state.user_df = df_uploaded
        except Exception as e:
            st.error(f"파일 읽기 실패: {e}")

    if 'delete_index' not in st.session_state:
        st.session_state.delete_index = None

    if st.session_state.custom_points:
        st.markdown("**입력된 데이터 목록**")
        for i, (t, p, ti) in enumerate(st.session_state.custom_points):
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
            col1.write(f"Temperature: {t}")
            col2.write(f"Power: {p}")
            col3.write(f"Time: {ti}")
            if col5.button("❌", key=f"del_input_{i}"):
                st.session_state.delete_index = i
                st.rerun()

    if st.session_state.delete_index is not None:
        idx = st.session_state.delete_index
        if 0 <= idx < len(st.session_state.custom_points):
            st.session_state.custom_points.pop(idx)
        st.session_state.delete_index = None
        st.rerun()

    try:
        import os
        df = pd.read_csv(os.path.join("final", "oxidefilm_data.csv"))
    

    except FileNotFoundError:
        st.error("⚠️ 'oxidefilm_data.csv' 파일을 찾을 수 없습니다.")
        st.stop()

    kmeans = KMeans(n_clusters=3, random_state=42)
    df['cluster_kmeans_raw'] = kmeans.fit_predict(df[['temperature', 'power', 'time']])

    palette = {0: 'green', 1: 'orange', 2: 'cornflowerblue'}
    fig = plt.figure(figsize=(11, 10))
    ax = fig.add_subplot(111, projection='3d')

    for c in sorted(df['cluster_kmeans_raw'].unique()):
        subset = df[df['cluster_kmeans_raw'] == c]
        ax.scatter(subset['temperature'], subset['power'], subset['time'],
                   c=palette[c], alpha=0.25, label=f'Data Cluster {c}')

    highlights = ['red', 'darkorange', 'gold', 'limegreen', 'deepskyblue']
    for i, (t, p, ti) in enumerate(st.session_state.custom_points):
        color = highlights[i % len(highlights)]
        ax.scatter(t, p, ti, c=color, s=50, edgecolors='black', label=f'{i+1}')

    if st.session_state.user_df is not None:
        for i, row in st.session_state.user_df.iterrows():
            label = "upload data" if i == 0 else ""
            ax.scatter(row['temperature'], row['power'], row['time'],
                       c='black', s=50, edgecolors='black', label=label)

    ax.set_xlabel('Temperature (℃)')
    ax.set_ylabel('Power (W)')
    ax.set_zlabel('Time (s)')
    ax.legend(loc='best')
    st.pyplot(fig)

    # 클러스터 예측 결과 출력
    st.subheader("예측된 클러스터 결과")
    if not st.session_state.custom_points:
        st.markdown("""
            <div style='border:2px; background-color:#ffe5e5; padding:12px; border-radius:6px;'>
                <b>⚠️ 데이터를 입력해주세요.</b>
            </div>
        """, unsafe_allow_html=True)
    else:
        input_df = pd.DataFrame(st.session_state.custom_points, columns=['temperature', 'power', 'time'])
        preds = kmeans.predict(input_df)
        for i, cluster in enumerate(preds):
            color = '#d4f7dc' if cluster == 0 else '#fff4d6' if cluster == 1 else '#dceeff'
            border = '#00aa00' if cluster == 0 else '#ffaa00' if cluster == 1 else '#0066cc'
            st.markdown(f"""
                <div style='border-left: 8px solid {border}; background-color:{color}; padding: 10px; border-radius: 6px;'>
                    <b>{i+1}번째 데이터 → 클러스터 {cluster}</b>
                </div>
            """, unsafe_allow_html=True)

    # 클러스터 설명 버튼
    # ----------------------------------
    st.markdown("<hr style='margin-top: 40px; margin-bottom: 10px;'>", unsafe_allow_html=True)
    st.subheader("클러스터 특징")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Cluster 0: 표준형 도금 공정", key="c0"):
            st.session_state.show_cluster = 0
    with col2:
        if st.button("Cluster 1: 정밀형 도금 공정", key="c1"):
            st.session_state.show_cluster = 1
    with col3:
        if st.button("Cluster 2: 내식형 도금 공정", key="c2"):
            st.session_state.show_cluster = 2

    if 'show_cluster' in st.session_state:
        cluster = st.session_state.show_cluster
        if cluster == 0:
            st.markdown("""
            <div style='border:2px solid #00aa00; padding:16px; border-radius:8px; background-color:#f0fff0;'>
                <h4>Cluster 0: 표준형 도금 공정 특징</h4>
                <ul>
                    <li>온도와 전력이 비교적 낮은 공정</li>
                    <li>도금 시간이 짧은 경향</li>
                    <li>안정적인 조건의 일반적인 공정군</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        elif cluster == 1:
            st.markdown("""
            <div style='border:2px solid #ffaa00; padding:16px; border-radius:8px; background-color:#fff8e1;'>
                <h4>Cluste 1: 정밀형 도금 공정 특징</h4>
                <ul>
                    <li>전력이 높은 고출력 공정</li>
                    <li>도금 품질에 변동성이 큰 클러스터</li>
                    <li>공정 제어가 중요한 구간</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        elif cluster == 2:
            st.markdown("""
            <div style='border:2px solid #0066cc; padding:16px; border-radius:8px; background-color:#e8f4ff;'>
                <h4>Cluster 2: 내식형 도금 공정 특징</h4>
                <ul>
                    <li>온도 및 시간 모두 높은 고강도 공정</li>
                    <li>특수 제품 또는 고도금 작업에 해당</li>
                    <li>설비 이상 감지를 요하는 고위험 구간</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
