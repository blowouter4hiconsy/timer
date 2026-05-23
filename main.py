import streamlit as st
from datetime import datetime, time as dtime, timedelta
import pytz
import time

# 1. 페이지 설정 및 서울 타임존 고정
st.set_page_config(page_title="사내 시험 타이머", layout="centered")
KST = pytz.timezone('Asia/Seoul')

st.title("⏱️ 사내 평가용 자동 시험 타이머")
st.caption("※ 서울 표준시 기준으로 작동하며, 기기 상관없이 브라우저에서 바로 사용 가능합니다.")

# 2. 시험 과목 선택
exam_type = st.selectbox("진행할 시험을 선택하세요:", ["1교시 국어", "직무/보안 교육 (테스트용)"])

# 기본 알람 소리 (구글 오디오 가이드용 파일)
ALARM_URL = "https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg"

# 3. 타이머 구동 상태 관리
if "run" not in st.session_state:
    st.session_state.run = False
if "fired" not in st.session_state:
    st.session_state.fired = []
if "times" not in st.session_state:
    st.session_state.times = {}

# 4. 제어 버튼
if not st.session_state.run:
    if st.button("🚀 시험 타이머 가동 (클릭 필수)", use_container_width=True, type="primary"):
        st.session_state.run = True
        st.session_state.fired = []
        
        # ★ 핵심 수정: 버튼을 누른 '현재 시점'을 기준으로 타임라인을 생성합니다.
        if exam_type == "1교시 국어":
            st.session_state.times = {
                "pre": dtime(8, 25),    # 예비령 정각
                "ready": dtime(8, 35),  # 준비령 정각
                "main": dtime(8, 40),   # 본령 정각
                "end": dtime(10, 0)     # 종료령 정각
            }
        else:
            # [테스트용 선택 시] 버튼 누른 현재 시간에서 자동으로 분 단위를 더함
            now_init = datetime.now(KST)
            st.session_state.times = {
                "pre": (now_init + timedelta(minutes=1)).time(),    # 1분 뒤 예비령
                "ready": (now_init + timedelta(minutes=2)).time(),  # 2분 뒤 준비령
                "main": (now_init + timedelta(minutes=3)).time(),   # 3분 뒤 본령
                "end": (now_init + timedelta(minutes=5)).time()     # 5분 뒤 종료령
            }
        st.rerun()
else:
    if st.button("⏹️ 타이머 중지 및 초기화", use_container_width=True):
        st.session_state.run = False
        st.session_state.fired = []
        st.session_state.times = {}
        st.rerun()

st.markdown("---")

# 5. 실시간 감시 루프
elif curr >= times["main"] and curr < times["end"]:
            # 남은 시간 실시간 계산 (수정됨)
            end_dt = KST.localize(datetime.combine(now.date(), times["end"]))
            rem = int((end_dt - now).total_seconds())
            mins, secs = divmod(rem, 60)
            
            status_spot.info(f"✍️ [본령] 시험 진행 중 (종료까지 {mins}분 {secs}초 남음)")
            if "main" not in st.session_state.fired:
                st.session_state.fired.append("main")
                with audio_spot:
                    st.components.v1.html(f'<audio autoplay><source src="{ALARM_URL}" type="audio/ogg"></audio>', height=0)

        elif curr >= times["end"]:
            status_spot.markdown("<h1 style='text-align: center; color: red;'>🚨 시험 종료 🚨</h1>", unsafe_allow_html=True)
            if "end" not in st.session_state.fired:
                st.session_state.fired.append("end")
                with audio_spot:
                    st.components.v1.html(f'<audio autoplay><source src="{ALARM_URL}" type="audio/ogg"></audio>', height=0)
                st.balloons()
            st.session_state.run = False
            break
        else:
            # 아직 예비령 시간이 안 되었을 때 남은 초 표시 (수정됨)
            pre_dt = KST.localize(datetime.combine(now.date(), times["pre"]))
            wait_secs = int((pre_dt - now).total_seconds())
            status_spot.write(f"⏳ 시험 시작 대기 중... (예비령까지 {wait_secs}초 남음)")

        time.sleep(1)
