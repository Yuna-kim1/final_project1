import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
import time
import os

# 스타일
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

    # 데이터 & 모델
    df_train = pd.read_csv(os.path.join("final", "oxidefilm_data.csv"))
    X_train = df_train[['time', 'temperature', 'rectifier', 'power']]
    y_train = df_train['mean_um']
    model = XGBRegressor(random_state=42)
    model.fit(X_train, y_train)

    uploaded_file = st.file_uploader("CSV 파일 업로드:", type=["csv"])
    if not uploaded_file:
        return

    df_new = pd.read_csv(uploaded_file)
    X_new = df_new[['time', 'temperature', 'rectifier', 'power']]
    df_new['predicted_mean_um'] = model.predict(X_new)

    available_vars = ['predicted_mean_um', 'time', 'temperature', 'rectifier', 'power']
    selected_var = st.selectbox("관리도를 그릴 변수를 선택하세요:", available_vars)

    n = 4
    total_groups = len(df_new) // n
    subgroups = np.array_split(df_new[selected_var][:total_groups * n], total_groups)

    xbar_list = [np.mean(g) for g in subgroups]
    r_list = [np.max(g) - np.min(g) for g in subgroups]

    xbar_bar = np.mean(xbar_list[:10])
    r_bar = np.mean(r_list[:10])
    A2, D3, D4 = 0.729, 0.0, 2.282
    UCL_xbar = xbar_bar + A2 * r_bar
    LCL_xbar = xbar_bar - A2 * r_bar
    UCL_r = D4 * r_bar
    LCL_r = D3 * r_bar

    d2 = 2.059
    sigma_est = r_bar / d2
    zone_A_upper = xbar_bar + 2 * sigma_est
    zone_A_lower = xbar_bar - 2 * sigma_est
    zone_B_upper = xbar_bar + sigma_est
    zone_B_lower = xbar_bar - sigma_est

    x_labels = [f'G{i+1}' for i in range(total_groups)]
    placeholder = st.empty()
    warning_box = st.empty()

    xbar_vals, r_vals = [], []
    all_warnings = []

    for i in range(total_groups):
        xbar_vals.append(xbar_list[i])
        r_vals.append(r_list[i])
        warnings = []

        # Rule checks
        if xbar_list[i] > UCL_xbar or xbar_list[i] < LCL_xbar:
            warnings.append(f"[{x_labels[i]}] Rule 1: 한 점이 관리 한계를 벗어났습니다.")
        if len(xbar_vals) >= 9:
            last9 = xbar_vals[-9:]
            if all(x > xbar_bar for x in last9) or all(x < xbar_bar for x in last9):
                warnings.append(f"[{x_labels[i]}] Rule 2: 같은 방향 9점 연속입니다.")
        if len(xbar_vals) >= 6:
            diffs = np.diff(xbar_vals[-6:])
            if all(diffs > 0) or all(diffs < 0):
                warnings.append(f"[{x_labels[i]}] Rule 3: 6점 연속 증가/감소입니다.")
        if len(xbar_vals) >= 14:
            alt = xbar_vals[-14:]
            if all((alt[j] > xbar_bar and alt[j+1] < xbar_bar) or (alt[j] < xbar_bar and alt[j+1] > xbar_bar) for j in range(13)):
                warnings.append(f"[{x_labels[i]}] Rule 4: 14점 교대로 위/아래 분포입니다.")
        if len(xbar_vals) >= 3:
            cnt = sum(1 for x in xbar_vals[-3:] if x > zone_A_upper or x < zone_A_lower)
            if cnt >= 2:
                warnings.append(f"[{x_labels[i]}] Rule 5: 3점 중 2점이 2σ 바깥입니다.")
        if len(xbar_vals) >= 5:
            cnt = sum(1 for x in xbar_vals[-5:] if x > zone_B_upper or x < zone_B_lower)
            if cnt >= 4:
                warnings.append(f"[{x_labels[i]}] Rule 6: 5점 중 4점이 1σ 바깥입니다.")
        if len(xbar_vals) >= 15 and all(zone_B_lower <= x <= zone_B_upper for x in xbar_vals[-15:]):
            warnings.append(f"[{x_labels[i]}] Rule 7: 15점 연속 1σ 이내입니다.")
        if len(xbar_vals) >= 8 and all(x > zone_B_upper or x < zone_B_lower for x in xbar_vals[-8:]):
            warnings.append(f"[{x_labels[i]}] Rule 8: 8점 연속 1σ 바깥입니다.")

        all_warnings.extend(warnings)

        # 실시간 관리도
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        ax1.plot(x_labels[:i+1], xbar_vals, marker='o', color='blue')
        ax1.axhline(UCL_xbar, color='red', linestyle='--')
        ax1.axhline(xbar_bar, color='green')
        ax1.axhline(LCL_xbar, color='red', linestyle='--')
        ax1.set_title(f"X-bar Chart ({selected_var})")
        ax1.grid(True)

        ax2.plot(x_labels[:i+1], r_vals, marker='o', color='purple')
        ax2.axhline(UCL_r, color='red', linestyle='--')
        ax2.axhline(r_bar, color='green')
        ax2.axhline(LCL_r, color='red', linestyle='--')
        ax2.set_title("R Chart")
        ax2.grid(True)

        fig.tight_layout()
        placeholder.pyplot(fig)
        plt.close(fig)

        # ⚠️ 경고 메시지 누적 표시
        if all_warnings:
            warning_box.markdown(
                "<div style='max-height: 200px; overflow-y: auto;'>"
                + "".join(f"<p>⚠️ {msg}</p>" for msg in all_warnings)
                + "</div>",
                unsafe_allow_html=True
            )

        time.sleep(0.5)

# 실행
if __name__ == "__main__":
    run()






