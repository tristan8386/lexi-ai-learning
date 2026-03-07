import streamlit as st
import google.generativeai as genai
import random
from datetime import datetime

class WritingAI:
    @staticmethod
    def generate_task(word_bank):
        seeds = random.sample([w['word'] for w in word_bank], min(len(word_bank), 5))
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Role: IELTS Examiner. Task: Create an IELTS Writing Task 2 prompt about: {seeds}. English only."
        return model.generate_content(prompt).text

    @staticmethod
    def render_ui():
        st.title("✍️ IELTS Writing Expert")
        
        if "current_task" not in st.session_state:
            st.session_state.current_task = "Nhấn nút bên dưới để nhận đề bài."
        
        st.info(f"**ĐỀ BÀI:** {st.session_state.current_task}")
        if st.button("🆕 Đổi đề bài"):
            st.session_state.current_task = WritingAI.generate_task(st.session_state.word_bank)
            st.rerun()

        user_essay = st.text_area("Bản thảo (Ít nhất 250 từ):", height=300)
        
        if st.button("🚀 Chấm điểm & Nâng cấp"):
            with st.spinner("Đang phân tích đa tầng..."):
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                Bạn là giám khảo IELTS. Hãy phân tích bài viết này:
                ĐỀ BÀI: {st.session_state.current_task}
                BÀI LÀM: {user_essay}

                YÊU CẦU PHẢN HỒI (Tiếng Việt):
                1. Đánh giá điểm (0-9) cho 4 tiêu chí.
                2. Liệt kê các lỗi sai theo cấu trúc: [SAI]: câu gốc | [SỬA]: câu đúng | [LÝ DO]: tại sao sai.
                3. Nâng cấp lũy tiến 2 câu: 6.5 -> 7.0 -> 7.5+.
                4. Bài mẫu hoàn hảo Band 8.0+.
                """
                st.session_state.last_feedback = model.generate_content(prompt).text

        if "last_feedback" in st.session_state:
            # Tách và hiển thị lỗi sai có màu sắc
            feedback = st.session_state.last_feedback
            if "[SAI]" in feedback:
                st.subheader("🔍 Soi lỗi chi tiết")
                lines = feedback.split('\n')
                for line in lines:
                    if "[SAI]" in line: st.error(line)
                    elif "[SỬA]" in line: st.success(line)
                    else: st.write(line)
            else:
                st.markdown(feedback)

            # Tính năng Tải file
            report = f"IELTS REPORT - {datetime.now()}\n\nTask: {st.session_state.current_task}\n\nEssay:\n{user_essay}\n\nFeedback:\n{feedback}"
            st.download_button("📥 Tải kết quả (.txt)", report, f"writing_{datetime.now().strftime('%d%m')}.txt")