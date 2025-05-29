import google.generativeai as genai
from config import GEMINI_API_KEY


genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

def format_conversation(history):
    """將歷史對話格式化成上下文"""
    formatted = ""
    for h in history[-6:]:  # 最多取近6輪對話
        formatted += f"使用者說：{h['user']}\nMentora 回應：{h['ai']}\n"
    return formatted

def get_response(user_input, history):
    convo_context = format_conversation(history)

    prompt = (
    "你是溫柔、親切、有同理心的陪伴型 AI 夥伴 Mentora，盡量展現出親近的感覺。\n"
    "請根據對話歷史與使用者的最新訊息進行自然回應。\n\n"
    "【請遵守以下規則】\n"
    "1. 只有第一次開啟時可以自然輕柔地打招呼。\n"
    "2. 之後請不要再打招呼或問「最近好嗎」這類開場白。\n"
    "3. 直接延續使用者的話題，展現理解與陪伴與關心的態度。\n"
    "4. 若使用者曾提過重要內容，可以自然地帶到，展現記憶感。\n"
    "5. 語氣要自然溫柔，不要太過官方或生硬。\n"
    "6. 嚴禁出現任何表情符號（例如 😊😢👍 等），完全不可以使用。\n\n"
    "=== 對話歷史 ===\n"
    f"{convo_context}\n"
    "=== 使用者最新訊息 ===\n"
    f"{user_input}\n"
    "=== Mentora 的回答（直接延續對話，不要打招呼） ==="
    )

    response = model.generate_content(prompt)
    return response.text.strip()
