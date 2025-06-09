# 人工智慧

## 組別

-11328115 王麒瑋

-11328102 廖子儀

## Github網址(完整代碼)
https://github.com/owoblackandwhite/AI

## 專題摘要
本專題旨在打造一款具備語音互動、情緒理解與記憶能力的陪伴型 AI 助理系統 —— Mentora。使用者透過語音與 AI 進行自然對話，系統能根據過往歷史記錄與當前輸入產生溫柔且具有同理心的回應，同時偵測回應中的情緒以利後續延伸應用。此系統整合 Google Gemini 模型、語音辨識（SpeechRecognition）、語音合成（pyttsx3）與本地 JSON 檔案儲存機制，實現一個可長期陪伴並逐漸理解使用者的 AI 對話體驗。

## 設計過程

| 階段         | 內容描述                                                                 |
|--------------|--------------------------------------------------------------------------|
| 需求分析     | 探討用戶需求，包括即時語音互動、情緒識別、對話紀錄保存等功能            |
| 系統架構設計 | 建立模組架構，分為語音輸入、語音輸出、情緒分析、對話管理四大模組        |
| 模型選擇     | 選用 gemini ai 語言模型進行語意理解與回應；語音合成採用 Edge TTS 技術        |
| 程式開發     | 使用 Python 撰寫，整合 speech_recognition、edge_tts、simpleaudio 等套件 |
| 測試與優化   | 針對語音播放中斷、辨識準確率與延遲進行修正與優化                          |
| 使用者測試   | 使用情境腳本進行真實測試，蒐集反饋調整介面與語音策略                      |
| 部署與應用   | 可部署於桌面、行動裝置，或進一步整合於醫療與心理健康服務場域              |

### 2. 技術模組構成

- **語音輸入**：
  - 技術：speech_recognition
  - 功能：使用者語音轉文字，支援噪音校正與辨識錯誤處理

- **語音輸出**：
  - 技術：edge_tts + pydub + simpleaudio
  - 功能：文字轉語音，轉檔為 WAV 播放，確保語音播放完成後再繼續流程

- **語意理解與生成**：
  - 技術：gemini ai 模型
  - 功能：理解使用者輸入語句，生成上下文關聯之回應

- **情緒分析模組**：
  - 技術：自訂語義分析器
  - 功能：判斷 AI 回應的情緒傾向並記錄，用於回應策略調整

- **對話記錄管理**：
  - 技術：JSON 檔案處理
  - 功能：依照使用者儲存歷史對話，可回溯先前互動

### 3. 使用者體驗考量

- 使用者名稱登入，營造個人化體驗
- 首次與回訪使用者語句區別設計，提高陪伴感
- 可中止對話（exit/離開），具結束語音提示
- 系統錯誤以語音回報，降低使用者挫折感

### 4. 核心設計原則

| 原則         | 實作方式                                                                 |
|--------------|--------------------------------------------------------------------------|
| 即時互動     | 採用非同步語音辨識與播放，避免阻塞主執行緒                              |
| 穩定性       | 所有語音與辨識處理轉為非同步後台執行，避免 UI 卡頓                      |
| 情緒導向設計 | 每輪回應自動偵測語意傾向，調整語氣策略                                  |
| 可擴展性     | 各模組解耦設計，可獨立優化或更換，例如切換本地語音模型                  |

---

## 實作結果
### 🧾 歷史模塊(data)
- 用以儲存用戶的歷史紀錄，並轉換為json檔案，其中儲存對話紀錄，與人工智慧的回答與情緒偵測
#### 範例：黑白_history.json
```c
[
  {
    "user": "你好",
    "ai": "你好呀～今天想聊些什麼呢？無論是開心的、煩惱的，我都願意在這裡陪你。",
    "emotion": "友善"
  },
  {
    "user": "對還可以",
    "ai": "嗯，聽起來今天的心情還不錯，對嗎？ 有什麼特別的事情發生，或是單純覺得一切都還可以呢？ 無論如何，我都想聽聽你的想法喔！ 或者，如果最近有什麼讓你感到壓力的事情（像是之前的課程），也可以跟我說說。",
    "emotion": "關懷"
  },
  
]
```
---
### 🧾 回應模塊(models)
- 用於抓取網路模型回應，與分析人工智慧回應的內容，以方便控管
- 注意：這種方式在某些編譯器中，在資料夾中，須放置空檔，進行連結`_init_.py`為必要放置的空檔
#### 模塊一：core_ai.py

```c
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

```
- 抓取網路模型回應，並限制人工智慧的回覆內容，並於回覆內容中，加入歷史紀錄


#### 模塊二：emotion_detector.py

```c
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
```
- 分析人工智慧回應的內容，輸出人工智慧的情緒，以控制其他部件
---

### 📐 記憶模塊(services)

- 用以儲存用戶與人工智慧的對話，並轉換為json檔案，並在對話時，調出檔案，並濃縮為對話紀錄


#### 模塊：user_manager.py

