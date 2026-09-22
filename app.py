import streamlit as st
import time
import json
import os

# 페이지 기본 설정
st.set_page_config(page_title="FocusNote - 학습 & 오답노트", page_icon="⏱️", layout="wide")

# ---------------------------------------------------------
# [세션 상태(Session State) 초기화] - 페이지 이동 시 데이터 유지
# ---------------------------------------------------------
if "notes" not in st.session_state:
    st.session_state.notes = []

if "timer_running" not in st.session_state:
    st.session_state.timer_running = False

if "time_left" not in st.session_state:
    st.session_state.time_left = 25 * 60  # 기본 25분 (초 단위)

# ---------------------------------------------------------
# [사이드바 메뉴] - 2개 이상의 페이지 전환 구현
# ---------------------------------------------------------
st.sidebar.title("📌 FocusNote 메뉴")
page = st.sidebar.radio(
    "이동할 페이지를 선택하세요:",
    ["1️⃣ 메인 학습 (뽀모도로 타이머 & 오답 등록)", "2️⃣ 오답 복습 퀴즈 시스템", "3️⃣ 학습 통계 및 목록"]
)

# =========================================================
# PAGE 1: 메인 학습 (뽀모도로 타이머 & 오답 등록)
# =========================================================
if page == "1️⃣ 메인 학습 (뽀모도로 타이머 & 오답 등록)":
    st.title("⏱️ 뽀모도로 타이머 & 오답 등록 시스템")
    st.caption("집중 타이머를 가동하고, 틀린 문제를 빠르게 정리하세요.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("⏱️ 뽀모도로 타이머")
        
        # 분:초 형식으로 표시
        mins, secs = divmod(st.session_state.time_left, 60)
        timer_text = f"{mins:02d}:{secs:02d}"
        st.markdown(f"# ⏳ `{timer_text}`")
        
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        
        if btn_col1.button("▶️ 시작"):
            st.session_state.timer_running = True
            
        if btn_col2.button("⏸️ 일시정지"):
            st.session_state.timer_running = False
            
        if btn_col3.button("🔄 리셋"):
            st.session_state.timer_running = False
            st.session_state.time_left = 25 * 60
            st.rerun()

        # 타이머 카운트다운 로직
        if st.session_state.timer_running and st.session_state.time_left > 0:
            time.sleep(1)
            st.session_state.time_left -= 1
            st.rerun()
        elif st.session_state.time_left == 0:
            st.success("🎉 축하합니다! 뽀모도로 1세션 완료! 휴식을 취하세요.")
            st.session_state.timer_running = False

    with col2:
        st.subheader("📝 오답 / 단어 즉시 등록")
        with st.form("note_form", clear_on_submit=True):
            subject = st.selectbox("과목 선택", ["영어", "수학", "국어", "탐구/기타"])
            question = st.text_area("문제 또는 복습할 단어 입력")
            answer = st.text_input("정답 입력")
            explanation = st.text_area("해설 또는 오답 이유 메모")
            
            submit_btn = st.form_submit_button("💾 오답노트에 저장")
            
            if submit_btn:
                if question and answer:
                    new_note = {
                        "subject": subject,
                        "question": question,
                        "answer": answer,
                        "explanation": explanation
                    }
                    st.session_state.notes.append(new_note)
                    st.success("✅ 성공적으로 오답 데이터가 저장되었습니다!")
                else:
                    st.error("⚠️ 문제와 정답을 모두 입력해주세요.")

# =========================================================
# PAGE 2: 오답 복습 퀴즈 시스템
# =========================================================
elif page == "2️⃣ 오답 복습 퀴즈 시스템":
    st.title("🎯 맞춤 오답 복습 퀴즈 화면")
    st.caption("등록된 오답 데이터를 바탕으로 퀴즈 시스템 화면이 작동합니다.")
    
    if not st.session_state.notes:
        st.warning("등록된 오답이 없습니다. '메인 학습' 페이지에서 오답을 먼저 추가해주세요!")
    else:
        subjects = list(set([n["subject"] for n in st.session_state.notes]))
        selected_sub = st.selectbox("복습할 과목 선택", ["전체"] + subjects)
        
        filtered_notes = st.session_state.notes
        if selected_sub != "전체":
            filtered_notes = [n for n in st.session_state.notes if n["subject"] == selected_sub]
            
        st.write(f"📊 총 **{len(filtered_notes)}**개의 복습 카드가 있습니다.")
        
        for idx, item in enumerate(filtered_notes, 1):
            with st.expander(f"Q{idx}. [{item['subject']}] {item['question']}"):
                user_ans = st.text_input(f"정답 작성 (문제 {idx})", key=f"ans_{idx}")
                if st.button(f"정답 확인 ({idx})", key=f"btn_{idx}"):
                    if user_ans.strip().lower() == item["answer"].strip().lower():
                        st.balloons()
                        st.success("⭕ 정답입니다!")
                    else:
                        st.error(f"❌ 틀렸습니다. 정답: {item['answer']}")
                    st.info(f"💡 해설: {item['explanation']}")

# =========================================================
# PAGE 3: 학습 통계 및 오답 목록
# =========================================================
elif page == "3️⃣ 학습 통계 및 목록":
    st.title("📊 학습 현황 및 전체 오답 목록")
    
    st.metric(label="총 등록된 오답 수", value=f"{len(st.session_state.notes)} 개")
    
    if st.session_state.notes:
        st.subheader("📋 전체 오답 데이터 표")
        st.dataframe(st.session_state.notes, use_container_width=True)
    else:
        st.info("아직 저장된 오답 목록이 없습니다.")
