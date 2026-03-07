import streamlit as st
import io
import random
from gtts import gTTS 
from modules.lexi_ai import get_word_info
import baitap  # Đảm bảo file baitap.py nằm cùng thư mục

# ================= 1. CẤU HÌNH & GIAO DIỆN =================
st.set_page_config(page_title="Lexi AI - Begin_6", layout="wide")

# CSS để làm đẹp giao diện, làm các thẻ card trông chuyên nghiệp hơn
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .header-container {
        display: flex; align-items: center; justify-content: space-between;
        background: white; padding: 15px 25px; border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 25px;
    }
    .mochi-card { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #E2E8F0; margin-bottom: 20px;}
    .side-card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
    .xp-badge { background: linear-gradient(135deg, #FF9800, #F44336); color: white; padding: 5px 15px; border-radius: 10px; font-weight: bold; }
    .word-item { border-bottom: 1px solid #F1F5F9; padding: 8px 0; }
</style>
""", unsafe_allow_html=True)

# ================= 2. QUẢN LÝ DỮ LIỆU =================
if "word_bank" not in st.session_state: st.session_state.word_bank = []
if "xp" not in st.session_state: st.session_state.xp = 0
if "quiz_data" not in st.session_state: st.session_state.quiz_data = None
if "current_card" not in st.session_state: st.session_state.current_card = None

word_count = len(st.session_state.word_bank)

# Tính toán danh hiệu Siêu nhân dựa trên số từ
if word_count <= 10: rank, r_color = "Tập sự 👶", "#94A3B8"
elif word_count <= 30: rank, r_color = "Chiến binh ⚔️", "#3B82F6"
elif word_count <= 60: rank, r_color = "Bậc thầy 🧠", "#8B5CF6"
else: rank, r_color = "Huyền thoại 👑", "#F59E0B"

# ================= 3. SIDEBAR =================
with st.sidebar:
    st.markdown("<h1 style='text-align:center;'>🦸‍♂️</h1>", unsafe_allow_html=True)
    st.title("LEXI DASHBOARD")
    
    # Hiển thị Hạng và Tiến độ mục tiêu
    st.markdown(f"Hạng: <b style='color:{r_color}'>{rank}</b>", unsafe_allow_html=True)
    progress_val = min(word_count / 80, 1.0)
    st.progress(progress_val)
    st.caption(f"Tiến độ: {word_count}/80 từ ({int(progress_val*100)}%)")
    
    st.divider()
    page = st.radio("Chế độ Siêu nhân:", ["🔍 Tra từ & Giải mã", "🎯 Đấu trường Ôn tập", "📖 Reading", "✍️ Writing"])

# ================= 4. HEADER =================
st.markdown(f"""
<div class="header-container">
    <div><b style="font-size: 20px; color:#1E293B;">SIÊU NHÂN LEXI</b> <small style="color:gray;">| Nhóm Begin_6</small></div>
    <div style="display: flex; gap: 15px; align-items: center;">
        <div class="xp-badge">✨ {st.session_state.xp} XP</div>
        <div style="background: #1E293B; color: white; padding: 5px 15px; border-radius: 10px; font-weight: bold;">🔥 STREAK: 5</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ================= 5. NỘI DUNG TỪNG TRANG =================

if page == "🔍 Tra từ & Giải mã":
    col_main, col_side = st.columns([7, 3])
    
    with col_main:
        word_input = st.text_input("Nhập từ vựng IELTS cần giải mã:", placeholder="Ví dụ: Resilience, Sustainable...")
        
        if word_input:
            with st.spinner("Lexi đang phân tích dữ liệu..."):
                data = get_word_info(word_input)
            
            if "error" not in data:
                # HIỂN THỊ DỊCH LUÔN Ở ĐÂY
                st.markdown(f"""
                <div class="mochi-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h2 style="color: #FFB300; margin: 0;">{word_input.upper()}</h2>
                        <span style="background: #E2E8F0; padding: 2px 10px; border-radius: 10px; font-size: 14px;">{data.get('word_class')}</span>
                    </div>
                    <p style="color: #64748B; font-size: 18px;">/{data.get('phonetic')}/</p>
                    <div style="background: #F8FAFC; padding: 15px; border-radius: 12px; border-left: 5px solid #FFB300; margin-top: 10px;">
                        <b style="color: #1E293B; font-size: 22px;">{data.get('definition_vi')}</b><br>
                        <i style="color: #64748B;">{data.get('definition_en')}</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Nút chức năng
                c1, c2 = st.columns(2)
                if c1.button("🔊 Nghe phát âm"):
                    tts = gTTS(text=word_input, lang='en')
                    fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
                    st.audio(fp, format='audio/mp3')
                
                if c2.button("💾 Lưu vào kho Siêu nhân"):
                    if word_input not in [w['word'] for w in st.session_state.word_bank]:
                        st.session_state.word_bank.append({
                            "word": word_input, 
                            "phonetic": data.get('phonetic'),
                            "definition_vi": data.get('definition_vi'),
                            "word_class": data.get('word_class'),
                            "definition_en": data.get('definition_en')
                        })
                        st.balloons()
                        st.rerun()
        else:
            st.info("💡 Hãy nhập một từ tiếng Anh để Lexi giúp bạn giải mã nghĩa và cách dùng!")
            st.image("https://img.freepik.com/free-vector/creative-thinking-concept-illustration_114360-3851.jpg", width=450)

    with col_side:
        st.markdown('<div class="side-card"><h5>📚 Từ vựng vừa lưu</h5>', unsafe_allow_html=True)
        if not st.session_state.word_bank:
            st.write("Kho vũ khí đang trống...")
        else:
            # Hiện 5 từ gần nhất kèm nghĩa dịch luôn
            for w in reversed(st.session_state.word_bank[-5:]):
                st.markdown(f"""
                <div class="word-item">
                    <b style="color: #3B82F6;">{w['word']}</b><br>
                    <small>{w['definition_vi']}</small>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "🎯 Đấu trường Ôn tập":
    if word_count < 4:
        st.warning("⚠️ Bạn cần ít nhất 4 từ trong kho để mở khóa Đấu trường. Hãy tra thêm từ nhé!")
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

# --- PHẦN KHÓA TÍNH NĂNG ---
elif page in ["📖 Reading", "✍️ Writing"]:
    limit = 20 if page == "📖 Reading" else 40
    if word_count < limit:
        st.markdown(f"""
        <div style="text-align:center; padding:100px; border:2px dashed #CBD5E1; border-radius:20px; background: white;">
            <h1 style="font-size:80px;">🔒</h1>
            <h2 style="color: #64748B;">TÍNH NĂNG ĐANG KHÓA</h2>
            <p>Siêu nhân cần thu thập đủ <b>{limit} từ vựng</b> để mở khóa vùng đất này.</p>
            <p>Tiến độ hiện tại: <b>{word_count}/{limit}</b></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success(f"🎉 Tuyệt vời! Bạn đã đủ Grit để bắt đầu luyện {page}.")