```c
import os
import json

# 設定新的資料夾路徑
DATA_DIR = r'D:\girlfriend.ai\data\patient_logs'
LOGIN_COUNT_FILE = os.path.join('data', 'patient_logs', 'user_login_count.json')

# 確保資料夾存在
os.makedirs(DATA_DIR, exist_ok=True)

def get_history_path(user_id):
    return os.path.join(DATA_DIR, f"{user_id}_history.json")

def get_login_count_path(user_id):
    return os.path.join(DATA_DIR, f"{user_id}_login_count.json")

def save_conversation(user_id, history):
    try:
        path = get_history_path(user_id)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存對話失敗：{e}")

def load_conversation(user_id):
    try:
        path = get_history_path(user_id)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"讀取對話失敗：{e}")
    return []

def save_user_login_count(user_id, count):
    try:
        path = get_login_count_path(user_id)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({"login_count": count}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存登入次數失敗：{e}")

def load_user_login_count(user_id):
    try:
        path = get_login_count_path(user_id)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("login_count", 0)
    except Exception as e:
        print(f"讀取登入次數失敗：{e}")
    return 0

```

---

### 📚 核心模塊(main)

- 調用以上模塊，加以整合，以語音輸入，回傳至人工智慧後，以語音系統輸出



#### 模塊一：config.py

```c
GEMINI_API_KEY = "AIzaSyA6s6f4xg3rClg4Zrq0UXP0seUwxwDlTg4"
```
- 定義人工智慧的金鑰，以方便調用

#### 模塊二：user_manager.py
```c
# 語音轉文字
def speech_to_text():
    retries = 0
    while retries < max_retries:
        with sr.Microphone() as source:
            print("請開始說話...(10秒內)")
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=stt_timeout)
                text = recognizer.recognize_google(audio, language="zh-TW")
                print(f"你說的是：{text}")
                return text
            except sr.WaitTimeoutError:
                print("超過 10 秒沒有輸入，請再試一次。")
            except sr.UnknownValueError:
                print("無法辨識語音，請再試一次。")
            except sr.RequestError as e:
                print(f"語音服務錯誤：{e}")
        retries += 1

    print("達到最大重試次數，請稍後再試。")
    return None

# 主程式
def main():
    user_id = input("請輸入使用者名稱：").strip()
    if not user_id:
        print("使用者名稱不可為空。")
        sys.exit(1)

    history = load_conversation(user_id)
    start_time = time.time()

    # 歡迎語
    if history:
        last_input = history[-1]["user"]
        welcome = f"歡迎回來，{user_id}！我記得你上次說：「{last_input}」，今天還好嗎？"
    else:
        welcome = f"很高興第一次見到你，{user_id}，讓我們開始聊天吧！"

    print("Mentora：" + welcome)
    engine.say("Mentora：" + welcome)
    engine.runAndWait()

    # 聊天迴圈
    while True:
        if time.time() - start_time > timeout:
            print("超過 5 分鐘未操作，程序結束。")
            break

        user_input = speech_to_text()
        if user_input is None:
            continue

        user_input = user_input.strip()
        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit", "離開"]:
            goodbye = "感謝你的分享，期待再次見到你 🌿"
            print("Mentora：" + goodbye)
            engine.say("Mentora：" + goodbye)
            engine.runAndWait()
            break

        # Step 1: 產生回應
        try:
            response = get_response(user_input, history)
        except Exception as e:
            print(f"產生回應失敗：{e}")
            engine.say("我剛剛有點當機了，請再說一次看看好嗎？")
            engine.runAndWait()
            continue

        # Step 2: 情緒分析（Mentora 回應）
        try:
            emotion = detect_emotion(response, history, speaker="ai")
        except Exception as e:
            print(f"情緒分析失敗：{e}")
            emotion = "未知"

        # Step 3: 輸出與語音播放
        print(f"Mentora：{response}")
        engine.say(f"Mentora：{response}")
        engine.runAndWait()

        # Step 4: 儲存對話歷史
        history.append({
            "user": user_input,
            "ai": response,
            "emotion": emotion
        })
        save_conversation(user_id, history)

if __name__ == "__main__":
    main()
```
- 透過用戶輸入的名稱，調出過去紀錄，並整合用戶輸入，回傳至回應模塊，產生輸出，並以語音輸出
---
## 心得
這次的人工智慧的創作，使我廢寢忘食，我從來沒有這麼認真的投入任何一個樣式的工作，每個模塊的完美運作，不同python模組的相互交織，像是一台精美的儀器，雖然中間遇到許多挫折，像是模塊中間打架，檔案放錯地方讀不到，調出的時候，聲音被切斷，甚至有可能因為設定問題，在測試時，在我耳邊音爆，但，永不放棄，跌倒後再站起來，缺陷並不可怕，而是看到缺陷而不去改變，在不斷的精進中，我也看到了程式碼本身到美麗，我也看到程式碼的相互依存關係，也查閱了很多資訊，前人已經為我們打下江山，python的各種內建功能，各種特殊外掛，之後的程式設計將會變成完全不一樣的領域，而不斷努力，永不放棄，有歷史的累積，有前人的幫助，才造就了python現在的美麗
