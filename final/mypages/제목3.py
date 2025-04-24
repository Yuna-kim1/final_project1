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

def run():
    st.markdown("""
    <div style='background-color: #1c1c1c; padding: 16px 24px; border-radius: 12px; margin: 20px auto; text-align: center;'>
        <h2 style='color: white; margin: 0;'> 도금 두께 예측</h2>
    </div>
    """, unsafe_allow_html=True)

    # 데이터 로드
    try:
        df = pd.read_csv("oxidefilm_data.csv")
    except FileNotFoundError:
        st.error("⚠️ 'oxidefilm_data.csv' 파일이 없습니다.")
        return

    # 학습 설정
    st.subheader("학습 설정")
    test_size = st.slider("테스트 비율", 0.1, 0.4, 0.2)
    random_state = st.number_input("랜덤 스테이트(SEED)", value=42, step=1)

    # 모델 선택
    model_options = ["RandomForest", "XGBoost", "LGBM", "CatBoost"]
    model_name = st.selectbox("모델 선택", model_options)

    # 독립/종속 변수 고정
    features = ['temperature','rectifier', 'power', 'time']
    target = 'mean_um'

    # 모델 학습 및 평가
    if st.button("모델 학습 및 평가", key="train_eval"):
        X, y = df[features], df[target]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state)

        # 모델 초기화
        if model_name == "CatBoost":
            model = CatBoostRegressor(verbose=0, random_state=random_state)
        elif model_name == "RandomForest":
            model = RandomForestRegressor(random_state=random_state)
        elif model_name == "XGBoost":
            model = XGBRegressor(random_state=random_state, verbosity=0)
        else:
            model = LGBMRegressor(random_state=random_state)

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        # 세션 저장
        st.session_state['ml_model'] = model
        st.session_state['eval_name'] = model_name
        st.session_state['eval_rmse'] = rmse
        st.session_state['eval_r2'] = r2

    # 학습 결과 박스
    if 'eval_rmse' in st.session_state:
        st.markdown(f"""
        <div style='border:2px solid #ccc; padding:16px; border-radius:8px; background-color:#ffffff; color:#000000; margin-top:20px; text-align: center;'>
            <h4 style='margin:0 0 8px 0; font-size:20px;'>모델 평가 결과 ({st.session_state['eval_name']})</h4>
            <div><strong>RMSE:</strong> {st.session_state['eval_rmse']:.4f}</div>
            <div><strong>R²:</strong> {st.session_state['eval_r2']:.4f}</div>
        </div>
        """, unsafe_allow_html=True)

    # ----------------------------------
    # 예측 및 파일 다운로드 구간 시작
    # ----------------------------------
    st.markdown("<hr style='margin-top: 40px; margin-bottom: 10px;'>", unsafe_allow_html=True)
    st.subheader("데이터 예측")

    uploaded_file = st.file_uploader("예측할 CSV 파일을 업로드하세요.", type=["csv"])

    if uploaded_file and 'ml_model' in st.session_state:
        df_new = pd.read_csv(uploaded_file)

        # 입력값에 필요한 feature가 포함되어 있는지 확인
        if not all(f in df_new.columns for f in features):
            st.error(f"입력 파일에 다음 컬럼이 포함되어 있어야 합니다: {features}")
        else:
            X_new = df_new[features]
            y_new_pred = st.session_state['ml_model'].predict(X_new)
            df_new['predicted_mean_um'] = y_new_pred

            # 예측 결과 표시
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("예측 결과")
            st.dataframe(df_new)

            # CSV 다운로드용 버튼
            csv = df_new.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 예측 결과 CSV 다운로드",
                data=csv,
                file_name="predicted_mean_um_result.csv",
                mime="text/csv"
            )
    elif uploaded_file:
        st.warning("먼저 모델을 학습해 주세요.")

