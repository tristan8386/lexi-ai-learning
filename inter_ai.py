import streamlit as st
import google.generativeai as genai
import random
from datetime import datetime

class InterpreterAI:
    @staticmethod
    def render_ui():
        # 1. Đồng bộ hóa dữ liệu từ Word Bank trong UI.py
        # UI.py lưu dạng: st.session_state.word_bank = [{"word": "...", "definition": "..."}]
        all_words = [w['word'] for w in st.session_state.get('word_bank', [])]

        st.title("🌐 IELTS Interpreter (Hybrid Mode)")
        st.caption("Chiến thuật 50/50: Kết hợp từ bạn chọn và từ AI thử thách.")

        # Khởi tạo các biến trạng thái nếu chưa có
        if "inter_task_vn" not in st.session_state: st.session_state.inter_task_vn = None
        if "inter_result" not in st.session_state: st.session_state.inter_result = None
        if "final_keywords" not in st.session_state: st.session_state.final_keywords = []

        if not all_words:
            st.warning("⚠️ Word Bank trống! Hãy quay lại trang 'Tra từ' để tích lũy thêm.")
            return

        # 2. Giao diện chọn từ chủ động
        st.markdown("### 🎯 Bước 1: Chọn từ bạn muốn luyện tập")
        user_selected = st.multiselect(
            "Chọn các từ bạn muốn chắc chắn xuất hiện trong bài dịch:",
            options=all_words,
            help="AI sẽ tự động chọn thêm các từ khác để tạo thành bộ khung 250 chữ."
        )

        # 3. Logic Tạo đề bài (Nút bấm)
        if st.button("✨ Tạo thử thách Hybrid (User + AI)"):
            with st.spinner("Lexi AI đang thiết kế bài dịch..."):
                # Lấy danh sách từ AI sẽ chọn thêm (những từ User KHÔNG chọn)
                remaining_pool = [w for w in all_words if w not in user_selected]
                
                # AI chọn thêm tối thiểu 3 từ, tối đa bằng số lượng user chọn
                num_to_pick = max(len(user_selected), 3)
                ai_selected = random.sample(remaining_pool, min(len(remaining_pool), num_to_pick))
                
                # Gộp danh sách cuối cùng
                st.session_state.final_keywords = list(set(user_selected + ai_selected))
                
                # Gọi Model (Đã được configure ở UI.py nên không cần gọi lại genai.configure)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Bạn là chuyên gia IELTS. Hãy soạn một đoạn văn nghị luận Tiếng Việt (khoảng 250 chữ).
                Chủ đề: Một vấn đề thực tế trong IELTS (Education, Technology, Health, or Environment).
                YÊU CẦU BẮT BUỘC: Khi dịch đoạn văn này sang tiếng Anh, người dịch phải sử dụng các từ sau: {st.session_state.final_keywords}.
                Hãy viết đoạn văn Tiếng Việt sao cho ngữ cảnh ép người dịch phải dùng đúng các từ đó.
                """
                
                try:
                    response = model.generate_content(prompt)
                    st.session_state.inter_task_vn = response.text
                    st.session_state.inter_result = None # Xóa kết quả chấm điểm cũ
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi kết nối AI: {e}")

        # 4. Khu vực hiển thị đề và Nhập bài dịch
        if st.session_state.inter_task_vn:
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🇻🇳 Bản gốc Tiếng Việt")
                st.info(st.session_state.inter_task_vn)
                st.write(f"🔑 **Từ bạn chọn:** `{', '.join(user_selected) if user_selected else 'Trống'}`")
                ai_only = [w for w in st.session_state.final_keywords if w not in user_selected]
                st.write(f"🤖 **AI thách thức thêm:** `{', '.join(ai_only)}`")
            
            with col2:
                st.markdown("### 🇬🇧 Bản dịch của bạn")
                user_trans = st.text_area("Nhập bản dịch tiếng Anh của bạn tại đây:", height=400)
                
                if st.button("🚀 Chấm điểm & Phân tích"):
                    if len(user_trans.split()) < 10:
                        st.warning("Vui lòng hoàn thành bài dịch trước khi chấm!")
                    else:
                        with st.spinner("Giám khảo đang phân tích bản dịch..."):
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            check_prompt = f"""
                            Phân tích bản dịch sau dựa trên đoạn gốc VN.
                            GỐC (VN): {st.session_state.inter_task_vn}
                            BẢN DỊCH (EN): {user_trans}
                            TỪ KHÓA BẮT BUỘC: {st.session_state.final_keywords}
                            
                            YÊU CẦU:
                            1. Điểm chính xác (0-100%).
                            2. Kiểm tra Checklist từ khóa: Liệt kê từ nào đã dùng, từ nào chưa dùng.
                            3. Chỉ ra lỗi sai và sửa lỗi theo định dạng [SAI]/[SỬA].
                            4. Gợi ý bản dịch mẫu chuyên nghiệp Band 8.0+.
                            """
                            st.session_state.inter_result = model.generate_content(check_prompt).text
                            st.session_state.user_trans_saved = user_trans
                            st.session_state.xp += 100 # Cộng 100 XP cho sự nỗ lực (Grit)
                            st.balloons()
                            st.rerun()

        # 5. Hiển thị kết quả và Nút Download
        if st.session_state.inter_result:
            st.markdown("---")
            st.markdown("### 📊 Phân tích chi tiết từ Lexi AI")
            st.markdown(st.session_state.inter_result)
            
            # Tạo nội dung file báo cáo
            report_text = f"""
LEXI AI - INTERPRETER REPORT
-------------------------------------------------
Từ khóa thử thách: {st.session_state.final_keywords}

BẢN GỐC (VN):
{st.session_state.inter_task_vn}

BẢN DỊCH CỦA BẠN (EN):
{st.session_state.user_trans_saved}

NHẬN XÉT CHI TIẾT:
{st.session_state.inter_result}
-------------------------------------------------
            """
            st.download_button(
                label="📥 Tải bài dịch & Nhận xét (.txt)",
                data=report_text,
                file_name=f"Interpreter_{datetime.now().strftime('%d%m_%H%M')}.txt",
                mime="text/plain"
            )