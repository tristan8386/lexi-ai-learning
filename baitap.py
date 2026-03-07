import random

class LexiQuiz:
    @staticmethod
    def tao_trac_nghiem(word_bank):
        if len(word_bank) < 4: return None
        
        target = random.choice(word_bank)
        correct_ans = target['definition_vi']
        
        # Lọc danh sách mồi nhử (distractors)
        # Ưu tiên các từ có cùng loại từ (noun, verb...) để câu hỏi thách thức hơn
        same_class = [w['definition_vi'] for w in word_bank 
                      if w.get('word_class') == target.get('word_class') and w['word'] != target['word']]
        
        others = [w['definition_vi'] for w in word_bank if w['word'] != target['word']]
        
        # Chọn 3 mồi nhử: ưu tiên cùng loại từ, nếu thiếu thì lấy ngẫu nhiên
        distractors = random.sample(same_class, min(len(same_class), 3))
        if len(distractors) < 3:
            con_lai = list(set(others) - set(distractors))
            distractors += random.sample(con_lai, 3 - len(distractors))
            
        options = distractors + [correct_ans]
        random.shuffle(options)
        
        return {
            "word": target['word'],
            "phonetic": target['phonetic'],
            "correct_ans": correct_ans,
            "options": options,
            "hint": target.get('definition_en', "No hint available")
        }

    @staticmethod
    def tao_dung_sai(word_bank):
        if len(word_bank) < 2: return None
        target = random.choice(word_bank)
        is_correct = random.choice([True, False])
        
        if is_correct:
            display_def = target['definition_vi']
        else:
            others = [w['definition_vi'] for w in word_bank if w['word'] != target['word']]
            display_def = random.choice(others)
            
        return {
            "word": target['word'],
            "display_def": display_def,
            "is_correct": is_correct
        }