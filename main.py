import streamlit as st
from datetime import datetime, time as dtime, timedelta
import pytz
import time

# 1. 페이지 설정 및 서울 타임존 고정
st.set_page_config(page_title="수능형 사내 시험 타이머", layout="centered")
KST = pytz.timezone('Asia/Seoul')

st.title("⏱️ 수능 실전형 자동 시험 타이머")
st.caption("※ 실제 수능 시간표 및 종소리 파일과 연동하여 작동합니다 (sounds/ 폴더 기준).")

# 전체 20개 파일 목록 정의 (sounds/ 폴더 안에 있다고 가정)
ALL_AUDIO_FILES = [
    "01 0825 1교시 예비령.mp3", "02 0835 1교시 준비령.mp3", "03 0840 1교시 본령.mp3", "04 1000 1교시 종료령.mp3",
    "05 1020 2교시 예비령.mp3", "06 1025 2교시 준비령.mp3", "07 1030 2교시 본령.mp3", "08 1210 2교시 종료령.mp3",
    "09 1300 3교시 예비령.mp3", "10 1307 3교시 영어듣기.mp3", "11 1420 3교시 종료령.mp3",
    "12 1440 4교시 한국사 예비령.mp3", "13 1445 4교시 한국사 준비령.mp3", "14 1450 4교시 한국사 본령.mp3", "15 1520 4교시 한국사 종료령.mp3",
    "16 1525 4교시 탐구 준비령.mp3", "17 1535 4교시 탐구 첫째본령.mp3", "18 1605 4교시 탐구 첫째종료령.mp3", "19 1607 4교시 탐구 둘째본령.mp3", "20 1637 4교시 탐구 둘째종료령.mp3"
]

# 2. 시험 과목 및 테스트 선택 드롭다운
exam_type = st.selectbox(
    "진행할 항목을 선택하세요:", 
    [
        "1교시 국어", 
        "2교시 수학", 
        "3교시 영어 (듣기 자동포함)", 
        "4교시 한국사/탐구 (연속진행)", 
        "🔥 종합 종소리 테스트 (10초 간격 순차재생)"
    ]
)

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
        st.session_state.start_time = time.time()  # 테스트 모드용 시작 시간 기록
        st.rerun()
else:
    if st.button("⏹️ 타이머 중지 및 초기화", use_container_width=True):
        st.session_state.run = False
        st.session_state.fired = []
        st.session_state.start_time = None
        st.rerun()

st.markdown("---")

