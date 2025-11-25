import os
import time
from typing import List, Tuple
import google.generativeai as genai

CHARACTER_SYSTEM_LINES = {
    "usagi": "キャラクター: うさぎ。おどおど前向き。日本語・絵文字なし・丁寧。",
    "kitsune": "キャラクター: きつね。軽口と合理的。日本語・絵文字なし。",
}

def build_system_instruction(character_id: str) -> str:
    return CHARACTER_SYSTEM_LINES.get(character_id, CHARACTER_SYSTEM_LINES["usagi"])

def chat_gemini(user_text: str, history_pairs: List[Tuple[str, str]], character_id: str = "usagi") -> str:
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return "[設定エラー] GEMINI_API_KEY が未設定です。"

    genai.configure(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 1024,
    }

    gm = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
        system_instruction=build_system_instruction(character_id),
    )

    # 過去履歴をGemini形式に整形
    history_for_gemini = []
    for role, content in history_pairs:
        if role == "user":
            history_for_gemini.append({"role": "user", "parts": [content]})
        elif role == "assistant":
            history_for_gemini.append({"role": "model", "parts": [content]})

    chat = gm.start_chat(history=history_for_gemini)

    # 簡易リトライ（429など）
    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = chat.send_message(user_text, stream=False)
            return (resp.text or "").strip()
        except Exception as e:
            err = str(e)
            if "429" in err or "Resource exhausted" in err:
                if attempt < max_retries - 1:
                    time.sleep(60)
                    continue
                return "[レート制限] 少し待ってから再試行してください。"
            return f"[Geminiエラー] {err}"
    return "[失敗] リトライ上限"
