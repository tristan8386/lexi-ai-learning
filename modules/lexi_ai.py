import google.generativeai as genai
import streamlit as st
import json
import re

def configure_ai():
    try:
        api_key = st.secrets["GENAI_API_KEY"]
        genai.configure(api_key=api_key)
        
        # Quét danh sách model khả dụng
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Ưu tiên gemini-1.5-flash, nếu không có thì lấy cái đầu tiên
        for m in models:
            if 'gemini-1.5-flash' in m:
                return genai.GenerativeModel(m)
        return genai.GenerativeModel(models[0]) if models else None
    except:
        return None

def get_word_info(word):
    try:
        model = configure_ai()
        if not model:
            return "Lỗi: Không tìm thấy Model AI hoặc sai API Key."

        prompt = f"""
        Analyze the word '{word}'. Return ONLY JSON:
        {{
          "phonetic": "IPA",
          "word_class": "Noun/Verb/...",
          "definition": "Nghĩa tiếng Việt",
          "etymology": "Gốc từ",
          "nuance": "Sắc thái",
          "collocations": [], "idioms": [], "word_family": [],
          "examples": ["Ví dụ 1", "Ví dụ 2", "Ví dụ 3"]
        }}
        """
        response = model.generate_content(prompt)
        
        # Dùng Regex để bốc tách JSON chuẩn xác
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return "Lỗi: AI trả về dữ liệu không đúng cấu trúc."
    except Exception as e:
        return f"Lỗi hệ thống lexi_ai: {str(e)}"

def check_writing(sentence, word):
    try:
        model = configure_ai()
        prompt = f"Check sentence: '{sentence}' with word '{word}'. Return ONLY JSON: {{'is_correct': true/false, 'feedback': '...'}}"
        response = model.generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        return json.loads(match.group(0)) if match else {"is_correct": False, "feedback": "Lỗi AI."}
    except:
        return {"is_correct": False, "feedback": "Lỗi kết nối AI."}