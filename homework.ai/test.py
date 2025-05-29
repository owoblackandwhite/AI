import asyncio
import os
import tempfile
import time
import threading

from pydub import AudioSegment
from pydub.utils import which
import simpleaudio as sa
import speech_recognition as sr
from edge_tts import Communicate

# 語音引擎設定
os.environ["PATH"] += os.pathsep + r"C:\Program Files\FFMPEG\bin"
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

VOICE = "zh-TW-HsiaoChenNeural"
recognizer = sr.Recognizer()

# 模擬回應與情緒檢測函式（請替換為實際邏輯）
def get_response(text, history): return "這是回應：" + text
def detect_emotion(text, history, speaker="ai"): return "neutral"
def load_conversation(user_id): return []
def save_conversation(user_id, history): pass

# 語音播放（阻塞直到播放完畢）
async def speak_text_async(text: str):
    try:
        print(f"[🗣️] 語音合成開始：{text}")
        communicate = Communicate(text, VOICE)
        mp3_path = os.path.join(tempfile.gettempdir(), f"mentora_tts_{int(time.time())}.mp3")
        wav_path = mp3_path.replace(".mp3", ".wav")

        await communicate.save(mp3_path)
        print("[🎧] MP3 下載完成，轉換為 WAV...")
        audio = AudioSegment.from_file(mp3_path, format="mp3")
        audio.export(wav_path, format="wav")

        print("[▶️] 播放語音中...")
        wave_obj = sa.WaveObject.from_wave_file(wav_path)
        play_obj = wave_obj.play()
        await asyncio.to_thread(play_obj.wait_done)

        os.remove(mp3_path)
        os.remove(wav_path)
        print("[✅] 語音播放完成")
        await asyncio.sleep(0.5)  # 播放完稍作等待，避免卡麥克風

    except Exception as e:
        print(f"[❌] 播放錯誤：{e}")

# 語音轉文字
async def speech_to_text_async(timeout=10):
    print("[🎤] 等待使用者說話...")
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = await asyncio.to_thread(recognizer.listen, source, timeout=timeout)
            text = await asyncio.to_thread(recognizer.recognize_google, audio, language="zh-TW")
            print(f"[📝] 使用者說了：{text}")
            return text
        except sr.WaitTimeoutError:
            print("[⌛] 沒有語音輸入")
        except sr.UnknownValueError:
            print("[⚠️] 語音無法辨識")
        except sr.RequestError as e:
            print(f"[❌] 語音辨識錯誤：{e}")
    return None

# 主流程
async def main_async():
    print("[🚀] 啟動 Mentora AI 助理")
    user_id = input("請輸入使用者名稱：").strip()
    if not user_id:
        print("使用者名稱不可為空。")
        return

    history = load_conversation(user_id)
    if history:
        last_input = history[-1]["user"]
        welcome = f"歡迎回來，{user_id}！我記得你上次說：「{last_input}」，今天還好嗎？"
    else:
        welcome = f"很高興第一次見到你，{user_id}，讓我們開始聊天吧！"

    print(f"[Mentora] {welcome}")
    await speak_text_async(welcome)

    timeout = 5 * 60
    last_activity = time.time()

    while True:
        if time.time() - last_activity > timeout:
            print("[⏳] 超過 5 分鐘未操作，結束對話。")
            break

        user_input = await speech_to_text_async()
        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit", "離開"]:
            goodbye = "感謝你的分享，期待再次見到你 🌿"
            print(f"[Mentora] {goodbye}")
            await speak_text_async(goodbye)
            break

        try:
            response = get_response(user_input, history)
            print(f"[Mentora] {response}")
            await speak_text_async(response)

            emotion = detect_emotion(response, history, speaker="ai")
            history.append({
                "user": user_input,
                "ai": response,
                "emotion": emotion
            })
            save_conversation(user_id, history)
            last_activity = time.time()

        except Exception as e:
            print(f"[❌] 系統錯誤：{e}")
            await speak_text_async("系統發生錯誤，請稍後再試。")

if __name__ == "__main__":
    asyncio.run(main_async())
