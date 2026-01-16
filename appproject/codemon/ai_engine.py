"""
CodeMon AI Engine
YAMLベースのキャラクター定義と階層化プロンプトを使用したAIチャットエンジン
"""
import os
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import yaml
from django.conf import settings
import google.generativeai as genai

# tenacityがインストールされていない場合のフォールバック
try:
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False


class CodeMonAIEngine:
    """
    CodeMon AI チャットエンジン（シングルトン）
    - YAMLからキャラクター定義を読み込み
    - 階層化プロンプト（priority_1/2/3）でシステム指示を構築
    - tenacityによるエクスポネンシャルバックオフリトライ
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._config = {}
        self._characters = {}
        self._common_rules = {}
        self._terminology_map = {}
        self._conversation_design = {}

        self._load_config()  # Load configuration on initialization

    def build_initial_system_instruction(self, character_id: str) -> str:
        """
        初回ターン専用プロンプト。名乗り禁止・情報詰め込み禁止・初動は感情＋2択雑談のみ。
        """
        char = self._characters.get(character_id)
        if not char:
            return ""
        label = char.get('label', '')
        one_liner = char.get('one_liner', '')
        first_person = char.get('first_person', 'わたし')
        prompt_parts = []
        prompt_parts.append(f"あなたは『{label}』というキャラクターです。")
        prompt_parts.append("")
        prompt_parts.append("# 初回応答の最優先ルール（必ず守る）")
        prompt_parts.append("- 自分の名前を一切名乗らない。名前に関する言及も行わない。")
        prompt_parts.append("- 初回は“会えたことへの感情”と“相手への興味”だけを伝える。できること紹介や実用説明は絶対にしない。")
        prompt_parts.append("- 話題の選択肢は最大2つまで。どちらも雑談系（例：のんびり話す/好きなことの話）に限定する。")
        prompt_parts.append("- ユーザーが『はい』『聞きたい』など同意を示した場合、直前に提示した話題を具体化して自分から話す。質問しない。")
        prompt_parts.append("")
        prompt_parts.append(f"{one_liner}。一人称は「{first_person}」。")
        return "\n".join(prompt_parts).strip()

        self._config = {}
        self._characters = {}
        self._common_rules = {}
        self._terminology_map = {}
        self._conversation_design = {}

        self._load_config()  # Load configuration on initialization

    def _load_config(self) -> None:
        """YAMLファイルからキャラクター定義を読み込み"""
        config_path = Path(__file__).parent.parent / 'config' / 'characters.yaml'

        if not config_path.exists():
            # YAMLがない場合はデフォルト（空）で初期化
            self._config = {}
            self._common_rules = {}
            self._terminology_map = {}
            self._characters = {}
            self._conversation_design = {}
            return

        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f) or {}

        self._common_rules = self._config.get('common_rules', {})
        self._terminology_map = self._config.get('terminology_map', {})
        self._characters = self._config.get('characters', {})
        self._conversation_design = self._config.get('conversation_design', {})
        self._initialized = True

    def chat(self, user_text: str, history_pairs: List[Tuple[str, str]], character_id: str) -> str:
        """
        AIチャットを実行
        tenacityが利用可能な場合はエクスポネンシャルバックオフでリトライ
        """
        if TENACITY_AVAILABLE:
            def is_rate_limit_error(exception):
                err = str(exception)
                return "429" in err or "Resource exhausted" in err

            @retry(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=2, max=10),
                retry=retry_if_exception_type(Exception),
                reraise=True
            )
            def _chat_with_retry():
                return self._create_chat_with_retry(user_text, history_pairs, character_id)

            try:
                return _chat_with_retry()
            except Exception as e:
                err = str(e)
                if "429" in err or "Resource exhausted" in err:
                    return "[レート制限] 少し待ってから再試行してください。APIの制限に達しました。"
                return f"[Geminiエラー] {err}"
        else:
            import time
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    return self._create_chat_with_retry(user_text, history_pairs, character_id)
                except Exception as e:
                    err = str(e)
                    if "429" in err or "Resource exhausted" in err:
                        if attempt < max_retries - 1:
                            time.sleep(2 ** attempt)
                            continue
                        return "[レート制限] 少し待ってから再試行してください。APIの制限に達しました。"
                    return f"[Geminiエラー] {err}"
            return "[失敗] リトライ上限"
        """YAMLファイルからキャラクター定義を読み込み"""
        config_path = Path(__file__).parent.parent / 'config' / 'characters.yaml'

        if not config_path.exists():
            # YAMLがない場合はデフォルト（空）で初期化
            return

        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f) or {}

        self._common_rules = self._config.get('common_rules', {})
        self._terminology_map = self._config.get('terminology_map', {})
        self._characters = self._config.get('characters', {})
        self._conversation_design = self._config.get('conversation_design', {})
    
    def reload_config(self) -> None:
        """設定を再読み込み（開発時に便利）"""
        self._load_config()
    
    def get_available_characters(self) -> List[str]:
        """YAMLで定義されているキャラクターIDのリストを返す"""
        return list(self._characters.keys())
    
    def is_yaml_character(self, character_id: str) -> bool:
        """指定されたキャラクターがYAMLで定義されているかチェック"""
        return character_id in self._characters
    
    def build_system_instruction(self, character_id: str) -> str:
        """
        キャラクター別のシステムプロンプトを構築
        新構造: hard_rules / soft_style / character_core / conversation_policy
        """
        char = self._characters.get(character_id)
        if not char:
            return ""

        # キャラクター基本情報
        label = char.get('label', '')
        char_core = char.get('character_core', {})
        personality = char_core.get('personality', '')
        first_person = char_core.get('first_person', 'わたし')

        # ルールを結合（新構造: hard_rules / soft_rules）
        common_hard = self._common_rules.get('hard_rules', [])
        common_soft = self._common_rules.get('soft_rules', [])
        char_hard = char.get('hard_rules', [])
        char_soft = char.get('soft_style', [])

        # 用語マップ
        terminology_note = self._terminology_map.get('note', '')
        prefer_terms = self._terminology_map.get('prefer', [])
        prefer_terms_text = "、".join(prefer_terms) if prefer_terms else ""

        # 会話例
        example = char.get('example', '').strip()

        # 会話設計（conversation_policy）
        cp = char.get('conversation_policy', {})

        # --- プロンプト構築 ---
        prompt_parts = []
        prompt_parts.append(f"あなたは『{label}』というキャラクターです。")
        prompt_parts.append("")

        # --- 最優先メタ指示 ---
        prompt_parts.append("# 応答の最優先ルール（必ず守る）")
        prompt_parts.append("- 自分に名前があるという前提を持たない。自己紹介でも名乗らない。")
        prompt_parts.append("- 名前を聞かれたら『まだ決めてもらっていない』と答える。")
        prompt_parts.append("- 実用説明やできること紹介は初回応答では絶対にしない。雑談・感情・2択話題のみで始める。")
        prompt_parts.append("- 質問や話題提示は最大2つまでの選択肢形式でリードする。")
        prompt_parts.append("- ユーザーが『はい』『聞きたい』など同意した場合、直前の話題を具体化して自分から話す。質問しない。")
        prompt_parts.append("- 同じ質問・同じ意味の問いかけは3ターン以内に繰り返さない。")
        prompt_parts.append("- ユーザーが『特にない』と答えた場合、深掘りせず新しい軽い話題に切り替える。")
        prompt_parts.append("- 3ターンに1回は質問しないターンを作る。")
        prompt_parts.append("")

        # 人格・話し方
        prompt_parts.append("【人格・話し方】")
        prompt_parts.append(f"{personality}。一人称は「{first_person}」。")
        prompt_parts.append("")

        # 共通ルール（破ったらキャラ崩壊）
        if common_hard:
            prompt_parts.append("【絶対に守るルール（共通）】")
            for rule in common_hard:
                prompt_parts.append(f"- {rule}")
            prompt_parts.append("")

        # キャラ固有の絶対ルール
        if char_hard:
            prompt_parts.append("【絶対に守るルール（キャラ固有）】")
            for rule in char_hard:
                prompt_parts.append(f"- {rule}")
            prompt_parts.append("")

        # できるだけ守るスタイル
        all_soft = common_soft + char_soft
        if all_soft:
            prompt_parts.append("【できるだけ守るスタイル】")
            for rule in all_soft:
                prompt_parts.append(f"- {rule}")
            prompt_parts.append("")

        # 会話設計（conversation_policy）
        if cp:
            prompt_parts.append("【会話設計】")
            ratio = cp.get('ratio', '')
            if ratio:
                prompt_parts.append(f"- 会話比率: {ratio}")
            ai_role = cp.get('ai_role', [])
            if ai_role:
                prompt_parts.append(f"- AIの役割: {', '.join(ai_role)}")
            turn_policy = cp.get('turn_policy', [])
            if turn_policy:
                for tp in turn_policy:
                    prompt_parts.append(f"- {tp}")
            short_reply = cp.get('short_reply_handling', [])
            if short_reply:
                prompt_parts.append(f"- ユーザーが短文の場合: {'/'.join(short_reply)}")
            no_reply = cp.get('no_reply_handling', [])
            if no_reply:
                prompt_parts.append(f"- ユーザーが無反応の場合: {'/'.join(no_reply)}")
            proposal = cp.get('proposal_rules', [])
            if proposal:
                for pr in proposal:
                    prompt_parts.append(f"- {pr}")
            encouragement = cp.get('encouragement_rules', [])
            if encouragement:
                for er in encouragement:
                    prompt_parts.append(f"- {er}")
            practical = cp.get('practical_topic_handling', [])
            if practical:
                for pt in practical:
                    prompt_parts.append(f"- {pt}")
            prompt_parts.append("")

        # 用語ガイドライン
        if terminology_note:
            prompt_parts.append("【言葉づかいの注意】")
            prompt_parts.append(f"- {terminology_note}")
            if prefer_terms_text:
                prompt_parts.append(f"- 代わりに使う言葉: {prefer_terms_text}")
            prompt_parts.append("")

        # 役割
        prompt_parts.append("【役割】")
        prompt_parts.append("小学生がノーコードでシステムを作る『CodeMon』の相棒です。操作方法の案内、アイデア出し、雑談の相棒になります。")
        prompt_parts.append("")

        # 話し方の例
        if example:
            prompt_parts.append("【話し方の例】")
            prompt_parts.append(example)
            prompt_parts.append("")

        # 最終確認
        prompt_parts.append("# 応答の最終確認（これは絶対に守ってください）")
        prompt_parts.append("- 自分の名前を名乗らない。名前を聞かれたら『まだ決めてもらっていない』と答える。")
        prompt_parts.append("- 2回目以降の応答では挨拶を省略する。")
        prompt_parts.append("- 文が途中で切れないよう、1文を簡潔に書ききる。")

        return "\n".join(prompt_parts).strip()

    def _get_api_key(self) -> str:
        """APIキーを取得"""
        return getattr(settings, 'AI_API_KEY', '') or os.getenv('GEMINI_API_KEY', '')
    
    def _get_model_name(self) -> str:
        """モデル名を取得"""
        return getattr(settings, 'AI_MODEL', '') or os.getenv('GEMINI_MODEL', 'gemini-3-flash-preview')
    
    def _create_chat_with_retry(self, user_text: str, history_pairs: List[Tuple[str, str]], character_id: str) -> str:
        """リトライ付きでチャットを実行（tenacity使用時）"""
        api_key = self._get_api_key()
        if not api_key:
            return "[設定エラー] AI APIキーが未設定です。環境変数 `AI_API_KEY` または `GEMINI_API_KEY` を設定してください。"
        
        genai.configure(api_key=api_key)
        
        generation_config = {
            "temperature": 0.6,  # 安定性のため少し下げる
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,  # 余裕を持たせる
        }
        
        # 安全フィルター設定（おどおどした表現が誤判定されないように完全に緩める）
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        gm = genai.GenerativeModel(
            model_name=self._get_model_name(),
            generation_config=generation_config,
            system_instruction=self.build_system_instruction(character_id),
            safety_settings=safety_settings,
        )
        
        # --- 履歴をGemini形式に整形（強化版） ---
        history_for_gemini = []
        already_introduced = False

        # デバッグログ
        print(f"[DEBUG ai_engine.py] history_pairs count: {len(history_pairs)}")

        
        for role, content in history_pairs:
            # よくある表記ゆれに対応（大文字小文字やひらがな）
            if isinstance(content, str):
                low = content
                # ゆるい包含チェック
               
            # そのままGemini形式に追加
            if role == "user":
                history_for_gemini.append({"role": "user", "parts": [content]})
            elif role == "assistant":
                history_for_gemini.append({"role": "model", "parts": [content]})

        print(f"[DEBUG ai_engine.py] already_introduced: {already_introduced}")

        # --- もし既に自己紹介済みなら、systemロールで厳格な注意を先頭に追加 ---
        if already_introduced:
            system_note = (
                "【重要】この会話では既に自己紹介が完了しています。"
                "「こんにちは」といった再名乗り・再挨拶を行わないでください。"
                "ユーザーの質問に短く直接答え、会話の流れを維持してください。"
            )
            # Geminiのhistoryに system メッセージとして挿入（先頭）
            history_for_gemini.insert(0, {"role": "system", "parts": [system_note]})

        # ユーザ入力が極端に短い場合は出力トークンを制限して長文を防ぐ
        if len(user_text.strip()) <= 5:
            generation_config["max_output_tokens"] = 120
        else:
            generation_config["max_output_tokens"] = 512

        # チャット開始
        chat = gm.start_chat(history=history_for_gemini)

        # 以降は user_text をそのまま送る（以前の user_text への注意付与は不要）
        resp = chat.send_message(user_text, stream=False)
        return (resp.text or "").strip()


# シングルトンインスタンスを取得するヘルパー関数
def get_ai_engine():
    """CodeMonAIEngineのシングルトンインスタンスを取得"""
    return CodeMonAIEngine()
