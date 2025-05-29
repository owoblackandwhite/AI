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
