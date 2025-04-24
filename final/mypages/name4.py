import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
import time
import os

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

    st.subheader("X-bar & R 관리도")

    # --- 학습 데이터 로드 및 모델 학습 ---
    df_train = pd.read_csv(os.path.join("final", "oxidefilm_data.csv"))
    X_train = df_train[['time', 'temperature', 'rectifier', 'power']]
    y_train = df_train['mean_um']
    model = XGBRegressor(random_state=42)
    model.fit(X_train, y_train)

    # --- 새 데이터 업로드 및 예측 ---
    uploaded_file = st.file_uploader(
        "도금 두께를 예측하여(XGBoost), 도금 상태를 실시간으로 확인할 수 있습니다.", 
        type=["csv"]
    )
    if not uploaded_file:
        return

    df_new = pd.read_csv(uploaded_file)
    X_new = df_new[['time', 'temperature', 'rectifier', 'power']]
    df_new['predicted_mean_um'] = model.predict(X_new)

    # --- 변수 선택 ---
    available_vars = ['predicted_mean_um', 'time', 'temperature', 'rectifier', 'power']
    selected_var = st.selectbox("관리도를 그릴 변수를 선택하세요:", available_vars)

    # --- subgroup 설정 및 X-bar/R 계산 ---
    n = 4  # subgroup size
    total_groups = len(df_new) // n
    subgroups = np.array_split(df_new[selected_var][:total_groups * n], total_groups)

    xbar_list = [np.mean(g) for g in subgroups]
    r_list    = [np.max(g) - np.min(g) for g in subgroups]

    # 기준선 계산용 첫 10그룹
    xbar_base = xbar_list[:10]
    r_base    = r_list[:10]
    xbar_bar  = np.mean(xbar_base)
    r_bar     = np.mean(r_base)

    # A2, D3, D4 값 (n=4)
    A2, D3, D4 = 0.729, 0.0, 2.282
    UCL_xbar = xbar_bar + A2 * r_bar
    LCL_xbar = xbar_bar - A2 * r_bar
    UCL_r    = D4 * r_bar
    LCL_r    = D3 * r_bar

    # --- Nelson 규칙용 σ 및 zone 계산 ---
    # d2 (n=4) = 2.059
    d2 = 2.059
    sigma_est = r_bar / d2

    zone_A_upper = xbar_bar + 2 * sigma_est
    zone_A_lower = xbar_bar - 2 * sigma_est
    zone_B_upper = xbar_bar + sigma_est
    zone_B_lower = xbar_bar - sigma_est
    # zone_C는 ±1σ 이내
    zone_C_upper = zone_B_upper
    zone_C_lower = zone_B_lower

    x_labels = [f'G{i+1}' for i in range(total_groups)]
    placeholder = st.empty()

    xbar_vals = []
    r_vals    = []

    # --- 그룹별 실시간 업데이트 및 이상 탐지 ---
    for i in range(total_groups):
        xbar_vals.append(xbar_list[i])
        r_vals.append(r_list[i])

        warnings = []

        # Rule 1: UCL/LCL 벗어남
        if xbar_list[i] > UCL_xbar or xbar_list[i] < LCL_xbar:
            warnings.append("Rule 1: 한 점이 관리 한계를 벗어났습니다.")

        # Rule 2: 같은 방향 9점 연속
        if len(xbar_vals) >= 9:
            last9 = xbar_vals[-9:]
            if all(x > xbar_bar for x in last9) or all(x < xbar_bar for x in last9):
                warnings.append("Rule 2: 중심선으로부터 같은 방향 9점 연속입니다.")

        # Rule 3: 6점 연속 증가/감소
        if len(xbar_vals) >= 6:
            last6 = xbar_vals[-6:]
            diffs = np.diff(last6)
            if all(diffs > 0) or all(diffs < 0):
                warnings.append("Rule 3: 6점 연속 증가/감소 추세입니다.")

        # Rule 4: 14점 교대로 위/아래
        if len(xbar_vals) >= 14:
            last14 = xbar_vals[-14:]
            alt = all(
                (last14[j] > xbar_bar and last14[j+1] < xbar_bar) or
                (last14[j] < xbar_bar and last14[j+1] > xbar_bar)
                for j in range(13)
            )
            if alt:
                warnings.append("Rule 4: 14점 교대로 위/아래 분포입니다.")

        # Rule 5: 3점 중 2점이 2σ 밖 같은 방향
        if len(xbar_vals) >= 3:
            last3 = xbar_vals[-3:]
            cnt = sum(1 for x in last3 if x > zone_A_upper or x < zone_A_lower)
            if cnt >= 2:
                warnings.append("Rule 5: 3점 중 2점이 2σ 바깥 같은 방향입니다.")

        # Rule 6: 5점 중 4점이 1σ 밖 같은 방향
        if len(xbar_vals) >= 5:
            last5 = xbar_vals[-5:]
            cnt = sum(1 for x in last5 if x > zone_B_upper or x < zone_B_lower)
            if cnt >= 4:
                warnings.append("Rule 6: 5점 중 4점이 1σ 바깥 같은 방향입니다.")

        # Rule 7: 15점 연속 1σ 이내
        if len(xbar_vals) >= 15:
            last15 = xbar_vals[-15:]
            if all(zone_C_lower <= x <= zone_C_upper for x in last15):
                warnings.append("Rule 7: 15점 연속 1σ 이내 분포입니다.")

        # Rule 8: 8점 연속 1σ 밖 (zone A 또는 B)
        if len(xbar_vals) >= 8:
            last8 = xbar_vals[-8:]
            if all((x > zone_B_upper or x < zone_B_lower) for x in last8):
                warnings.append("Rule 8: 8점 연속 1σ 바깥 분포입니다.")

        # --- 관리도 그리기 ---
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        # X-bar 차트
        ax1.plot(x_labels[:i+1], xbar_vals, marker='o', color='blue', label='X-bar')
        ax1.axhline(UCL_xbar, color='red', linestyle='--', label='UCL')
        ax1.axhline(xbar_bar, color='green', linestyle='-', label='CL')
        ax1.axhline(LCL_xbar, color='red', linestyle='--', label='LCL')
        ax1.set_title(f"X-bar Control Chart ({selected_var})")
        ax1.set_ylabel("Mean")
        ax1.legend()
        ax1.grid(True)

        # R 차트
        ax2.plot(x_labels[:i+1], r_vals, marker='o', color='purple', label='R')
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

        # --- 이상 징후 표시 ---
        for msg in warnings:
            st.warning(msg)

        time.sleep(0.5)  # 업데이트 속도 조절

# 앱 실행
if __name__ == "__main__":
    run()



