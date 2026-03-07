import streamlit as st
import random
import json
import google.generativeai as genai

# Cấu hình API - Hai em thay KEY của mình vào đây nhé
genai.configure(api_key="GENAI_API_KEY")

class ReadingAI:
    @staticmethod
    def generate_content(word_bank):
        """Gọi Gemini AI để tạo bài đọc và câu hỏi dựa trên Word Bank"""
        if len(word_bank) < 5:
            return None
        
        # Lấy 5 từ ngẫu nhiên để làm "hạt giống" cho bài viết
        seeds = random.sample([w['word'] for w in word_bank], 10)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Bạn là chuyên gia ra đề IELTS. Dựa trên 10 từ: {seeds}, hãy viết 1 bài đọc (250 chữ) và 8 câu hỏi.
        YÊU CẦU CÂU HỎI:
        1. Main Idea: Tiêu đề bài viết.
        2. Detail: Chi tiết cụ thể trong bài.
        3. Reference: Từ 'They/It' ở đoạn X thay thế cho từ nào?
        4. Vocabulary: Tìm từ đồng nghĩa trong ngữ cảnh.
        5. Inference: Điều nào sau đây là ĐÚNG/SAI?
        6. Main Idea: Ý chính của đoạn Y.
        7. Detail: Thông tin về từ Z.
        8. Message: Ý nghĩa tổng thể của bài viết.

        TRẢ VỀ ĐỊNH DẠNG JSON NGUYÊN BẢN (KHÔNG CÓ CHỮ ```json):
        {{
          "title": "Tiêu đề",
          "content": "Nội dung bài viết (chia làm 2-3 đoạn)...",
          "questions": [
            {{"type": "Main Idea", "q": "...", "options": ["A", "B", "C", "D"], "ans": "Đáp án đúng"}},
            {{"type": "Detail", "q": "...", "options": ["A", "B", "C", "D"], "ans": "Đáp án đúng"}},
            {{"type": "Reference", "q": "...", "options": ["A", "B", "C", "D"], "ans": "Đáp án đúng"}},
            {{"type": "Vocabulary", "q": "...", "options": ["A", "B", "C", "D"], "ans": "Đáp án đúng"}},
            {{"type": "Inference", "q": "...", "options": ["A", "B", "C", "D"], "ans": "Đáp án đúng"}}
          ]
        }}
        """
        try:
            response = model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            st.error(f"Lỗi AI: {e}")
            return None

    @staticmethod
    def render_ui():
        st.title("📖 IELTS Reading Simulation (AI)")
        
        # Kiểm tra điều kiện mở khóa
        word_count = len(st.session_state.word_bank)
        if word_count < 20:
            st.warning(f"🔒 Cần 20 từ để mở khóa Reading. Bạn mới có {word_count} từ.")
            return

        # Nút tạo bài mới
        if st.button("✨ Generate New AI Passage"):
            with st.spinner("AI Lexi đang sáng tác bài đọc cho bạn..."):
                st.session_state.current_reading = ReadingAI.generate_content(st.session_state.word_bank)
                st.session_state.answers_state = {} # Lưu trạng thái đúng/sai từng câu

        # Hiển thị giao diện SONG SONG
        if "current_reading" in st.session_state and st.session_state.current_reading:
            data = st.session_state.current_reading
            
            col_left, col_right = st.columns([1.2, 1])

            # CỘT TRÁI: BÀI ĐỌC (Có thanh cuộn)
            with col_left:
                st.markdown("### 📝 Reading Passage")
                st.markdown(f"""
                <div style="background: #ffffff; padding: 25px; border-radius: 15px; border: 2px solid #e2e8f0; height: 550px; overflow-y: auto; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);">
                    <h2 style="color: #1e40af; margin-top:0;">{data['title']}</h2>
                    <p style="font-size: 17px; line-height: 1.8; color: #334155; text-align: justify;">
                        {data['content'].replace('.', '.<br><br>')} 
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # CỘT PHẢI: CÂU HỎI
            with col_right:
                st.markdown("### 🎯 Questions")
                with st.container():
                    for i, item in enumerate(data['questions']):
                        st.markdown(f"**Q{i+1}** <small style='color:gray;'>({item['type']})</small>", unsafe_allow_html=True)
                        user_choice = st.radio(item['q'], item['options'], key=f"ai_q_{i}")
                        
                        if st.button(f"Check Answer Q{i+1}", key=f"btn_{i}"):
                            if user_choice == item['ans']:
                                st.success("🎯 Correct! +10 XP")
                                if f"q{i}" not in st.session_state.answers_state:
                                    st.session_state.xp += 10
                                    st.session_state.answers_state[f"q{i}"] = True
                            else:
                                st.error(f"❌ Incorrect. Try again!")
                        st.divider()