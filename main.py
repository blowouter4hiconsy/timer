# main.py
import streamlit as st
from datetime import datetime
import pytz
import time
import os

# 🌟 핵심: 방금 만든 config.py 창고에서 데이터 꺼내오는 함수를 수입합니다!
from config import get_all_audio_files, get_schedules

st.set_page_config(page_title="수능형 사내 시험 타이머", layout="centered")
KST = pytz.timezone('Asia/Seoul')

if not os.path.exists("sounds"):
    os.makedirs("sounds")

st.title("⏱️ 수능 실전형 자동 시험 타이머")

exam_type = st.selectbox(
    "진행할 항목을 선택하세요:", 
    ["☀️ 전교시 자동 진행 (1~4교시 전체)", "1교시 국어", "2교시 수학", "3교시 영어 (듣기 자동포함)", "4교시 한국사/탐구 (연속진행)", "🔥 종합 종소리 테스트 (30초 간격 & 수동 제어)"]
)

if exam_type in ["☀️ 전교시 자동 진행 (1~4교시 전체)", "3교시 영어 (듣기 자동포함)", "🔥 종합 종소리 테스트 (30초 간격 & 수동 제어)"]:
    uploaded_file = st.file_uploader("여기에 13시 10분에 재생할 mp3 파일을 마우스로 끌어다 놓으세요!", type=["mp3"])
    if uploaded_file is not None:
        selected_english_file = "10 1310 3교시 직접올린영어듣기.mp3"
        with open(f"sounds/{selected_english_file}", "wb") as f:
            f.write(uploaded_file.getbuffer())
    else:
        selected_english_file = "10 1310 3교시 기본영어듣기.mp3" 
else:
    selected_english_file = "10 1310 3교시 기본영어듣기.mp3"

st.markdown("---")

# 🌟 창고에서 파일 목록 데이터 받아오기
ALL_AUDIO_FILES = get_all_audio_files(selected_english_file)

if "run" not in st.session_state:
    st.session_state.run = False
if "fired" not in st.session_state:
    st.session_state.fired = []
if "start_time" not in st.session_state:
    st.session_state.start_time = None

if not st.session_state.run:
    if st.button("🚀 타이머/테스트 시작", use_container_width=True, type="primary"):
        st.session_state.run = True
        st.session_state.fired = []
        st.session_state.start_time = time.time()
        st.rerun()
else:
    if st.button("⏹️ 타이머 중지 및 초기화", use_container_width=True):
        st.session_state.run = False
        st.session_state.fired = []
        st.rerun()

st.markdown("---")

if st.session_state.run:
    clock_spot = st.empty()
    status_spot = st.empty()
    audio_spot = st.empty()

    while st.session_state.run:
        now = datetime.now(KST)
        curr = now.time()

        clock_spot.markdown(f"<h1 style='text-align: center;'>{now.strftime('%H:%M:%S')}</h1>", unsafe_allow_html=True)

        # 🌟 창고에서 현재 시험 과목에 맞는 시간표 받아오기
        schedules = get_schedules(exam_type, selected_english_file)

        for target_time, file_name in schedules.items():
            if curr.hour == target_time.hour and curr.minute == target_time.minute:
                if file_name not in st.session_state.fired:
                    st.session_state.fired.append(file_name)
                    with audio_spot:
                        st.audio(f"sounds/{file_name}", autoplay=True)
        
        upcoming = [t for t in schedules.keys() if curr < t]
        if upcoming:
            next_time = min(upcoming)
            status_spot.info(f"⏳ 다음 방송 예정: {schedules[next_time]}")
        else:
            status_spot.warning("🚨 모든 일정이 종료되었습니다")
            st.session_state.run = False
            break

        time.sleep(1)
