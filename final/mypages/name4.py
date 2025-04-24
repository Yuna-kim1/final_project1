import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
import time

# 페이지 상단 스타일
st.markdown("""
    <style>
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
        <h2 style='color: white; margin: 0;'>실시간 관리도</h2>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("X bar-R 관리도")

    df_train = pd.read_csv("oxidefilm_data.csv")
    X_train = df_train[['time', 'temperature', 'rectifier', 'power']]
    y_train = df_train['mean_um']
    model = XGBRegressor(random_state=42)
    model.fit(X_train, y_train)

    uploaded_file = st.file_uploader("도금 두께를 예측하여(XgBoost), 도금 상태를 실시간으로 확인할 수 있습니다.", type=["csv"])
    if not uploaded_file:
        st.stop()

    df_new = pd.read_csv(uploaded_file)
    X_new = df_new[['time', 'temperature', 'rectifier', 'power']]
    df_new['predicted_mean_um'] = model.predict(X_new)

    # 🎯 변수 선택 필터 추가
    available_vars = ['predicted_mean_um', 'time', 'temperature', 'rectifier', 'power']
    selected_var = st.selectbox("관리도를 그릴 변수를 선택하세요:", available_vars)

    # 관리도용 그룹 설정
    n = 4
    total_groups = len(df_new) // n
    subgroups = np.array_split(df_new[selected_var][:total_groups * n], total_groups)

    xbar_list = [np.mean(g) for g in subgroups]
    r_list = [np.max(g) - np.min(g) for g in subgroups]

    xbar_base = xbar_list[:10]
    r_base = r_list[:10]

    xbar_bar = np.mean(xbar_base)
    r_bar = np.mean(r_base)
    A2 = 0.729
    D4 = 2.282
    D3 = 0

    UCL_xbar = xbar_bar + A2 * r_bar
    LCL_xbar = xbar_bar - A2 * r_bar
    UCL_r = D4 * r_bar
    LCL_r = D3 * r_bar

    x_labels = [f'G{i+1}' for i in range(total_groups)]
    placeholder = st.empty()

    xbar_vals = []
    r_vals = []

    for i in range(total_groups):
        xbar_vals.append(xbar_list[i])
        r_vals.append(r_list[i])

        warnings = []
        if xbar_list[i] > UCL_xbar or xbar_list[i] < LCL_xbar:
            warnings.append(f"{x_labels[i]} 그룹: X-bar 관리 한계를 벗어났습니다.")
        if r_list[i] > UCL_r or r_list[i] < LCL_r:
            warnings.append(f"{x_labels[i]} 그룹: R 관리 한계를 벗어났습니다.")

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        # X-bar
        ax1.plot(x_labels[:i+1], xbar_vals, marker='o', color='blue', label='Mean (X-bar)')
        ax1.axhline(UCL_xbar, color='red', linestyle='--', label='UCL')
        ax1.axhline(xbar_bar, color='green', linestyle='-', label='CL')
        ax1.axhline(LCL_xbar, color='red', linestyle='--', label='LCL')
        ax1.set_title(f"X-bar Control Chart ({selected_var})")
        ax1.set_ylabel("Mean")
        ax1.legend()
        ax1.grid(True)

        # R
        ax2.plot(x_labels[:i+1], r_vals, marker='o', color='purple', label='Range (R)')
        ax2.axhline(UCL_r, color='red', linestyle='--', label='UCL')
        ax2.axhline(r_bar, color='green', linestyle='-', label='CL')
        ax2.axhline(LCL_r, color='red', linestyle='--', label='LCL')
        ax2.set_title("R Control Chart")
        ax2.set_ylabel("Range")
        ax2.set_xlabel("Group")
        ax2.legend()
        ax2.grid(True)

        fig.tight_layout()
        placeholder.pyplot(fig)
        plt.close(fig)

        for msg in warnings:
            st.warning(msg)

        time.sleep(0.001)


