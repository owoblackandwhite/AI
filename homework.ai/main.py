import sys
import time
import pyttsx3
import speech_recognition as sr
from models.core_ai import get_response
from models.emotion_detector import detect_emotion
from services.user_manager import save_conversation, load_conversation

# 初始化語音合成
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

# 初始化語音辨識器
recognizer = sr.Recognizer()

# 設定參數
max_retries = 3
timeout = 5 * 60  # 5 分鐘
stt_timeout = 10

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
