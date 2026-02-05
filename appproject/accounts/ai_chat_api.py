from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from codemon.services import chat_gemini
from .models import AiConfig
from .views import get_logged_account
import json

@csrf_exempt
def ai_chat_api(request):
    print(f"[DEBUG AI CHAT] Method: {request.method}")
    print(f"[DEBUG AI CHAT] Content-Type: {request.content_type}")
    print(f"[DEBUG AI CHAT] Body length: {len(request.body)}")
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        # JSON形式のリクエストボディを解析
        if request.content_type == 'application/json':
            body_str = request.body.decode('utf-8')
            print(f"[DEBUG AI CHAT] Body: {body_str}")
            data = json.loads(body_str)
            message = data.get('message', '')
            print(f"[DEBUG AI CHAT] Message: {message}")
        else:
            # フォームデータの場合
            message = request.POST.get('message', '')
            print(f"[DEBUG AI CHAT] Form message: {message}")
        
        if not message:
            print(f"[ERROR AI CHAT] Message is empty!")
            return JsonResponse({'error': 'メッセージが空です'}, status=400)
        acc = get_logged_account(request)
        ai_config = None
        character = 'inu'
        # appearance名→YAML ID変換マップ
        appearance_map = {
            'うさぎ': 'usagi',
            'キツネ': 'kitsune',
            'いぬ': 'inu',
            'イヌ': 'inu',
            'パンダ': 'panda',
            'リス': 'risu',
            'フクロウ': 'fukurou',
            'ネコ': 'neko',
            'アルパカ': 'arupaka',
            # 画像名も考慮
            'usagi': 'usagi',
            'kitsune': 'kitsune',
            'inu': 'inu',
            'panda': 'panda',
            'risu': 'risu',
            'fukurou': 'fukurou',
            'neko': 'neko',
            'arupaka': 'arupaka',
        }
        if acc:
            ai_config = AiConfig.objects.filter(user_id=acc.user_id).first()
            if ai_config and ai_config.appearance:
                # .png除去・小文字化
                appearance = ai_config.appearance.replace('.png', '').replace('.PNG', '').strip()
                # マッピング（なければそのまま）
                character = appearance_map.get(appearance, appearance.lower())
        
        # セッションから会話履歴を取得（キャラクターごとに保持）
        session_key = f'ai_chat_history_{character}'
        history_raw = request.session.get(session_key, [])
        # セッションはリストで保存されるのでタプルに変換
        history_pairs = [(h[0], h[1]) for h in history_raw if len(h) >= 2]
        
        # デバッグログ
        print(f"[DEBUG] Session key: {session_key}")
        print(f"[DEBUG] History pairs count: {len(history_pairs)}")
        for i, (role, content) in enumerate(history_pairs):
            print(f"[DEBUG] History[{i}]: {role} = {content[:50]}...")
        
        # Gemini APIでAI返答を生成（履歴を渡す）
        ai_reply = chat_gemini(message, history_pairs, character)
        # Geminiエラーやレート制限等は必ずerrorキーで返す
        if ai_reply.startswith('[') and ']' in ai_reply:
            # 例: [Geminiエラー] ... や [レート制限] ...
            return JsonResponse({'error': ai_reply}, status=500)

        # 履歴を更新（最大10往復まで保持）
        history_raw.append(['user', message])
        history_raw.append(['assistant', ai_reply])
        if len(history_raw) > 20:  # 10往復 = 20メッセージ
            history_raw = history_raw[-20:]
        request.session[session_key] = history_raw
        
        # AI会話の実績トラッキング（ユーザーがログインしている場合のみ）
        if acc:
            try:
                from codemon.achievement_utils import update_ai_chat_count
                update_ai_chat_count(acc)
            except Exception as e:
                print(f"[WARNING] Achievement tracking failed: {e}")

        return JsonResponse({'reply': ai_reply})
    except json.JSONDecodeError as e:
        print(f"[ERROR AI CHAT] JSON decode error: {e}")
        return JsonResponse({'error': f'invalid json: {str(e)}'}, status=400)
    except Exception as e:
        print(f"[ERROR AI CHAT] Exception: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
