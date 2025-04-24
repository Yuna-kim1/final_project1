import streamlit as st

def run():
    st.markdown("""
        <div style='
            background-color: #1c1c1c;
            padding: 16px 24px;
            border-radius: 12px;
            margin: 20px auto;
            text-align: center;
        '>
            <h2 style='color: white; margin: 0;'> 공정 최적화 </h2>
        </div>
    """, unsafe_allow_html=True)

    st.write("아래에 버튼을 클락하여 대시보드에 대한 정보를 확인할 수 있습니다.")

    st.subheader("대시보드 설명")
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
                    <li>온도와 전력이 비교적 낮은 공정</li>
                    <li>도금 시간이 짧은 경향</li>
                    <li>안정적인 조건의 일반적인 공정군</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        elif cluster == 1:
            st.markdown("""
            <div style='border:2px solid #ffaa00; padding:16px; border-radius:8px; background-color:#fff8e1;'>
                <h4>도금 두께 예측</h4>
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
                <h4>실시간 관리도</h4>
                <ul>
                    <li>온도 및 시간 모두 높은 고강도 공정</li>
                    <li>특수 제품 또는 고도금 작업에 해당</li>
                    <li>설비 이상 감지를 요하는 고위험 구간</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)





