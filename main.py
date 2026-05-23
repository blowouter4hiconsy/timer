import streamlit as st
from datetime import datetime, time as dtime
import pytz
import time

# 1. 페이지 설정 및 서울 타임존 고정
st.set_page_config(page_title="사내 시험 타이머", layout="centered")
KST = pytz.timezone('Asia/Seoul')

st.title("⏱️ 사내 평가용 자동 시험 타이머")
st.caption("※ 서울 표준시 기준으로 작동하며, 기기 상관없이 브라우저에서 바로 사용 가능합니다.")

# 2. 시험 과목 선택 (업무 확장성을 위해 메뉴화)
exam_type = st.selectbox("진행할 시험을 선택하세요:", ["1교시 국어", "직무/보안 교육 (테스트용)"])

# 과목별 알람 시간 세팅
if exam_type == "1교시 국어":
    times = {
        "pre": dtime(8, 25),    # 예비령
        "ready": dtime(8, 35),  # 준비령
        "main": dtime(8, 40),   # 본령
        "end": dtime(10, 0)     # 종료령
    }
else:
    # 테스트용 시간 (현재 컴퓨터 시간 근처로 자유롭게 수정해서 테스트하세요)
    times = {
        "pre": dtime(13, 0),
        "ready": dtime(13, 5),
        "main": dtime(13, 10),
        "end": dtime(14, 0)
    }

# 기본 알람 소리 (구글 오디오 가이드용 파일)
ALARM_URL = "https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg"

# 3. 타이머 구동 상태 관리
if "run" not in st.session_state:
    st.session_state.run = False
if "fired" not in st.session_state:
    st.session_state.fired = []

# 4. 제어 버튼
if not st.session_state.run:
    if st.button("🚀 시험 타이머 가동 (클릭 필수)", use_container_width=True, type="primary"):
        st.session_state.run = True
        st.session_state.fired = []
        st.rerun()
else:
    if st.button("⏹️ 타이머 중지 및 초기화", use_container_width=True):
        st.session_state.run = False
        st.session_state.fired = []
        st.rerun()

st.markdown("---")

# 5. 실시간 감시 루프
if st.session_state.run:
    clock_spot = st.empty()
    status_spot = st.empty()
    audio_spot = st.empty()

    while st.session_state.run:
        now = datetime.now(KST)
        curr = now.time()

        # 실시간 시계 노출
        clock_spot.markdown(f"""
        <div style='text-align: center; border: 2px solid #4B79A1; padding: 15px; border-radius: 10px; background-color: #F0F4F8;'>
            <p style='margin: 0; color: #555; font-weight: bold;'>{exam_type} - 현재 서울 시간</p>
            <h1 style='margin: 0; font-size: 60px; color: #4B79A1;'>{now.strftime('%H:%M:%S')}</h1>
        </div>
        """, unsafe_allow_html=True)

        # 타임라인별 알람 트리거
        if curr >= times["pre"] and curr < times["ready"]:
            status_spot.warning(f"🔔 [예비령] 시험 준비 시각입니다. ({times['pre'].strftime('%H:%M')})")
            if "pre" not in st.session_state.fired:
                st.session_state.fired.append("pre")
                with audio_spot:
                    st.components.v1.html(f'<audio autoplay><source src="{ALARM_URL}" type="audio/ogg"></audio>', height=0)

        elif curr >= times["ready"] and curr < times["main"]:
            status_spot.error(f"🔔 [준비령] 문제지 배부 및 인적사항 기재 시각입니다. ({times['ready'].strftime('%H:%M')})")
            if "ready" not in st.session_state.fired:
                st.session_state.fired.append("ready")
                with audio_spot:
                    st.components.v1.html(f'<audio autoplay><source src="{ALARM_URL}" type="audio/ogg"></audio>', height=0)

        elif curr >= times["main"] and curr < times["end"]:
            # 남은 시간 실시간 계산
            end_dt = datetime.combine(now.date(), times["end"]).localize(KST)
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
            status_spot.write("⏳ 시험 시작 대기 중입니다...")

        time.sleep(1)
