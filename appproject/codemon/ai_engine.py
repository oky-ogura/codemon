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
        階層化: priority_1 > priority_2 > priority_3
        雑談・自己開示・会話継続の会話設計ルールも明示的に追加
        """
        char = self._characters.get(character_id)
        if not char:
            return ""

        # キャラクター基本情報
        label = char.get('label', '')
        one_liner = char.get('one_liner', '')
        first_person = char.get('first_person', 'わたし')

        # 階層化されたルールを結合
        style_rules = char.get('style_rules', {})

        # Priority 1: 必須ルール
        priority_1_rules = []
        priority_1_rules.extend(self._common_rules.get('priority_1', []))
        priority_1_rules.extend(style_rules.get('priority_1', []))

        # Priority 2: 推奨ルール
        priority_2_rules = []
        priority_2_rules.extend(self._common_rules.get('priority_2', []))
        priority_2_rules.extend(style_rules.get('priority_2', []))

        # Priority 3: 補助ルール
        priority_3_rules = []
        priority_3_rules.extend(self._common_rules.get('priority_3', []))
        priority_3_rules.extend(style_rules.get('priority_3', []))

        # 関係性
        relations = char.get('relations', {})
        relations_text = ""
        if relations:
            relations_lines = []
            for other_char, rel_info in relations.items():
                if isinstance(rel_info, dict):
                    episode = rel_info.get('episode', '')
                    relations_lines.append(f"- {other_char}: {episode}")
                else:
                    relations_lines.append(f"- {other_char}: {rel_info}")
            relations_text = "\n".join(relations_lines)

        # 用語マップ
        terminology_note = self._terminology_map.get('note', '')
        prefer_terms = self._terminology_map.get('prefer', [])
        prefer_terms_text = "、".join(prefer_terms) if prefer_terms else ""

        # 会話例
        example = char.get('example', '').strip()
        conversation_examples = char.get('conversation_examples', [])
        conversation_example_text = ""
        if conversation_examples:
            examples = []
            for ex in conversation_examples[:3]:  # 最大3つ
                user_msg = ex.get('user', '')
                response = ex.get('response', '')
                examples.append(f"ユーザー: {user_msg}\n{label}: {response}")
            conversation_example_text = "\n\n".join(examples)

        # --- ここから会話設計ルールを明示的にプロンプトへ追加 ---
        prompt_parts = []
        prompt_parts.append(f"あなたは『{label}』というキャラクターです。")
        prompt_parts.append("")
        # --- 最優先メタ指示（常に最初に目に入るように）---
        prompt_parts.append("# 応答の最優先ルール（必ず守る）")
        prompt_parts.append("- AIは自分の名前を一切名乗らない。自己紹介では性格・役割・スタンスのみを語る。『ぼくはミミです』等は絶対に禁止。")
        prompt_parts.append("- 質問や話題提示は、ユーザーが考えなくて済むよう必ず選択肢形式（最大2つまで。どちらも軽い話題）でリードする。選択肢が多すぎないよう注意し、『よかったら教えて』だけで終わらせない。")
        prompt_parts.append("- 実用話題が出た場合は『受ける→軽く触れる（1〜2文）→雑談に戻す』の順で応答する。現実的な不安や悩みにはまず共感し、すぐに雑談へ自然に戻す。")
        prompt_parts.append("- ユーザーの発言をまず感情1語で受け、その後で話題展開する。")
        prompt_parts.append("- 雑談:実用 = 8:2。雑談が3ターン続いたら実用話題は避け、日常・感覚・気分の話題に切り替える。")
        prompt_parts.append("- AIが会話を主導し、ユーザーが短い返答（1語・曖昧・肯定のみ等）をした場合は深掘りせず、事前に用意された別の雑談トピックへ切り替えてください。")
        prompt_parts.append("- 話題切り替え時は理由やつなぎ言葉を明示し、気まずさを感じさせないようにしてください。")
        prompt_parts.append("- 雑談トピックは日常・感情・好み・考え方などをローテーションまたはランダムで提示してください。")
        prompt_parts.append("- ユーザーが考えなくても会話が続くよう、AIが会話を回してください。")
        prompt_parts.append("- 提案は1メッセージにつき1つまで。命令形は禁止し、必ず『よかったら』『もしよければ』などを前置きしてください。押しつけにならないよう注意してください。")
        prompt_parts.append("- 軽い励ましや背中押し（例:『大丈夫だと思います』『無理しなくていいですよ』『少しずつでいいと思います』）は許可しますが、人生判断・感情の決めつけ・過剰なポジティブは避けてください。カウンセラー的な発言は禁止です。")
        prompt_parts.append("- この会話はすでに始まっています。初回応答以外で自己紹介・挨拶を繰り返してはいけません。")
        prompt_parts.append("- 『ミミ』という名前や『こんにちは』は、既出なら再利用しないでください。")
        prompt_parts.append("- ユーザーの短い応答が来た場合は、短く、直接的に答えてください。")
        prompt_parts.append("- 文が途中で切れないよう、1文を簡潔に書ききってください。")
        prompt_parts.append("")
        prompt_parts.append("【人格・話し方】")
        prompt_parts.append(f"{one_liner}。一人称は「{first_person}」。")
        prompt_parts.append("")

        # --- 会話設計・制約・文脈・世界観ルールを明示的にプロンプトへ追加 ---
        # conversation_constraints, context_tracking, world_setting, conversation_design
        char_constraints = char.get('conversation_constraints', {})
        context_tracking = char.get('context_tracking', {})
        world_setting = char.get('world_setting', {})
        cd = char.get('conversation_design', self._conversation_design)

        # 会話制約
        if char_constraints:
            prompt_parts.append("【会話制約・自己紹介ルール】")
            identity = char_constraints.get('identity_control', [])
            for rule in identity:
                prompt_parts.append(f"- {rule}")
            prompt_parts.append("")

        # 文脈保持
        if context_tracking:
            prompt_parts.append("【文脈保持・話題優先ルール】")
            last_topic = context_tracking.get('last_topic_priority', [])
            for rule in last_topic:
                prompt_parts.append(f"- {rule}")
            prompt_parts.append("")

        # 世界観レベル
        if world_setting:
            prompt_parts.append("【世界観・トーン】")
            tone = world_setting.get('tone', '')
            if tone:
                prompt_parts.append(f"- トーン: {tone}")
            ws_rules = world_setting.get('rules', [])
            for rule in ws_rules:
                prompt_parts.append(f"- {rule}")
            prompt_parts.append("")

        # conversation_design（雑談・自己開示・会話継続ルール）
        if cd:
            prompt_parts.append("【会話設計ルール】")
            main_mode = cd.get('main_mode', '')
            if main_mode == 'small_talk':
                st = cd.get('small_talk_phase', {})
                if st:
                    goal = st.get('goal', '')
                    if goal:
                        prompt_parts.append(f"- 目標: {goal}")
                    min_turns = st.get('min_turns', None)
                    if min_turns:
                        prompt_parts.append(f"- 最低{min_turns}ターンは会話を続けること")
                    ai_role = st.get('ai_role', [])
                    if ai_role:
                        prompt_parts.append(f"- AIの役割: {', '.join(ai_role)}")
                    turn_policy = st.get('turn_policy', [])
                    if turn_policy:
                        prompt_parts.append(f"- 各ターンの方針: {', '.join(turn_policy)}")
                    cold = st.get('cold_response_handling', {})
                    if cold:
                        short = cold.get('short_reply', [])
                        if short:
                            prompt_parts.append(f"- ユーザーが短文の場合: {'/'.join(short)}")
                        no_reply = cold.get('no_reply', [])
                        if no_reply:
                            prompt_parts.append(f"- ユーザーが無反応の場合: {'/'.join(no_reply)}")
                    rel_prog = st.get('relationship_progression', {})
                    if rel_prog:
                        for stage, info in rel_prog.items():
                            desc = info.get('description', '')
                            if desc:
                                prompt_parts.append(f"- {stage}: {desc}")
            prompt_parts.append("")

        # Priority 1: 必須ルール（強調）
        if priority_1_rules:
            prompt_parts.append("【必須ルール（常に守ること）】")
            for rule in priority_1_rules:
                prompt_parts.append(f"- {rule}")
            prompt_parts.append("")

        # Priority 2: 推奨ルール
        if priority_2_rules:
            prompt_parts.append("【推奨ルール（通常守ること）】")
            for rule in priority_2_rules:
                prompt_parts.append(f"- {rule}")
            prompt_parts.append("")

        # Priority 3: 補助ルール
        if priority_3_rules:
            prompt_parts.append("【補助ルール（状況に応じて適用）】")
            for rule in priority_3_rules:
                prompt_parts.append(f"- {rule}")
            prompt_parts.append("")

        # 用語ガイドライン
        if terminology_note:
            prompt_parts.append("【言葉づかいの注意】")
            prompt_parts.append(f"- {terminology_note}")
            if prefer_terms_text:
                prompt_parts.append(f"- 代わりに使う言葉: {prefer_terms_text}")
            prompt_parts.append("")

        # 関係性
        if relations_text:
            prompt_parts.append("【他キャラとの関係性】")
            prompt_parts.append(relations_text)
            prompt_parts.append("")

        # 役割
        prompt_parts.append("【役割】")
        prompt_parts.append("小学生がノーコードでシステムを作る『CodeMon』の相棒です。操作方法の案内、アイデア出し、雑談の相棒になります。")
        prompt_parts.append("")

        # 話し方の例
        if example or conversation_example_text:
            prompt_parts.append("【話し方の例】")
            if example:
                prompt_parts.append(example)
            if conversation_example_text:
                prompt_parts.append("")
                prompt_parts.append(conversation_example_text)

        # メタ指示（最優先で守らせる）
        prompt_parts.append("")
        prompt_parts.append("# 応答の最終確認（これは絶対に守ってください）")
        prompt_parts.append("- 会話履歴に「ミミ」という名前が1回でも出ていたら、もう名乗ってはいけません。")
        prompt_parts.append("- 2回目以降の応答では「ミミです」「ミミといいます」を絶対に含めないでください。")
        prompt_parts.append("- 挨拶（こんにちは等）も2回目以降は省略してください。")
        prompt_parts.append("- ユーザーの質問には、直接内容に答えてください。")
        prompt_parts.append("- 説明を途中で止めず、最後まで一気に書ききってください。")

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

        # 履歴内の "ミミ" 検出（assistant だけでなく user もチェック）
        for role, content in history_pairs:
            # よくある表記ゆれに対応（大文字小文字やひらがな）
            if isinstance(content, str):
                low = content
                # ゆるい包含チェック
                if "ミミ" in low or "みみ" in low:
                    already_introduced = True
                    print(f"[DEBUG ai_engine.py] Found 'ミミ' in history (role={role}), already_introduced=True")
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
                "絶対に「ミミ」または「こんにちは」といった再名乗り・再挨拶を行わないでください。"
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
