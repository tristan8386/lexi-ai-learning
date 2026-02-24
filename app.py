import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from modules import lexi_ai
import random

# Cấu hình UI
st.set_page_config(page_title="Lexi AI - Elite Learning", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .example-box { background-color: #1e2130; padding: 15px; border-left: 5px solid #4f8bf9; border-radius: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Khởi tạo dữ liệu
if 'word_bank' not in st.session_state: st.session_state.word_bank = []
if 'quiz_data' not in st.session_state: st.session_state.quiz_data = None

# SIDEBAR
with st.sidebar:
    st.title("🏆 My Progress")
    word_count = len(st.session_state.word_bank)
    st.progress(min(word_count / 80, 1.0), text=f"Vốn từ: {word_count}/80")
    st.divider()
    st.subheader("🔓 Hệ thống mở khóa")
    if word_count >= 20: st.success("📖 Reading: OPEN")
    else: st.info(f"🔒 20 từ: Reading (Cần {20-word_count})")
    if word_count >= 40: st.success("✍️ Writing: OPEN")
    else: st.info(f"🔒 40 từ: Writing (Cần {40-word_count})")

# GIAO DIỆN TRA TỪ
st.title("🤖 LEXI AI: SMART DICTIONARY")
search_query = st.text_input("Tra từ thông minh:", placeholder="Nhập từ...")

if search_query:
    with st.spinner("Đang phân tích..."):
        data = lexi_ai.get_word_info(search_query)
        
        if isinstance(data, dict):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.header(f"{search_query.upper()} [/{data.get('phonetic','')}/]")
            with c2:
                if st.button("⭐ Thêm vào Word Bank"):
                    if not any(d['Word'].lower() == search_query.lower() for d in st.session_state.word_bank):
                        st.session_state.word_bank.append({
                            "Word": search_query, "Meaning": data['definition'],
                            "Wrong": 0, "Correct": 0, "Date": datetime.now().strftime("%Y-%m-%d")
                        })
                        st.toast("Đã lưu!")

            t1, t2, t3 = st.tabs(["🎯 Định nghĩa", "🔗 Mở rộng", "💡 Ví dụ ngữ cảnh"])
            with t1:
                st.info(f"**Nghĩa:** {data['definition']}")
                st.write(f"**Gốc từ:** {data['etymology']}")
            with t2:
                st.write("**Collocations:**", ", ".join(data.get('collocations', [])))
                st.write("**Word Family:**", ", ".join(data.get('word_family', [])))
            with t3:
                st.subheader("💡 Ví dụ thực tế")
                for ex in data.get('examples', []):
                    st.markdown(f'<div class="example-box"><i>"{ex}"</i></div>', unsafe_allow_html=True)
        else:
            st.error("❌ Lỗi hiển thị")
            st.warning(data)

# PRACTICE CENTER
st.divider()
st.header("🎮 Practice Center")
p1, p2 = st.columns(2)

with p1:
    st.subheader("🧩 Trắc nghiệm")
    if len(st.session_state.word_bank) >= 4:
        def gen_quiz():
            c = random.choice(st.session_state.word_bank)
            w = random.sample([d for d in st.session_state.word_bank if d['Word']!=c['Word']], 3)
            opts = [c['Meaning']] + [i['Meaning'] for i in w]
            random.shuffle(opts)
            return {"word": c['Word'], "ans": c['Meaning'], "opts": opts}
        if st.button("Câu hỏi mới") or st.session_state.quiz_data is None:
            st.session_state.quiz_data = gen_quiz()
        q = st.session_state.quiz_data
        choice = st.radio(f"Nghĩa của {q['word'].upper()}:", q['opts'], index=None)
        if st.button("Kiểm tra"):
            if choice == q['ans']: st.success("Đúng!"); 
            else: st.error("Sai!")
            st.session_state.quiz_data = None
            st.rerun()
    else: st.info("Cần 4 từ để mở trắc nghiệm.")

with p2:
    st.subheader("✍️ Luyện viết")
    if word_count >= 40:
        target = st.selectbox("Chọn từ:", [d['Word'] for d in st.session_state.word_bank])
        sent = st.text_area("Viết câu:")
        if st.button("Chấm điểm"):
            res = lexi_ai.check_writing(sent, target)
            st.info(res['feedback'])
    else: st.warning(f"Cần 40 từ (Hiện tại: {word_count}/40)")