import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

def detect_emotion(text, history, speaker="user"):
    convo_context = ""
    for h in history[-6:]:
        convo_context += f"Mentora 回應：{h['ai']}\n"
    if speaker == "ai":
        prompt = (
            "以下是Mentora針對使用者的回應內容。\n"
            "請分析Mentora語句中所表現的情緒。\n"
            "僅輸出被舉例的1個最符合狀況的情緒詞（如：開心、難過、安慰、生氣），不需多餘文字。\n\n"
            f"Mentora說：{text}\n"
            "情緒分析結果："
        )
    else:
        raise ValueError("speaker 必須為 'user' 或 'ai'")

    response = model.generate_content(prompt)
    return response.text.strip()


