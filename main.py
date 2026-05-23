import streamlit as st
from datetime import datetime, time as dtime, timedelta
import pytz
import time
import os

# 1. 페이지 설정 및 서울 타임존 고정
st.set_page_config(page_title="수능형 사내 시험 타이머", layout="centered")
KST = pytz.timezone('Asia/Seoul')

# sounds 폴더가 없으면 자동 생성 (오류 방지용)
if not os.path.exists("sounds"):
    os.makedirs("sounds")

st.title("⏱️ 수능 실전형 자동 시험 타이머")
st.caption("※ 실제 수능 시간표 및 종소리 파일과 연동하여 작동합니다.")

# 2. 시험 과목 및 테스트 선택 드롭다운
exam_type = st.selectbox(
    "진행할 항목을 선택하세요:", 
    [
        "☀️ 전교시 자동 진행 (1~4교시 전체)",
        "1교시 국어", 
        "2교시 수학", 
        "3교시 영어 (듣기 자동포함)", 
        "4교시 한국사/탐구 (연속진행)", 
        "🔥 종합 종소리 테스트 (30초 간격 & 수동 제어)"
    ]
)

# 🎧 [핵심 기능] 드래그 앤 드롭으로 듣기 파일 직접 넣기 (File Uploader)
if exam_type in ["☀️ 전교시 자동 진행 (1~4교시 전체)", "3교시 영어 (듣기 자동포함)", "🔥 종합 종소리 테스트 (30초 간격 & 수동 제어)"]:
    st.markdown("### 🎧 3교시 영어 듣기 파일 업로드")
    
    # st.file_uploader가 마우스로 끌어다 놓는 드래그 앤 드롭 영역을 만들어줍니다!
    uploaded_file = st.file_uploader(
        "여기에 13시 10분에 재생할 mp3 파일을 마우스로 끌어다 놓으세요!", 
        type=["mp3"]
    )
    
    if uploaded_file is not None:
        # 사용자가 올린 파일을 기존 시스템 이름 규칙에 맞게 저장 (안내 메시지 출력용)
        selected_english_file = "10 1310 3교시 직접올린영어듣기.mp3"
        
        # 파일을 sounds 폴더 안에 덮어쓰기로 임시 저장합니다.
        with open(f"sounds/{selected_english_file}", "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        st.success(f"✅ '{uploaded_file.name}' 파일이 13시 10분 일정으로 세팅되었습니다!")
    else:
        # 파일을 아직 안 올렸을 때의 기본값
        selected_english_file = "10 1310 3교시 기본영어듣기.mp3" 
        st.warning("⚠️ 아직 파일을 넣지 않았습니다. (파일을 넣기 전에는 기본 듣기 파일이 재생됩니다)")
else:
    # 영어가 없는 교시 선택 시 임시값
    selected_english_file = "10 1310 3교시 기본영어듣기.mp3"

st.markdown("---")

# 전체 20개 파일 목록 정의 (업로드한 파일이 10번째 인덱스에 자동 삽입됨!)
ALL_AUDIO_FILES = [
    "01 0825 1교시 예비령.mp3", "02 0835 1교시 준비령.mp3", "03 0840 1교시 본령.mp3", "04 1000 1교시 종료령.mp3",
    "05 1020 2교시 예비령.mp3", "06 1025 2교시 준비령.mp3", "07 1030 2교시 본령.mp3", "08 1210 2교시 종료령.mp3",
    "09 1300 3교시 예비령.mp3", 
    selected_english_file,  # 🌟 화면에서 마우스로 던져 넣은 파일이 바로 여기에 꽂힙니다.
    "11 1420 3교시 종료령.mp3",
    "12 1440 4교시 한국사 예비령.mp3", "13 1445 4교시 한국사 준비령.mp3", "14 1450 4교시 한국사 본령.mp3", "15 1520 4교시 한국사 종료령.mp3",
    "16 1525 4교시 탐구 준비령.mp3", "17 1535 4교시 탐구 첫째본령.mp3", "18 1605 4교시 탐구 첫째종료령.mp3", "19 1607 4교시 탐구 둘째본령.mp3", "20 1637 4교시 탐구 둘째종료령.mp3"
]

# 🛠️ 테스트 모드일 때 수동으로 파일 번호를 조절할 수 있는 슬라이더
if exam_type == "🔥 종합 종소리 테스트 (30초 간격 & 수동 제어)":
    st.markdown("### 🎛️ 테스트 수동 제어 패널")
    if "current_test_idx" not in st.session_state:
        st.session_state.current_test_idx = 1
        
    slider_idx = st.slider(
        "테스트할 파일 번호를 선택하세요 (드래그하거나 방향키 조절):", 
        min_value=1, 
        max_value=len(ALL_AUDIO_FILES), 
        value=st.session_state.current_test_idx,
        key="test_slider"
    )
    
    if slider_idx != st.session_state.current_test_idx:
        st.session_state.current_test_idx = slider_idx
        current_file = ALL_AUDIO_FILES[slider_idx - 1]
        if current_file in st.session_state.fired:
            st.session_state.fired.remove(current_file)
        st.session_state.start_time = time.time() - ((slider_idx - 1) * 30)

# 3. 타이머 구동 상태 관리 변수 초기화
if "run" not in st.session_state:
    st.session_state.run = False
if "fired" not in st.session_state:
    st.session_state.fired = []
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# 4. 제어 버튼 (시작 / 중지)
if not st.session_state.run:
    if st.button("🚀 타이머/테스트 시작", use_container_width=True, type="primary"):
        st.session_state.run = True
        st.session_state.fired = []
        if exam_type == "🔥 종합 종소리 테스트 (30초 간격 & 수동 제어)":
            st.session_state.start_time = time.time() - ((st.session_state.current_test_idx - 1) * 30)
        else:
            st.session_state.start_time = time.time()
        st.rerun()
else:
    if st.button("⏹️ 타이머 중지 및 초기화", use_container_width=True):
        st.session_state.run = False
        st.session_state.fired = []
        st.session_state.start_time = None
        if "current_test_idx" in st.session_state:
            st.session_state.current_test_idx = 1
        st.rerun()

st.markdown("---")

# 5. 실시간 감시 및 재생 루프
if st.session_state.run:
    clock_spot = st.empty()
    status_spot = st.empty()
    audio_spot = st.empty()

    while st.session_state.run:
        # [A] 🔥 종합 종소리 테스트 모드 (30초 간격 및 수동 이동 로직)
        if exam_type == "🔥 종합 종소리 테스트 (30초 간격 & 수동 제어)":
            elapsed = int(time.time() - st.session_state.start_time)
            idx = elapsed // 30  
            
            if idx >= len(ALL_AUDIO_FILES):
                status_spot.success("🎉 모든 종소리 파일 테스트가 완료되었습니다!")
                st.session_state.run = False
                break
                
            st.session_state.current_test_idx = idx + 1
            current_file = ALL_AUDIO_FILES[idx]
            countdown = 30 - (elapsed % 30) 
            
            clock_spot.markdown(f"""
            <div style='text-align: center; border: 2px solid #FF4B4B; padding: 15px; border-radius: 10px; background-color: #FFF0F0;'>
                <p style='margin: 0; color: #FF4B4B; font-weight: bold;'>🚨 전체 종소리 기능 테스트 중 ({idx + 1} / {len(ALL_AUDIO_FILES)})</p>
                <h2 style='margin: 10px 0; color: #333;'>{current_file}</h2>
                <p style='margin: 0; color: #555;'>다음 파일 재생까지 <b>{countdown}초</b> 남음</p>
            </div>
            """, unsafe_allow_html=True)
            
            if current_file not in st.session_state.fired:
                st.session_state.fired.append(current_file)
                with audio_spot:
                    st.audio(f"sounds/{current_file}", autoplay=True)

        # [B] ⏰ 실제 교시별 수능 시험 모드 로직
        else:
            now = datetime.now(KST)
            curr = now.time()
            
            schedules = {}
            if exam_type == "☀️ 전교시 자동 진행 (1~4교시 전체)":
                schedules = {
                    dtime(8, 25): "01 0825 1교시 예비령.mp3", dtime(8, 35): "02 0835 1교시 준비령.mp3", dtime(8, 40): "03 0840 1교시 본령.mp3", dtime(10, 0): "04 1000 1교시 종료령.mp3",
                    dtime(10, 20): "05 1020 2교시 예비령.mp3", dtime(10, 25): "06 1025 2교시 준비령.mp3", dtime(10, 30): "07 1030 2교시 본령.mp3", dtime(12, 10): "08 1210 2교시 종료령.mp3",
                    dtime(13, 0): "09 1300 3교시 예비령.mp3", 
                    dtime(13, 10): selected_english_file,  # 🌟 13시 10분, 사용자가 넣은 파일 재생!
                    dtime(14, 20): "11 1420 3교시 종료령.mp3",
                    dtime(14, 40): "12 1440 4교시 한국사 예비령.mp3", dtime(14, 45): "13 1445 4교시 한국사 준비령.mp3", dtime(14, 50): "14 1450 4교시 한국사 본령.mp3", dtime(15, 20): "15 1520 4교시 한국사 종료령.mp3",
                    dtime(15, 25): "16 1525 4교시 탐구 준비령.mp3", dtime(15, 35): "17 1535 4교시 탐구 첫째본령.mp3", dtime(16, 5): "18 1605 4교시 탐구 첫째종료령.mp3",
                    dtime(16, 7): "19 1607 4교시 탐구 둘째본령.mp3", dtime(16, 37): "20 1637 4교시 탐구 둘째종료령.mp3"
                }
            elif exam_type == "1교시 국어":
                schedules = {dtime(8, 25): "01 0825 1교시 예비령.mp3", dtime(8, 35): "02 0835 1교시 준비령.mp3", dtime(8, 40): "03 0840 1교시 본령.mp3", dtime(10, 0): "04 1000 1교시 종료령.mp3"}
            elif exam_type == "2교시 수학":
                schedules = {dtime(10, 20): "05 1020 2교시 예비령.mp3", dtime(10, 25): "06 1025 2교시 준비령.mp3", dtime(10, 30): "07 1030 2교시 본령.mp3", dtime(12, 10): "08 1210 2교시 종료령.mp3"}
            elif exam_type == "3교시 영어 (듣기 자동포함)":
                schedules = {
                    dtime(13, 0): "09 1300 3교시 예비령.mp3", 
                    dtime(13, 10): selected_english_file,  # 🌟 여기도 13시 10분 반영
                    dtime(14, 20): "11 1420 3교시 종료령.mp3"
                }
            elif exam_type == "4교시 한국사/탐구 (연속진행)":
                schedules = {
                    dtime(14, 40): "12 1440 4교시 한국사 예비령.mp3", dtime(14, 45): "13 1445 4교시 한국사 준비령.mp3", dtime(14, 50): "14 1450 4교시 한국사 본령.mp3", dtime(15, 20): "15 1520 4교시 한국사 종료령.mp3",
                    dtime(15, 25): "16 1525 4교시 탐구 준비령.mp3", dtime(15, 35): "17 1535 4교시 탐구 첫째본령.mp3", dtime(16, 5): "18 1605 4교시 탐구 첫째종료령.mp3",
                    dtime(16, 7): "19 1607 4교시 탐구 둘째본령.mp3", dtime(16, 37): "20 1637 4교시 탐구 둘째종료령.mp3"
                }

            clock_spot.markdown(f"""
            <div style='text-align: center; border: 2px solid #4B79A1; padding: 15px; border-radius: 10px; background-color: #F0F4F8;'>
                <p style='margin: 0; color: #555; font-weight: bold;'>{exam_type} - 현재 서울 표준시</p>
                <h1 style='margin: 0; font-size: 55px; color: #4B79A1;'>{now.strftime('%H:%M:%S')}</h1>
            </div>
            """, unsafe_allow_html=True)

            for target_time, file_name in schedules.items():
                if curr.hour == target_time.hour and curr.minute == target_time.minute:
                    if file_name not in st.session_state.fired:
                        st.session_state.fired.append(file_name)
                        with audio_spot:
                            st.audio(f"sounds/{file_name}", autoplay=True)
            
            upcoming = [t for t in schedules.keys() if curr < t]
            if upcoming:
                next_time = min(upcoming)
                next_file = schedules[next_time]
                display_name = " ".join(next_file.split(' ')[2:]).replace('.mp3', '')
                next_dt = KST.localize(datetime.combine(now.date(), next_time))
                rem_secs = int((next_dt - now).total_seconds())
                mins, secs = divmod(rem_secs, 60)
                status_spot.info(f"⏳ 다음 방송 예정: **{display_name}** ({mins}분 {secs}초 남음)")
            else:
                status_spot.markdown("<h1 style='text-align: center; color: red; white-space: nowrap;'>🚨 모든 시험 일정이 종료되었습니다 🚨</h1>", unsafe_allow_html=True)
                st.session_state.run = False
                break

        time.sleep(1)
