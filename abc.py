import streamlit as st
import io
import random
from datetime import datetime, date
from gtts import gTTS 
from modules.lexi_ai import get_word_info
import baitap


# ================= 1. CẤU HÌNH & STYLE =================
st.set_page_config(page_title="Lexi AI - Super Hero", layout="wide")

TIPS = [
    "💡 Đừng chỉ học từ đơn, hãy học cả cụm (Collocations)!",
    "💡 Dùng từ nối (Linking words) để tăng điểm Cohesion.",
    "💡 Luyện nghe 15 phút mỗi ngày giúp tăng phản xạ.",
    "💡 Paraphrase là chìa khóa để đạt điểm Writing cao."
    "💡 Học từ qua ngữ cảnh sẽ nhớ lâu hơn là học riêng lẻ."
]

st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .header-container {
        display: flex; align-items: center; justify-content: space-between;
        background: white; padding: 15px 25px; border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 25px;
    }
    .side-card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
    .recent-tag { display: inline-block; background: #E2E8F0; padding: 5px 12px; border-radius: 20px; margin: 3px; font-size: 13px; }
    .mochi-card { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
    .info-item { background: #F8FAFC; padding: 10px; border-radius: 10px; border-left: 4px solid #FFB300; margin-bottom: 8px; }
    .locked-box { text-align: center; padding: 80px; background: #F1F5F9; border-radius: 20px; border: 2px dashed #CBD5E1; }
</style>
""", unsafe_allow_html=True)

# ================= 2. QUẢN LÝ DỮ LIỆU =================
if "word_bank" not in st.session_state: st.session_state.word_bank = []
if "streak" not in st.session_state: st.session_state.streak = 0
if "last_date" not in st.session_state: st.session_state.last_date = None
if "start_time" not in st.session_state: st.session_state.start_time = datetime.now()
if "quiz_data" not in st.session_state: st.session_state.quiz_data = None
if "current_quiz" not in st.session_state: st.session_state.current_quiz = None
if "xp" not in st.session_state: st.session_state.xp = 0

word_count = len(st.session_state.word_bank)

# Xếp hạng dựa trên số lượng từ đã lưu
if word_count <= 10: rank, r_color = " Tập sự 👶", "#94A3B8"
elif word_count <= 30: rank, r_color = "Chiến binh ⚔️", "#3B82F6"
elif word_count <= 60: rank, r_color = "Bậc thầy 🧠", "#8B5CF6"
else: rank, r_color = "Huyền thoại 👑", "#F59E0B"

def update_streak():
    today = date.today()
    if st.session_state.last_date != today:
        if st.session_state.last_date == today - date.resolution:
            st.session_state.streak += 1
        else:
            st.session_state.streak = 1
        st.session_state.last_date = today

# ================= 3. SIDEBAR =================
with st.sidebar:
    st.markdown('<div style="text-align:center"><span style="font-size:70px;">🦸‍♂️</span></div>', unsafe_allow_html=True)
    st.title("LEXI DASHBOARD")
    st.progress(min(word_count/80, 1.0))
    st.caption(f"Tiến độ: {word_count}/80 từ")
    page = st.radio("Chế độ:", ["🔍 Tra từ", "📖 Reading", "✍️ Writing", "🧠 Quiz", "🌐Interpreter"])
    st.divider()
    if st.button("🗑️ Xóa lịch sử"):
        st.session_state.word_bank = []
        st.session_state.streak = 0
        st.session_state.quiz_data = None
        st.session_state.current_quiz = None
        st.rerun()

# ================= 4. HEADER =================
dur = (datetime.now() - st.session_state.start_time).seconds // 60
st.markdown(f"""
<div class="header-container">
    <div style="display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 30px;">🦸‍♂️</span>
        <b style="font-size: 18px;">LEXI AI </b>
    </div>
    <div style="display: flex; gap: 20px; align-items: center;">
        <div style="text-align:right"><small>Phiên học</small><br><b>{dur} phút</b></div>
         <div class="xp-badge">✨ {st.session_state.xp} XP</div>
        <div style="background: linear-gradient(135deg, #FF9800, #F44336); color: white; padding: 8px 18px; border-radius: 12px; font-weight: bold;">
            🔥 STREAK: {st.session_state.streak} NGÀY
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ================= 5. NỘI DUNG CHÍNH =================
if page == "🔍 Tra từ":
    main_col, side_col = st.columns([8, 3])

    with main_col:
        word_input = st.text_input("Nhập từ vựng:", placeholder="Ví dụ: Resilience, Sustainable...", label_visibility="collapsed")
        
        if word_input:
            with st.spinner("Siêu nhân Lexi đang phân tích..."):
                data = get_word_info(word_input)
            
            if "error" not in data:
                st.markdown('<div class="mochi-card">', unsafe_allow_html=True)
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"<h2 style='color:#FFB300; margin:0;'>{word_input.upper()}</h2>", unsafe_allow_html=True)
                    st.write(f"/{data.get('phonetic')}/ • {data.get('word_class')}")
                with c2:
                    if st.button("🔊 Nghe"):
                        tts = gTTS(text=word_input, lang='en')
                        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
                        st.audio(fp, format='audio/mp3', autoplay=True)
                
                st.divider()
                t1, t2, t3, t4 = st.tabs(["🎯 Collocations", "💡 Idioms", "👪 Word Forms", "📖 Examples & Expand "])
                with t1:
                    cols = st.columns(2)
                    for i, it in enumerate(data.get('collocations', [])):
                        en, vi = it.split(":", 1) if ":" in it else (it, "")
                        cols[i%2].markdown(f'<div class="info-item"><b>{en}</b><br><small>{vi}</small></div>', unsafe_allow_html=True)
                with t3:
                    wf = data.get('word_forms', {})
                    wf_cols = st.columns(4)
                    types = [("Noun", "noun", "#2563EB"), ("Verb", "verb", "#DC2626"), ("Adj", "adj", "#EA580C"), ("Adv", "adv", "#7C3AED")]
                    for i, (lab, key, color) in enumerate(types):
                        val = wf.get(key, "- : -")
                        en_f, vi_f = val.split(":", 1) if ":" in val else (val, "-")
                        wf_cols[i].markdown(f'<div style="border-top:3px solid {color}; padding:8px; background:#F8FAFC; border-radius:10px; text-align:center;"><small style="color:{color}; font-weight:bold;">{lab}</small><br><b>{en_f}</b><br><small>{vi_f}</small></div>', unsafe_allow_html=True)
                with t4:
                    st.info(f"💡 Sắc thái: {data.get('nuance')}")
                    for ex in data.get('examples', []):
                        st.write(f"🔹 {ex}")

                if st.button("💾 Lưu từ & Tăng Streak"):
                    if word_input not in st.session_state.word_bank:
                        st.session_state.word_bank.append(word_input)
                        update_streak()
                        st.balloons()
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("👆 Nhập một từ vựng bất kỳ ở trên để bắt đầu khám phá!")
            st.image("https://img.freepik.com/free-vector/creative-thinking-concept-illustration_114360-3851.jpg", width=500)

    with side_col:
        st.markdown('<div class="side-card"><h5>💡 IELTS Tip</h5>' + random.choice(TIPS) + '</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="side-card"><h5>📊 Thống kê</h5>• Từ đã lưu: <b>{word_count}</b><br>• Cấp độ: <b>{"Grit Newbie" if word_count < 20 else "Grit Warrior"}</b></div>', unsafe_allow_html=True)
        if st.session_state.word_bank:
            st.markdown('<div class="side-card"><h5>🕒 Vừa lưu</h5>' + "".join([f'<span class="recent-tag">{w}</span>' for w in st.session_state.word_bank[-6:]]) + '</div>', unsafe_allow_html=True)

elif page == "🧠 Quiz":
    if word_count < 4:
        st.markdown(f'<div class="locked-box"><h1 style="font-size:80px;">⚠️</h1><h2>CHƯA ĐỦ TỪ ĐỂ TẠO BÀI TẬP</h2><p>Cần thêm <b>{4-word_count}</b> từ nữa để mở Quiz.</p></div>', unsafe_allow_html=True)
    else:
        # Thanh tiến độ XP trong trang ôn tập
        st.markdown("##### ⚡ Năng lượng học tập (XP)")
        st.progress(min(st.session_state.xp / 500, 1.0))
        
        tab1, tab2, tab3 = st.tabs(["🎴 Flashcard", "🎯 Trắc nghiệm", "⚡ Đúng/Sai"])

        with tab1:
            if st.button("⏭️ Đổi thẻ mới") or st.session_state.current_card is None:
                st.session_state.current_card = random.choice(st.session_state.word_bank)
            
            card = st.session_state.current_card
            st.markdown(f"""
            <div style="background: white; padding: 50px; border-radius: 20px; border: 3px solid #FFB300; text-align: center;">
                <h1 style="font-size: 60px; margin:0;">{card['word'].upper()}</h1>
                <p style="color: gray;">{card['phonetic']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("👉 NHẤN ĐỂ LẬT THẺ (XEM NGHĨA)"):
                st.markdown(f"### {card['definition_vi']}")
                if st.button("✅ Đã thuộc từ này (+5 XP)"):
                    st.session_state.xp += 5
                    st.rerun()

        with tab2:
            if st.button("🔄 Câu hỏi trắc nghiệm mới") or st.session_state.quiz_data is None:
                st.session_state.quiz_data = baitap.LexiQuiz.tao_trac_nghiem(st.session_state.word_bank)
            
            q = st.session_state.quiz_data
            if q:
                st.markdown(f"#### Nghĩa của từ **{q['word']}** là gì?")
                for opt in q['options']:
                    if st.button(opt, use_container_width=True, key=f"quiz_{opt}"):
                        if opt == q['correct_ans']:
                            st.success("🎯 Quá chuẩn Siêu nhân ơi! +10 XP")
                            st.session_state.xp += 10
                        else:
                            st.error("❌ Sai rồi, thử lại nhé!")

        with tab3:
            st.write("⚡ Phản xạ nhanh: Đúng hay Sai?")
            ds = baitap.LexiQuiz.tao_dung_sai(st.session_state.word_bank)
            if ds:
                st.markdown(f"""
                <div style="background: #F1F5F9; padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 20px;">
                    <h3>{ds['word']}  =  {ds['display_def']}</h3>
                </div>
                """, unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                if c1.button("✅ ĐÚNG", use_container_width=True):
                    if ds['is_correct']: st.success("Chuẩn! +5 XP"); st.session_state.xp += 5
                    else: st.error("Sai rồi!")
                if c2.button("❌ SAI", use_container_width=True):
                    if not ds['is_correct']: st.success("Chính xác! +5 XP"); st.session_state.xp += 5
                    else: st.error("Sai rồi!")

elif page == "📖 Reading":
    if word_count < 20:
        st.markdown(f'<div class="locked-box"><h1 style="font-size:80px;">🔒</h1><h2>TÍNH NĂNG CHƯA KÍCH HOẠT</h2><p>Cần thêm <b>{20-word_count}</b> từ nữa để mở Reading.</p></div>', unsafe_allow_html=True)
    else:
        st.success("✅ Bạn đã đủ Grit! Bắt đầu luyện Reading thôi.")
elif page == "✍️ Writing":
    if word_count < 40:
        st.markdown(f'<div class="locked-box"><h1 style="font-size:80px;">🛡️</h1><h2>TÍNH NĂNG CHƯA KÍCH HOẠT</h2><p>Cần thêm <b>{40-word_count}</b> từ nữa để mở Writing.</p></div>', unsafe_allow_html=True)
    else:
        st.success("✅ Bạn đã đủ Grit! Bắt đầu luyện Writing thôi.")
elif page == "🌐Interpreter":
    if word_count < 80:
        st.markdown(f'<div class="locked-box"><h1 style="font-size:80px;">🌐</h1><h2>TÍNH NĂNG CHƯA KÍCH HOẠT</h2><p>Cần thêm <b>{80-word_count}</b> từ nữa để mở Interpreter.</p></div>', unsafe_allow_html=True)
    else:
        st.success("✅ Bạn đã đủ Grit! Bắt đầu luyện tập về việc dịch thuật thôi.")