# 5. 실시간 감시 및 재생 루프
if st.session_state.run:
    clock_spot = st.empty()
    status_spot = st.empty()
    audio_spot = st.empty()

    while st.session_state.run:
        # ------------------------------------------------------------------
        # [A] 🔥 종합 종소리 테스트 모드 (10초 간격 순차 재생) 로직
        # ------------------------------------------------------------------
        if exam_type == "🔥 종합 종소리 테스트 (10초 간격 순차재생)":
            elapsed = int(time.time() - st.session_state.start_time)
            idx = elapsed // 10  # 10초마다 인덱스 1씩 증가
            
            # 20개 파일을 다 돌았으면 종료
            if idx >= len(ALL_AUDIO_FILES):
                status_spot.success("🎉 모든 종소리 파일 파일 테스트가 완료되었습니다!")
                st.balloons()
                st.session_state.run = False
                break
                
            current_file = ALL_AUDIO_FILES[idx]
            countdown = 10 - (elapsed % 10)
            
            # 화면 표시
            clock_spot.markdown(f"""
            <div style='text-align: center; border: 2px solid #FF4B4B; padding: 15px; border-radius: 10px; background-color: #FFF0F0;'>
                <p style='margin: 0; color: #FF4B4B; font-weight: bold;'>🚨 전체 종소리 기능 테스트 중 ({idx + 1} / {len(ALL_AUDIO_FILES)})</p>
                <h2 style='margin: 10px 0; color: #333;'>{current_file}</h2>
                <p style='margin: 0; color: #555;'>다음 파일 재생까지 <b>{countdown}초</b> 남음</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 10초가 되는 시점에 한 번만 음원 재생 리드
            if current_file not in st.session_state.fired:
                st.session_state.fired.append(current_file)
                with audio_spot:
                    # sounds/ 폴더 내 파일 자동 재생 (Streamlit 1.36+ 기능)
                    st.audio(f"sounds/{current_file}", autoplay=True)

        # ------------------------------------------------------------------
        # [B] ⏰ 실제 교시별 수능 시험 모드 로직
        # ------------------------------------------------------------------
        else:
            now = datetime.now(KST)
            curr = now.time()
            
            # 교시별 타임라인 스케줄 매핑
            schedules = {}
            if exam_type == "1교시 국어":
                schedules = {
                    dtime(8, 25): "01 0825 1교시 예비령.mp3",
                    dtime(8, 35): "02 0835 1교시 준비령.mp3",
                    dtime(8, 40): "03 0840 1교시 본령.mp3",
                    dtime(10, 0): "04 1000 1교시 종료령.mp3"
                }
            elif exam_type == "2교시 수학":
                schedules = {
                    dtime(10, 20): "05 1020 2교시 예비령.mp3",
                    dtime(10, 25): "06 1025 2교시 준비령.mp3",
                    dtime(10, 30): "07 1030 2교시 본령.mp3",
                    dtime(12, 10): "08 1210 2교시 종료령.mp3"
                }
            elif exam_type == "3교시 영어 (듣기 자동포함)":
                schedules = {
                    dtime(13, 0): "09 1300 3교시 예비령.mp3",
                    dtime(13, 7): "10 1307 3교시 영어듣기.mp3",  # 영어듣기 파일 자동 재생!
                    dtime(14, 20): "11 1420 3교시 종료령.mp3"
                }
            elif exam_type == "4교시 한국사/탐구 (연속진행)":
                schedules = {
                    dtime(14, 40): "12 1440 4교시 한국사 예비령.mp3",
                    dtime(14, 45): "13 1445 4교시 한국사 준비령.mp3",
                    dtime(14, 50): "14 1450 4교시 한국사 본령.mp3",
                    dtime(15, 20): "15 1520 4교시 한국사 종료령.mp3",
                    dtime(15, 25): "16 1525 4교시 탐구 준비령.mp3",
                    dtime(15, 35): "17 1535 4교시 탐구 첫째본령.mp3",
                    dtime(16, 5): "18 1605 4교시 탐구 첫째종료령.mp3",
                    dtime(16, 7): "19 1607 4교시 탐구 둘째본령.mp3",
                    dtime(16, 37): "20 1637 4교시 탐구 둘째종료령.mp3"
                }

            # 현재 시간 시계 노출
            clock_spot.markdown(f"""
            <div style='text-align: center; border: 2px solid #4B79A1; padding: 15px; border-radius: 10px; background-color: #F0F4F8;'>
                <p style='margin: 0; color: #555; font-weight: bold;'>{exam_type} - 현재 서울 표준시</p>
                <h1 style='margin: 0; font-size: 55px; color: #4B79A1;'>{now.strftime('%H:%M:%S')}</h1>
            </div>
            """, unsafe_allow_html=True)

            # 타임라인 체크 및 알람 재생
            fired_any = False
            for target_time, file_name in schedules.items():
                # 정각 분/초가 되었을 때 재생
                if curr.hour == target_time.hour and curr.minute == target_time.minute:
                    if file_name not in st.session_state.fired:
                        st.session_state.fired.append(file_name)
                        with audio_spot:
                            st.audio(f"sounds/{file_name}", autoplay=True)
            
            # 상태 메시지 관리 (현재 진행 중인 상태 파악용)
            upcoming = [t for t in schedules.keys() if curr < t]
            if upcoming:
                next_time = min(upcoming)
                next_file = schedules[next_time]
                next_dt = KST.localize(datetime.combine(now.date(), next_time))
                rem_secs = int((next_dt - now).total_seconds())
                mins, secs = divmod(rem_secs, 60)
                status_spot.info(f"⏳ 다음 방송 예정: **{next_file.split(' ')[2]}** ({mins}분 {secs}초 남음)")
            else:
                # 모든 일정이 끝난 경우
                status_spot.markdown("<h1 style='text-align: center; color: red;'>🚨 해당 교시 시험 종료 🚨</h1>", unsafe_allow_html=True)
                st.balloons()
                st.session_state.run = False
                break

        time.sleep(1)
